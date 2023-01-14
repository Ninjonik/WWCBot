import random

import discord
from discord.ext import commands
from discord import app_commands

import presets


class assign_roles_to_all(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="roles-all")
    async def assign_roles_to_all(self, interaction: discord.Interaction, role: discord.Role):
        member = interaction.user
        userName = f"{member.name}#{member.discriminator}"
        if presets.check_perm(userName):
            for member in interaction.guild.members:
                await member.add_roles(role)
            await interaction.response.send_message(content="Command successfully executed!", ephemeral=True)
        else:
            await interaction.response.send_message(content="Not enough permissions for this command!", ephemeral=True)



async def setup(client: commands.Bot) -> None:
    await client.add_cog(assign_roles_to_all(client))
