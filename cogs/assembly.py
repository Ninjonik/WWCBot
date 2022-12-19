import discord
from discord.ext import commands
from discord import app_commands


class assembly(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="assembly", description="Sends hello!")
    async def cog1(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="Hello!")


async def setup(client: commands.Bot) -> None:
    await client.add_cog(assembly(client))
