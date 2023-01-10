import asyncio
import random
import discord
from discord.ext import commands
from discord import app_commands


class randomcog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="random")
    async def choose(self, interaction: discord.Interaction, args: str):
        arguments = args.split(" ")  # this that this -> 1) this 2)that 3)this
        choice = random.choice(arguments)
        thinking = await interaction.channel.send(":clock1: Thinking...")
        for i in range(4):
            await thinking.edit(content=f":clock{i + 1}: Thinking...")
            await asyncio.sleep(0.15)
        await interaction.response.send_message(choice)
        await thinking.delete()


async def setup(client: commands.Bot) -> None:
    await client.add_cog(randomcog(client))
