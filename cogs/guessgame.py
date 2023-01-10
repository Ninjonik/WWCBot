import random
import discord
from discord.ext import commands
from discord import app_commands


class guessgame(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="guess")
    async def guess(self, interaction: discord.Interaction, maximum: int = 10):
        number = random.randint(1, maximum)
        tries = int(round(maximum / 2 + maximum / 3, 0))
        tries_max = tries

        await interaction.response.send_message(
            f"Guessing game has started!\nPlease guess a number  **1-{maximum}**\nNumber of tries left: {tries}")

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        while tries > 0:
            guessnum = await self.client.wait_for('message', check=check)
            try:
                int(guessnum.content)
            except:
                print("Invalid expression")
                continue
            tries = tries - 1
            if int(guessnum.content) == number:
                await interaction.channel.send(f"You have guessed correctly, it has taken you {tries_max} tries.")
            elif int(guessnum.content) > number:
                await interaction.channel.send(
                    f"Incorrect, number is too high, try again! Number of tries left: {tries}")
            elif int(guessnum.content) <= 0:
                await interaction.channel.send(
                    f"Incorrect, number is too low, try again! Number of tries left: {tries}")
            else:
                await interaction.channel.send(f"Incorrect, try again! Number of tries left: {tries}")
            print("Carrying on")
        else:
            await interaction.channel.send(f"Game lost, you've run out of tries. The Number was: {number}")


async def setup(client: commands.Bot) -> None:
    await client.add_cog(guessgame(client))
