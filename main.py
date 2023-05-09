import random

import discord
import discord.utils
from discord.ext import tasks, commands
from colorama import Fore
from datetime import datetime
import platform
import asyncio
import datetime
import config
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


@tasks.loop(hours=6)
async def update_guild_data(guilds):
    for guild in guilds:
        print(f"{presets.prefix()} Initializing guild {guild.name}")
        await on_start(guild.name, guild.description, guild.id, guild.member_count)
        print(f"{presets.prefix()} Guild {guild.name} initialized!")


@tasks.loop(seconds=1800)
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
                         "cogs.assembly", "cogs.clear", "cogs.assign_roles_to_all", "cogs.assembly_info",
                         "cogs.assembly_suggest"]

    @tasks.loop(seconds=1400)
    async def refreshConnection(self):
        print(presets.prefix() + " Refreshing DB Connection")
        self.cursor, self.connection = config.setup()
        if self.connection.is_connected():
            db_Info = self.connection.get_server_info()
            print(presets.prefix() + " Connected to MySQL Server version ", db_Info)

    async def setup_hook(self):
        for ext in self.cogsList:
            await self.load_extension(ext)

    async def on_ready(self):
        await self.refreshConnection()
        print(presets.prefix() + " Logged in as " + Fore.YELLOW + self.user.name)
        print(presets.prefix() + " Bot ID " + Fore.YELLOW + str(self.user.id))
        print(presets.prefix() + " Discord Version " + Fore.YELLOW + discord.__version__)
        print(presets.prefix() + " Python version " + Fore.YELLOW + platform.python_version())
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
        valid_greetings = {"hi", "hello", "sup", "hi!", "hello!", "sup!", "hello everyone", "hello everyone!"}
        valid_hrus = {"hru?", "hru", "how are you?", "how are you", "how have you been?", "how have you been"}

        now = datetime.datetime.utcnow()
        if message.content.lower() in valid_greetings and now-datetime.timedelta(hours=72) <= message.author.joined_at <= now:
            rules_channel = message.guild.rules_channel
            embed = discord.Embed(
                title=f"Hello, {message.author.name}!",
                description=f"Welcome to WWC's Discord, {message.author.mention}! "
                            f"We're glad to have you here. Please take a moment to read our rules in "
                            f"{rules_channel.mention}. "
                            f"If you have any questions, don't hesitate to ask in the appropriate channel. Enjoy your "
                            f"stay!",
                color=0x00ff00
            )
            await message.channel.send(embed=embed)

        elif message.content.lower() in valid_hrus:
            responses = [
                "Thanks! I'm fine! How are you?",
                "Great, thank you. How are you?",
                "Good, thanks, and you?",
                "Fine, thanks. How are you?",
                "I’m doing well.",
                "I’m fine, maybe a little tired. I need some more coffee. ☕",
                "Good, thanks.",
                "Not bad, thanks. How about you?",
                "I'm doing alright. How about you?",
                "Can't complain, thanks. How are you?",
                "I'm doing well, thank you. How about you?",
                "I'm doing great, thanks. How are you?"
            ]
            await message.channel.send(random.choice(responses))

    async def on_message_edit(self, before, after):
        await self.check_toxicity(after)

    async def check_toxicity(self, message):
        self.cursor, self.connection = config.setup()
        toxicityValue = 0
        if message.author != client.user and message.content:
            message.content = (message.content[:75] + '..') if len(message.content) > 75 else message.content
            member = message.author
            analyze_request = {
                'comment': {'text': message.content},
                'requestedAttributes': {'TOXICITY': {}}
            }
            try:
                response = presets.perspective.comments().analyze(body=analyze_request).execute()
                toxicityValue = (response["attributeScores"]["TOXICITY"]["summaryScore"]["value"])
                current_time = datetime.datetime.now()
                query = "INSERT INTO wwcbot_filter_logs (guildId, created_at, updated_at, message, authorId, result) " \
                        "VALUES (%s, %s, %s, %s, %s, %s)"
                values = (
                    message.guild.id, current_time, current_time, message.content, message.author.id, toxicityValue)
                self.cursor.execute(query, values)
                if toxicityValue >= 0.60:
                    await message.delete()
                    if toxicityValue < 0.75:
                        punishment = "Original message has been deleted."
                    elif 0.75 <= toxicityValue < 0.9:
                        punishment = "Original message has been deleted. You have been timed-outed for 5 minutes."
                        timeMessage = datetime.datetime.now().astimezone() + datetime.timedelta(minutes=5)
                        await member.timeout(timeMessage, reason=f"Inappropriate message with value {toxicityValue}")
                    elif 0.9 <= toxicityValue < 0.95:
                        punishment = "Original message has been deleted. You have been timed-outed for 15 minutes."
                        timeMessage = datetime.datetime.now().astimezone() + datetime.timedelta(minutes=15)
                        await member.timeout(timeMessage, reason=f"Inappropriate message with value {toxicityValue}")
                    else:
                        punishment = "Original message has been deleted. You have been kicked from the server. Please" \
                                     " refrain from such a toxicity if you dont want to face harsher consequences."
                        await member.kick(reason=f"Inappropriate message with value {toxicityValue}")

                    channel = await member.create_dm()
                    embed = discord.Embed(title="You have been auto-moderated",
                                          description="One of your messages has been flagged as inappropriate which has"
                                                      " resulted in the following punishment(s):",
                                          color=0xe01b24)
                    embed.set_author(name="WWCBot")
                    embed.add_field(name="Message Content:", value=message.content, inline=True)
                    embed.set_footer(text="If you feel that this punishment is a mistake / inappropriate then"
                                          " please contact WWC Staff.")
                    embed.add_field(name="Punishment:", value=punishment, inline=True)
                    await channel.send(embed=embed)
                    for channel in member.guild.text_channels:
                        if channel.name == 'automod-logs':
                            embed.add_field(name="Time", value=datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                                            inline=True)
                            embed.add_field(name="User:", value=member, inline=True)
                            embed.add_field(name="Punishment:", value=punishment, inline=True)
                            embed.add_field(name="Toxicity Value:", value=toxicityValue)
                            embed.set_footer(text="This message was sent to the user. Consider "
                                                  "taking more actions if needed.")
                            await channel.send(embed=embed)
                else:
                    channel = message.channel
                    # await channel.send(f"Toxicity value: {toxicityValue}")
            except Exception as e:
                embed = discord.Embed(title="Auto-Moderation Error",
                                      description="WWCBot has been unable to moderate this message.",
                                      color=0xff8000)
                embed.add_field(name="Error", value=e, inline=True)
                embed.add_field(name="Message", value=message.content, inline=True)
                embed.add_field(name="Time", value=datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"), inline=True)
                embed.set_author(name="WWCBot")
                for channel in member.guild.text_channels:
                    if channel.name == 'automod-logs':
                        embed.add_field(name="User:", value=member, inline=True)
                        embed.add_field(name="Value of toxicity:", value=toxicityValue, inline=True)
                        await channel.send(embed=embed)

    async def on_raw_reaction_add(self, payload):
        self.cursor, self.connection = config.setup()
        guild = client.get_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)
        channel = await guild.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        role = discord.utils.get(guild.roles, name="Assembly Leader")

        print(member, message, role, guild)
        if not member.bot and role in member.roles and payload.emoji.name == "🔒":
            current_time = datetime.datetime.now()
            approvals = discord.utils.get(message.reactions, emoji="✅")
            denials = discord.utils.get(message.reactions, emoji="❎")
            count_sum = approvals.count - denials.count
            self.cursor.execute("UPDATE assembly_suggestions SET votes=%s, updated_at='%s' "
                                "WHERE message_id=%s" % (count_sum, current_time, payload.message_id))
            self.connection.commit()
            embed = discord.Embed(title="Suggestion closed!", color=0xff0000)
            embed.add_field(name="Closed!",
                            value=f"Suggestion #{message.id} has been 🔒 closed by the Assembly Leader {member.mention}",
                            inline=True)
            embed.add_field(name="Voting Result!", value=f"\nVotes result: **{approvals.count}** - **{denials.count}**",
                            inline=True)
            await channel.send(embed=embed)
            await message.clear_reactions()
            await message.add_reaction("🔓")
        elif not member.bot and role in member.roles and payload.emoji.name == "🔓":
            await message.clear_reactions()
            await message.add_reaction('✅')
            await message.add_reaction('❎')
            await message.add_reaction('🔒')
            embed = discord.Embed(title="Suggestion re-opened!", color=0x00ff00)
            embed.add_field(name="Re-Opened!",
                            value=f"Suggestion #{message.id} has been 🔓 re-opened by the Assembly Leader"
                                  f" {member.mention}\nYou can now vote again on this suggestion!")
            await channel.send(embed=embed)

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
