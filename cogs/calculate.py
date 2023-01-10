import discord
from discord.ext import commands
from discord import app_commands
import datetime


class calculate(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="calculate", description="Calculates given expression.")
    async def calculate(self, interaction: discord.Interaction, expression: str):
        symbols = ['+', '-', '*', '/', '**', '//', '%']
        if any(s in expression for s in symbols):
            calculated = eval(expression)
            embed = discord.Embed(title="Calculator", description=f"Expression {expression}\n "
                                                                  f"Answer {calculated}", color=discord.Colour.green(),
                                  timestamp=datetime.datetime.utcnow())
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Wrong math expression.")


async def setup(client: commands.Bot) -> None:
    await client.add_cog(calculate(client))
