import discord
import discord.utils
from discord.ext import tasks, commands
from discord import app_commands
import config
import presets

class verify(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="verify", description="Resends the verify message.")
    async def verify(self, interaction: discord.Interaction):
        member = interaction.user
        embed = discord.Embed(
            title=f"Welcome to **WWC**, {member.name}#{member.discriminator}",
            description="**World War Community** is a 20th Century oriented community that allows its members to "
                        "explore and discuss various events and actions that took place during the 20th century. "
                        "We focus on providing safe and friendly space for war related discussions, hosting tons "
                        "of events and game-nights every week, and developing our own WW2 Roblox games where "
                        "everyone can learn about historic events while also having fun.",
            colour=discord.Colour.green()
        )
        embed.set_thumbnail(url=member.guild.icon)
        if config.hoi:
            embed.add_field(
                name='**HOI4 Role**', value='If you came to the server to take part in one of our HOI4 games, '
                                            'click on '
                                            'the "HOI4" button to get access to HOI4 Category.',
                inline=False,
            )
        embed.add_field(
            name="**General Access**",
            value='Click on the "Verify" button in order to start the interactive verification process '
                  'which will grant you access to the majority of the server.',
            inline=True,
        )
        embed.set_footer(
            text="Welcome to World War Community, make sure to follow verification instructions to get a full "
                 "access to the server. "
        )

        await interaction.response.send_message(content=f"{member.mention}", embed=embed,
                                                view=presets.EntryDialog(self.client))


async def setup(client: commands.Bot) -> None:
    await client.add_cog(verify(client))
