import discord.utils
from discord.ext import tasks, commands
from discord import app_commands
import presets


class roles(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="roles", description="Customize your optional roles!")
    async def roles(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"Customization - **Roles**",
            description="You can unlock additional channels immediately by clicking on one of the buttons below.",
            colour=discord.Colour.blurple()
        )
        embed.set_thumbnail(url=interaction.guild.icon)
        embed.add_field(
            name='**War Discussion**',
            value="If you came to the server to discuss various historical content or you have "
                  "any questions about uniform/badge/... you've found -> it's the place for you.",
            inline=False,
        )
        embed.add_field(
            name="**Military Games**",
            value='If you came to the server to take part in a discussion or came to find other people '
                  'to play various Historical Games that took place in the 20th century, '
                  "then it's the place for you!",
            inline=True,
        )
        embed.add_field(
            name="**Roblox Access**",
            value='Click on this role if you want to stay updated on the brand new projects coming out '
                  'of our Roblox game studio and participate in our Roblox-oriented channels!',
            inline=True,
        )
        embed.set_footer(
            text="Click on Roles you want to Add/Remove."
        )

        await interaction.response.send_message(content="Now please click on roles you want to get / remove.",
                                       embed=embed,
                                       view=presets.UpdateRoles())


async def setup(client: commands.Bot) -> None:
    await client.add_cog(roles(client))
