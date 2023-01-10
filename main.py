from asyncio import tasks
from time import sleep

import discord
import discord.utils
from discord.ext import tasks, commands
from colorama import Back, Fore, Style
from datetime import datetime
import platform
import os
import random
import asyncio
import json
import datetime
import string
from pprint import pprint
import config
from PIL import Image, ImageDraw, ImageFont
import mysql.connector
import time
import presets

intents = discord.Intents.all()
intents.typing = True
intents.presences = True
intents.members = True
intents.guilds = True

# Store the cursor object in a global variable
global cursor
global connection


async def on_start(server_name, server_description, guild_id, guild_count):
    # Establish database connection
    cursor, connection = config.setup()
    cursor.execute("SELECT guildId FROM settings WHERE guildId='%s'" % guild_id)
    settings = cursor.fetchall()
    current_time = datetime.datetime.now()
    current_date = datetime.datetime.now().date()
    if not settings:
        print(f"{presets.prefix()} Guild was not in database - {server_name}")
        cursor.execute("INSERT INTO settings (created_at, updated_at, verify, serverName, "
                       "serverDescription, guildId) VALUES ('%s', "
                       "'%s', %s, '%s', '%s', %s)" % (current_time,
                                                      current_time, 0, server_name,
                                                      server_description, guild_id))
        cursor.execute(
            "INSERT INTO statistics (guildId, created_at, updated_at, count) VALUES (%s, '%s', '%s', %s) " % (
                guild_id, current_time, current_time, guild_count))
        connection.commit()

    else:
        cursor.execute("SELECT updated_at FROM statistics WHERE guildId='%s' ORDER BY id DESC LIMIT 1" % guild_id)
        row = cursor.fetchall()
        # Extract the date from the datetime object stored in the database
        db_datetime = row[0][0]
        db_date = db_datetime.date()
        print(f" {presets.prefix()} Current date is: {current_date} meanwhile DB date is: {db_date}")
        if current_date != db_date:
            print(f"{presets.prefix()} Date is different, updating statistics for {server_name}")
            cursor.execute("UPDATE settings SET serverName='%s', serverDescription='%s', updated_at='%s'"
                           " WHERE guildId='%s'" % (server_name, server_description,
                                                    current_time, guild_id))
            cursor.execute(
                "INSERT INTO statistics (guildId, created_at, updated_at, count) VALUES (%s, '%s', '%s', %s) " % (
                    guild_id, current_time, current_time, guild_count))
            connection.commit()


@tasks.loop(hours=24)
async def update_guild_data(guilds):
    for guild in guilds:
        print(f"{presets.prefix()} Initializing guild {guild.name}")
        await on_start(guild.name, guild.description, guild.id, guild.member_count)
        print(f"{presets.prefix()} Guild {guild.name} initialized!")


@tasks.loop(seconds=60)
async def guildLoop():
    # Establish database connection
    cursor, connection = config.setup()
    guildCount = len(client.guilds)
    cursor.execute("SELECT count(guildId) as Counter FROM settings")
    dbCount = cursor.fetchone()
    if guildCount != int(dbCount[0]):
        print(presets.prefix() + " New guild was detected, restarting loop.")
        await update_guild_data(client.guilds)


@tasks.loop(seconds=30)
async def statusLoop():
    await client.wait_until_ready()
    await client.change_presence(status=discord.Status.idle,
                                 activity=discord.Activity(type=discord.ActivityType.watching,
                                                           name=f"{len(client.guilds)} servers. 🧐"))
    await asyncio.sleep(10)
    memberCount = 0
    for guild in client.guilds:
        memberCount += guild.member_count
    await client.change_presence(status=discord.Status.dnd,
                                 activity=discord.Activity(type=discord.ActivityType.listening,
                                                           name=f"{memberCount} people! 😀", ))
    await asyncio.sleep(10)

    await client.change_presence(status=discord.Status.online,
                                 activity=discord.Activity(type=discord.ActivityType.competing,
                                                           name=f"dsc.gg/wwc 🎖️",
                                                           url="https://discord.gg/dCVNQeywKY"))
    await asyncio.sleep(10)


class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('.'), intents=discord.Intents().all())
        self.cursor, self.connection = config.setup()
        self.cogsList = ["cogs.roles", "cogs.calculate", "cogs.whois", "cogs.dice", "cogs.randomcog", "cogs.guessgame",
                         "cogs.assembly", "cogs.verify", "cogs.clear"]

    async def setup_hook(self):
        for ext in self.cogsList:
            await self.load_extension(ext)

    async def on_ready(self):
        if self.connection.is_connected():
            db_Info = self.connection.get_server_info()
            print(presets.prefix() + " Connected to MySQL Server version ", db_Info)
        print(presets.prefix() + " Logged in as " + Fore.YELLOW + self.user.name)
        print(presets.prefix() + " Bot ID " + Fore.YELLOW + str(self.user.id))
        print(presets.prefix() + " Discord Version " + Fore.YELLOW + self.user.name)
        print(presets.prefix() + " Python version " + Fore.YELLOW + discord.__version__)
        print(presets.prefix() + " Syncing slash commands...")
        synced = await self.tree.sync()
        print(presets.prefix() + " Slash commands synced " + Fore.YELLOW + str(len(synced)) + " Commands")
        print(presets.prefix() + " Initializing guilds....")
        print(presets.prefix() + " Initializing status....")
        if not statusLoop.is_running():
            statusLoop.start()
        if not guildLoop.is_running():
            guildLoop.start(),
        if not update_guild_data.is_running():
            update_guild_data.start(self.guilds)

    async def on_message(self, message):
        await self.check_toxicity(message)

    async def on_message_edit(self, before, after):
        await self.check_toxicity(after)

    async def check_toxicity(self, message):
        if message.author != client.user and message.content:
            analyze_request = {
                'comment': {'text': message.content},
                'requestedAttributes': {'TOXICITY': {}}
            }
            try:
                response = presets.perspective.comments().analyze(body=analyze_request).execute()
                toxicityValue = (response["attributeScores"]["TOXICITY"]["summaryScore"]["value"])
                member = message.author
                current_time = datetime.datetime.now()
                self.cursor.execute(
                    "INSERT INTO wwcbot_filter_logs (guildId, created_at, updated_at, message, authorId, result) "
                    "VALUES (%s, '%s', '%s', '%s', %s, %s) " % (
                        message.guild.id, current_time, current_time,
                        message.content, message.author.id, toxicityValue))
                self.connection.commit()
                if toxicityValue >= 0.8:
                    channel = await member.create_dm()
                    await channel.send(f"Your message with following content:\n"
                                       f"{message.content}\n"
                                       f"has been auto-moderated and deleted.\n"
                                       f"Value of toxicity: {toxicityValue}")
                    print(f"{presets.prefix()} Message {message} has been deleted with {toxicityValue}.")
                    await message.delete()
                else:
                    channel = message.channel
                    # await channel.send(f"Toxicity value: {toxicityValue}")
            except:
                pass

    async def on_member_join(self, member):
        # await updateMemberCount(1, member.guild.id)
        for channel in member.guild.text_channels:
            if channel.name == '👋entry':
                embed = discord.Embed(
                    title=f"Welcome to **WWC**, {member.name}#{member.discriminator}",
                    description="**World War Community** is a 20th Century oriented community that allows its members "
                                "to "
                                "explore and discuss various events and actions that took place during the 20th "
                                "century. "
                                "We focus on providing safe and friendly space for war related discussions, hosting "
                                "tons "
                                "of events and game-nights every week, and developing our own WW2 Roblox games where "
                                "everyone can learn about historic events while also having fun.",
                    colour=discord.Colour.green()
                )
                embed.set_thumbnail(url=member.guild.icon)
                if config.hoi:
                    embed.add_field(
                        name='**HOI4 Role**', value='If you came to the server to participate in one of our HOI4 games,'
                                                    ' click on '
                                                    'the "HOI4" button to get access to HOI4 Category.',
                        inline=False,
                    )
                embed.add_field(
                    name="**General Access**",
                    value='Click on the "Verify" button in order to start the interactive verification process '
                          'which will grant you access to the majority of the server.',
                    inline=True,
                )
                embed.set_footer(
                    text="Welcome to World War Community, make sure to follow verification instructions to get a "
                         "full "
                         "access to the server. "
                )

                await channel.send(content=f"{member.mention}", embed=embed, view=presets.EntryDialog(client))


client = Client()

client.run(presets.token)
