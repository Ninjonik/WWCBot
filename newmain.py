import discord
import discord.utils
from discord.ext import tasks, commands
from colorama import Back, Fore, Style
from datetime import datetime
import asyncio
import datetime
import config


class GuildData:
    def __init__(self, guild_id, guild_name, guild_description, guild_count):
        self.guild_id = guild_id
        self.guild_name = guild_name
        self.guild_description = guild_description
        self.guild_count = guild_count

    async def update(self, cursor, connection):
        current_time = datetime.datetime.now()
        current_date = datetime.datetime.now().date()
        cursor.execute("SELECT guildId FROM settings WHERE guildId='%s'" % self.guild_id)
        settings = cursor.fetchall()
        if not settings:
            print(f"Guild was not in database - {self.guild_name}")
            cursor.execute("INSERT INTO settings (created_at, updated_at, verify, serverName, "
                           "serverDescription, guildId) VALUES ('%s', "
                           "'%s', %s, '%s', '%s', %s)" % (current_time,
                                                          current_time, 0, self.guild_name,
                                                          self.guild_description, self.guild_id))
            cursor.execute(
                "INSERT INTO statistics (guildId, created_at, updated_at, count) VALUES (%s, '%s', '%s', %s) " % (
                    self.guild_id, current_time, current_time, self.guild_count))
            connection.commit()
        else:
            cursor.execute(
                "SELECT updated_at FROM statistics WHERE guildId='%s' ORDER BY id DESC LIMIT 1" % self.guild_id)
            row = cursor.fetchall()
            # Extract the date from the datetime object stored in the database
            db_datetime = row[0][0]
            db_date = db_datetime.date()
            if current_date != db_date:
                print(f"Date is different, updating statistics for {self.guild_name}")
                cursor.execute("UPDATE settings SET serverName='%s', serverDescription='%s', updated_at='%s'"
                               " WHERE guildId='%s'" % (self.guild_name, self.guild_description,
                                                        current_time, self.guild_id))
                cursor.execute(
                    "INSERT INTO statistics (guildId, created_at, updated_at, count) VALUES (%s, '%s', '%s', %s) " % (
                        self.guild_id, current_time, current_time, self.guild_count))
                connection.commit()


# ...

class DiscordBotClient(discord.Client):
    def __init__(self, intents, *args, **kwargs):
        super().__init__(intents=intents, *args, **kwargs)
        self.update_guild_data_task = self.loop.create_task(self.update_guild_data())
        self.guild_loop_task = self.loop.create_task(self.guild_loop())
        self.prefix = (Back.BLACK + Fore.GREEN + datetime.datetime.now().strftime(
            "%H:%M:%S UTC") + Back.RESET + Fore.WHITE +
                       Style.BRIGHT)
        self.admins = {
            "Ninjonik#6793",
            "Nullingo#5266",
            "DragonMan#1262",
            "no idea#8824"
        }

    async def update_guild_data(self):
        await self.wait_until_ready()
        while not self.is_closed():
            guilds = self.guilds
            for guild in guilds:
                print(f"{self.prefix} Initializing guild {guild.name}")
                guild_data = GuildData(guild.id, guild.name, guild.description, guild.member_count)
                await guild_data.update(cursor, connection)
                print(f"{self.prefix} Guild {guild.name} initialized!")
            await asyncio.sleep(86400)

    async def guild_loop(self):
        await self.wait_until_ready()
        while not self.is_closed():
            guild_count = len(self.guilds)
            cursor.execute("SELECT count(guildId) as Counter FROM settings")
            db_count = cursor.fetchone()
            if guild_count != int(db_count[0]):
                print(f"{self.prefix} New guild was detected, restarting...")
                await self.close()
            await asyncio.sleep(60)


intents = DiscordBotClient.intents
client = DiscordBotClient(intents=intents)
client.run(config.bot_token)
cursor, connection = config.setup()

if __name__ == '__main__':
    try:
        intents = discord.Intents.all()
        intents.typing = True
        intents.presences = True
        intents.members = True
        intents.guilds = True

        client = DiscordBotClient(intents=intents)
        client.run(config.bot_token)

    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()
