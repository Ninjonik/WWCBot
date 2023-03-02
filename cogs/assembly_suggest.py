import discord
from discord.ext import commands
from discord import app_commands
import datetime

import config


class assembly_suggest(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.cursor, self.connection = config.setup()

    @app_commands.command(name='assembly_suggest', description="Creates an Assembly Suggestion for Assembly Members "
                                                               "to vote!")
    async def assembly_suggest(self, interaction: discord.Interaction, title: str, description: str):
        self.cursor, self.connection = config.setup()
        self.cursor.execute("SELECT discord_id FROM assemblies WHERE discord_id='%s'" % interaction.user.id)
        assembly = self.cursor.fetchall()
        current_time = datetime.datetime.now()
        if assembly:
            await interaction.response.send_message("Suggestion successfully created!")
            embed = discord.Embed(title=title, description=description, color=0xb3ffb3)
            embed.set_author(name=f"{interaction.user.name}#{interaction.user.discriminator}",
                             icon_url=interaction.user.avatar)
            channel = interaction.guild.get_channel(1078247137646760016)
            message = await channel.send(embed=embed)
            await message.add_reaction('✅')
            await message.add_reaction('❎')
            await message.add_reaction('🔒')
            current_time = datetime.datetime.now()
            self.cursor.execute(
                "INSERT INTO assembly_suggestions (message_id, author_discord_id, title, description, "
                "created_at, updated_at) "
                "VALUES (%s, %s, '%s', '%s', '%s', '%s') " % (
                    message.id, interaction.user.id, title, description, current_time, current_time))
            self.connection.commit()
        else:
            await interaction.response.send_message("You are not an Assembly Member!")


async def setup(client: commands.Bot) -> None:
    await client.add_cog(assembly_suggest(client))
