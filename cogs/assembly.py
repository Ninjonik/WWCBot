import discord
import discord.utils
from discord.ext import tasks, commands
from discord import app_commands
import presets


class assembly(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="assembly", description="Become Assembly Member or learn about Assembly!")
    async def assembly(self, interaction: discord.Interaction):
        member = interaction.user
        embed = discord.Embed(
            title=f"**Assembly**",
            description="**The Assembly** is a group of members who have the right to vote on proposed changes to the "
                        "World War Community server. These changes are put forward by the Assembly Leader, "
                        "who is also responsible for guiding the direction of the Assembly and the server. Assembly "
                        "Members also have the ability to suggest new changes to the Assembly Leader for future "
                        "consideration.",
            colour=discord.Colour.green()
        )
        embed.set_thumbnail(url=member.guild.icon)
        embed.add_field(
            name="**Become Assembly Member**",
            value='Click on the "Assembly Member" button in order to become an Assembly Member yourself!',
            inline=True,
        )
        embed.add_field(
            name="What is Assembly?",
            value='Click on the "Assembly" button to check what is Assembly about and what it can do!',
            inline=True,
        )

        await interaction.response.send_message(content=f"{member.mention}", embed=embed,
                                                view=presets.AssemblyDialog(self.client))


async def setup(client: commands.Bot) -> None:
    await client.add_cog(assembly(client))
