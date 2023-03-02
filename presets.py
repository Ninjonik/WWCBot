from asyncio import tasks
from time import sleep

import discord
import discord.utils
from discord.ext import tasks, commands
from discord import app_commands
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
from googleapiclient import discovery


def prefix():
    return (Back.BLACK + Fore.GREEN + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S") + Back.RESET + Fore.WHITE +
            Style.BRIGHT)


token = config.bot_token

admins = {
    "Ninjonik#6793",
    "Nullingo#5266",
    "DragonMan#1262",
    "no idea#8824"
}

perspective = discovery.build(
    "commentanalyzer",
    "v1alpha1",
    developerKey=config.API_KEY,
    discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
    static_discovery=False,
)


async def ban(member, reason):
    await member.ban(reason=reason)


async def kick(member):
    await member.kick()


def check_perm(member):
    if member in admins:
        return True
    else:
        return False


def log(content):
    print(prefix() + content)


async def _add_player(player_id, rating_percentage, current_time):
    cursor, connection = config.setup()
    try:
        cursor.execute(
            "INSERT INTO players (discord_id, rating, created_at, updated_at) VALUES (%s, %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE rating = %s, updated_at = %s",
            (player_id, rating_percentage, current_time, current_time, rating_percentage, current_time))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e


class UpdateRoles(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="War Discussion Access", style=discord.ButtonStyle.success, custom_id="ur_war_discussion",
                       emoji="📜")
    async def war_discussion(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name="War Discussion Access")
        if role in interaction.user.roles:
            await interaction.user.remove_roles(discord.utils.get(interaction.user.guild.roles,
                                                                  name="War Discussion Access"))
        else:
            await interaction.user.add_roles(discord.utils.get(interaction.user.guild.roles,
                                                               name="War Discussion Access"))

        msg = await interaction.response.send_message("Your roles have been updated.", ephemeral=True)

    @discord.ui.button(label="Military Games Access", style=discord.ButtonStyle.danger, custom_id="ur_military_games",
                       emoji="🎮")
    async def military_games(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name="Military Games Access")
        if role in interaction.user.roles:
            await interaction.user.remove_roles(discord.utils.get(interaction.user.guild.roles,
                                                                  name="Military Games Access"))
        else:
            await interaction.user.add_roles(discord.utils.get(interaction.user.guild.roles,
                                                               name="Military Games Access"))
        msg = await interaction.response.send_message("Your roles have been updated.", ephemeral=True)

    @discord.ui.button(label="Roblox Access", style=discord.ButtonStyle.secondary, custom_id="ur_roblox",
                       emoji="✨")
    async def roblox(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name="Roblox Access")
        if role in interaction.user.roles:
            await interaction.user.remove_roles(discord.utils.get(interaction.user.guild.roles,
                                                                  name="Roblox Access"))
        else:
            await interaction.user.add_roles(discord.utils.get(interaction.user.guild.roles,
                                                               name="Roblox Access"))

        msg = await interaction.response.send_message("Your roles have been updated.", ephemeral=True)

    @discord.ui.button(label="HOI4 Role", style=discord.ButtonStyle.primary, custom_id="ur_hoi4", emoji="🎖️")
    async def hoi4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.user.add_roles(discord.utils.get(interaction.user.guild.roles, name="HOI4 Access"))
        msg = await interaction.response.send_message("Your roles have been updated.", ephemeral=True)


class EntryDialog(discord.ui.View):
    def __init__(self, client):
        super().__init__(timeout=None)
        self.client = client

    if config.hoi:
        @discord.ui.button(label="HOI4 Role", style=discord.ButtonStyle.success, custom_id="ed_hoi4", emoji="🎖️")
        async def hoi4(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.user.add_roles(discord.utils.get(interaction.user.guild.roles, name="HOI4 Access"))
            msg = await interaction.response.send_message("Your roles have been updated.", ephemeral=True)

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.primary, custom_id="ed_verify", emoji="✅")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name="Verified")
        if role not in interaction.user.roles:
            member = interaction.user
            await interaction.response.send_message("Generating image...")
            await interaction.channel.send("Please enter the following code: (you have 3 tries left)")

            log(f" User {interaction.user.name}#{interaction.user.discriminator} has started a verification process.")

            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel

            characters = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNOPQRSTUVWXYZ0123456789"
            key = ''.join(random.choice(characters) for i in range(8))

            filename = f'keys/{key}.png'
            text = key
            size = 180
            fnt = ImageFont.truetype('arial.ttf', size)
            # create image
            image = Image.new(mode="RGB", size=(int(size / 1.4) * len(text), size + 60), color="black")
            draw = ImageDraw.Draw(image)
            # draw text
            draw.text((10, 10), text, font=fnt, fill=(255, 255, 0), color="white")
            # save file
            image.save(filename)
            await interaction.channel.send(file=discord.File(filename))

            tries = 3

            while tries > 0:
                user_key = await self.client.wait_for('message', check=check)
                if user_key.content == key:
                    log(f" User {member.name}#{member.discriminator} "
                        f"has successfully solved the captcha with {tries} tries left.")

                    await interaction.channel.send(content=f"You have solved the verification, "
                                                           f"{interaction.user.mention}. ")
                    await member.add_roles(discord.utils.get(member.guild.roles, name="Verified"))
                    os.remove(filename)
                    break
                else:
                    tries = tries - 1
                    await interaction.channel.send(f"Incorrect, you have {tries} tries left.")
                    log(f" User {member.name}#{member.discriminator} has failed captcha with "
                        f"{tries} left, generated key was {key} and they entered {user_key.content}")
                    continue
            if tries == 0:
                os.remove(filename)
                log(f" User {member.name}#{member.discriminator} "
                    f"has been kicked from the server for not completing the captcha.")
                await kick(member)

class AssemblyDialog(discord.ui.View):
    def __init__(self, client):
        super().__init__(timeout=None)
        self.cursor, self.connection = config.setup()

    @discord.ui.button(label="Assembly Member", style=discord.ButtonStyle.blurple,
                       custom_id="as_assembly_member", emoji="📋")
    async def assembly_member(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.cursor, self.connection = config.setup()
        self.cursor.execute("SELECT discord_id FROM assemblies WHERE discord_id='%s'" % interaction.user.id)
        assembly = self.cursor.fetchall()
        current_time = datetime.datetime.now()
        if not assembly:
            print(f"{prefix()} User was not in DB - {interaction.user.name}")
            self.cursor.execute("INSERT INTO assemblies (discord_id, created_at, updated_at) "
                                "VALUES (%s, '%s', '%s')"
                                % (interaction.user.id, current_time, current_time))
            self.connection.commit()
            await interaction.user.add_roles(
                discord.utils.get(interaction.user.guild.roles, name="Assembly Member"))
        else:
            print(f"{prefix()} Removing User from Assembly - {interaction.user.name}")
            self.cursor.execute("DELETE FROM assembly_suggestions WHERE author_discord_id=%s"
                                % interaction.user.id)
            self.cursor.execute("DELETE FROM assemblies WHERE discord_id=%s"
                                % interaction.user.id)
            self.connection.commit()
            await interaction.user.remove_roles(
                discord.utils.get(interaction.user.guild.roles, name="Assembly Member"))
        await interaction.response.send_message("Your roles have been updated.", ephemeral=True)

    @discord.ui.button(label="Assembly", style=discord.ButtonStyle.danger, custom_id="as_assembly", emoji="📚")
    async def assembly(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("https://docs.google.com/document/d/19eV4b-V6LIG1m2_pXdD_txJb"
                                                "RaCzrMOsxy3GI1CCR5U/edit?usp=sharing")
