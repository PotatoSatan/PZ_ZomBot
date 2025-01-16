import discord
from discord import app_commands
import subprocess
import asyncio
from utils import execute_rcon_command, create_embed, tail_log_for_mod_update
from config import LUA_FILE

class BotCommands(discord.ext.commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="players", description="List all players on the server.")
    async def players(self, interaction: discord.Interaction):
        await interaction.response.defer()
        response = execute_rcon_command('players', max_retries=3, timeout=3)
        if "Players connected" in response:
            embed = create_embed("Current Players", response)
        elif "Error" in response:
            embed = create_embed("Error", response, color=discord.Color.red())
        else:
            embed = create_embed("No Response",
                                 "Server responded but no player information received. Please try again.",
                                 color=discord.Color.yellow())

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="server_status", description="Check if the server is active.")
    async def server_status(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        try:
            execute_rcon_command("players")
            embed = create_embed("Server Status", "The server is **active** and responding.", discord.Color.green())
        except Exception:
            embed = create_embed("Server Status", "The server is **offline** or not responding.", discord.Color.red())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="start_server", description="Start the Project Zomboid server.")
    async def start_server(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        try:
            command = 'tmux new-session -d -s proj_z "sh /opt/pzserver/start-server.sh"'
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                embed = create_embed("Server Control", "The server has been started.", discord.Color.green())
            else:
                embed = create_embed(
                    "Server Control",
                    f"Failed to start the server:\n{result.stderr.decode()}",
                    discord.Color.red()
                )
        except Exception as e:
            embed = create_embed("Server Control", f"Error: {e}", discord.Color.red())

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="stop_server", description="Stop the Project Zomboid server.")
    async def stop_server(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        try:
            command = 'tmux send-keys -t proj_z "quit" C-m && tmux kill-session -t proj_z'
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                embed = create_embed("Server Control", "The server has been stopped.", discord.Color.green())
            else:
                embed = create_embed(
                    "Server Control",
                    f"Failed to stop the server:\n{result.stderr.decode()}",
                    discord.Color.red()
                )
        except Exception as e:
            embed = create_embed("Server Control", f"Error: {e}", discord.Color.red())

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="restart_server", description="Restart the Project Zomboid server.")
    async def restart_server(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            followup_message = await interaction.followup.send("Restarting the server. This will take up to 5 minutes...")
            await asyncio.sleep(10)
            await interaction.followup.send("Alerting everyone in game...")

            command = '/opt/pzserver/restart-server.sh'
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                embed = create_embed("Server Control", "The server has been restarted successfully.", discord.Color.green())
            else:
                embed = create_embed(
                    "Server Control",
                    f"Failed to restart the server:\n{stderr.decode()}",
                    discord.Color.red()
                )
        except Exception as e:
            embed = create_embed("Server Control", f"Error: {e}", discord.Color.red())

        await followup_message.edit(embed=embed)

    @app_commands.command(name="kick", description="Kick a player from the server.")
    async def kick(self, interaction: discord.Interaction, player: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        response = execute_rcon_command(f'kick "{player}"')
        embed = create_embed("Kick Player", response)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="broadcast", description="Broadcast a message to the server.")
    async def broadcast(self, interaction: discord.Interaction, message: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        response = execute_rcon_command(f'servermsg "{message}"')
        embed = create_embed("Broadcast", f"Message broadcasted: {message}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="update_mods", description="Update mods")
    async def update_mods(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        response = execute_rcon_command("checkModsNeedUpdate")
        embed = create_embed("Server Mods", response)
        await interaction.response.send_message(embed=embed)

        result = tail_log_for_mod_update()
        embed = discord.Embed(
            title="Mod Update Check Results",
            description=result,
            color=discord.Color.green() if "Completed" in result else discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="reload_lua", description="Use /help to display list of lua files")
    async def reload_lua(self, interaction: discord.Interaction, lua: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        response = execute_rcon_command(f'reloadlua "{LUA_FILE}{lua}"')
        embed = create_embed("Lua Reloaded", response)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="changeoption", description="Change a server option.")
    async def change_option(self, interaction: discord.Interaction, option_name: str, new_value: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        response = execute_rcon_command(f'changeoption "{option_name}" "{new_value}"')
        embed = create_embed(f'Updated value for "{option_name}" to "{new_value}"', response)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="reload_options", description="Reload server options (ServerOptions.ini) and send to clients.")
    async def reload_options(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        response = execute_rcon_command("reloadoptions")
        embed = create_embed("Server Options Reloaded", response)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="save", description="Save world.")
    async def save(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        response = execute_rcon_command("save")
        embed = create_embed("World saved", response)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="Displays help and lua filenames for reload")
    async def help(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        description = (
            "List below are lua files that can be used to reload on the server:\n"
            "- servertest_SandboxVars.lua\n"
            "- servertest_spawnpoints.lua\n"
            "- servertest_spawnregions.lua"
        )
        embed = create_embed("Help: Lua Files for Reload", description)
        await interaction.response.send_message(embed=embed)