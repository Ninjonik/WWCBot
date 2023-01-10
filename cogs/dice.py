import random

import discord
from discord.ext import commands
from discord import app_commands


class dice(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="dice")
    async def roll(self, interaction: discord.Interaction, minimum: int = 1, maximum: int = 6):
        number = random.randint(minimum, maximum)
        await interaction.response.send_message(number)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(dice(client))
