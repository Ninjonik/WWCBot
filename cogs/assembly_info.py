import discord
import discord.utils
from discord.ext import tasks, commands
from discord import app_commands

import config


class assembly_info(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.cursor, self.connection = config.setup()

    @app_commands.command(name="assembly_info", description="Who is in our current assembly?")
    async def assembly_info(self, interaction: discord.Interaction):
        self.cursor, self.connection = config.setup()
        self.cursor.execute("SELECT * FROM assemblies")
        assembly = self.cursor.fetchall()
        assembly_members = []
        assembly_leader = "None"
        for member in assembly:
            val = interaction.guild.get_member(member[1]).mention
            if member[2] == 1:
                assembly_leader = val
            assembly_members.append(val)

        embed = discord.Embed(
            title=f"**Assembly**",
            description="**The Assembly** is a group of members who have the right to vote on proposed changes to the "
                        "World War Community server. These changes are put forward by the Assembly Leader, "
                        "who is also responsible for guiding the direction of the Assembly and the server. Assembly "
                        "Members also have the ability to suggest new changes to the Assembly Leader for future "
                        "consideration. Become Assembly Member by running /assembly command!",
            colour=discord.Colour.green()
        )
        embed.set_thumbnail(url=interaction.guild.icon)
        embed.add_field(
            name="**Current Assembly Leader**",
            value=assembly_leader,
            inline=True,
        )
        embed.add_field(
            name="Current Assembly Members",
            value=", ".join(assembly_members),
            inline=True,
        )

        await interaction.response.send_message(embed=embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(assembly_info(client))
