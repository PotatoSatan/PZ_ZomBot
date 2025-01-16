import discord
from discord.ext import tasks, commands
from utils import execute_rcon_command, MAX_PLAYERS


class ServerStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()
        self.update_server_status.start()

    def cog_unload(self):
        self.update_server_status.cancel()

    @tasks.loop(minutes=5)
    async def update_server_status(self):
        """Update the bot's status every 5 minutes."""
        try:
            response = execute_rcon_command("players")

            if "Players connected" in response:
                player_count = response.split("(")[1].split(")")[0].strip()
                status_message = f"{player_count} survivors"
            else:
                status_message = "0 survivors"

            activity = discord.Activity(type=discord.ActivityType.watching, name=status_message)
            await self.bot.change_presence(activity=activity)
            print(f"Status updated to: Watching {status_message}")
        except Exception as e:
            print(f"Failed to update status: {e}")

    @update_server_status.before_loop
    async def before_update_server_status(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(ServerStatus(bot))