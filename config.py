import os

# Discord Configuration
DISCORD_TOKEN = "your token"

# RCON Configuration
RCON_HOST = "your ip"
RCON_PORT = 27015
RCON_PASSWORD = "rcon password"

# File Paths
HOME_DIR = os.path.expanduser("~")
LOG_FILE_PATH = os.path.join(HOME_DIR, "Zomboid", "server-console.txt")
SERVER_DIR = os.path.join(HOME_DIR, "Zomboid", "Server")
LUA_FILE = os.path.join(HOME_DIR, "Zomboid", "Server")
