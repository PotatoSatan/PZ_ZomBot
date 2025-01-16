import discord
from discord.ext import commands
import asyncio
from config import DISCORD_TOKEN
from bot_commands import BotCommands
from server_status import ServerStatus

# Bot Setup
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    # Load cogs first
    await setup()
    # Then sync commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

async def setup():
    await bot.add_cog(BotCommands(bot))
    await bot.add_cog(ServerStatus(bot))

# Run the bot
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)