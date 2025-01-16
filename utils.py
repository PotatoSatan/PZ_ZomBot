import os
import time
from mcrcon import MCRcon
import discord
from config import RCON_HOST, RCON_PORT, RCON_PASSWORD, SERVER_DIR, LOG_FILE_PATH
import asyncio
from datetime import datetime, timedelta


def get_max_players_from_ini(directory):
    try:
        for filename in os.listdir(directory):
            if filename.endswith(".ini"):
                file_path = os.path.join(directory, filename)
                with open(file_path, "r") as file:
                    for line in file:
                        if line.startswith("MaxPlayers="):
                            return int(line.split("=")[1].strip())
    except Exception as e:
        print(f"Error reading max players from .ini files: {e}")
    return None


async def tail_log_for_mod_update(timeout=30, num_lines=5):  # timeout in seconds, num_lines is how many lines to check
    start_time = datetime.now()

    try:
        with open(LOG_FILE_PATH, "r") as log_file:
            log_file.seek(0, os.SEEK_END)

            file_position = log_file.tell()

            while (datetime.now() - start_time) < timedelta(seconds=timeout):
                log_file.seek(file_position - 1024, os.SEEK_SET)  # Adjust 1024 to a larger buffer if necessary
                lines = log_file.readlines()[-num_lines:]

                for line in lines:
                    if "Mods updated" in line:
                        return f"Mods are up to date"
                return "New update found, restart server using /restart_server (5 minutes). Use /help for other options."
                await asyncio.sleep(1)

        return "Timeout: No update, or script is broken."
    except Exception as e:
        return f"Error reading log file: {e}"


# RCON Command
def execute_rcon_command(command, max_retries=3, timeout=3):
    last_exception = None
    for attempt in range(max_retries):
        try:
            with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT, timeout=timeout) as mcr:
                response = mcr.command(command)
                if response:
                    return response

                time.sleep(1)
        except Exception as e:
            last_exception = e

            timeout += 1
            time.sleep(1)
            continue
    if last_exception:
        return f"Error after {max_retries} attempts: {last_exception}"
    return "Command executed - No RCON response."


def create_embed(title, description, color=discord.Color.blue()):
    embed = discord.Embed(title=title, description=description, color=color)
    return embed


MAX_PLAYERS = get_max_players_from_ini(SERVER_DIR)