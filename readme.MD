This Discord Bot was made for personal use, set it to public for anyone needing to setup a bot for their Zomboid Server.
Install requirements using >pip install -r requirements.txt

**WHAT IT CAN DO** (so far ...)
Monitor and display player count as status.
Send a few RCON commands to the server's Zomboid console (see /help). 
Perform stop/start/restart of running instance - requires modification for these commands. 

Make sure that you update the following under config.py

BOT
DISCORD_TOKEN = "your_discord_token" - your bot's token (https://discord.com/developers/applications)

RCON Configuration
RCON_HOST = "0.0.0.0" (your server's IP)
RCON_PORT = 27015 - (your RCON port)
RCON_PASSWORD = "rcon_password" - (your RCON password)

Check bot_commands.py as well as some commands made are not tied with RCON but with the Linux terminal, this includes start_server, stop_server, restart_server. Change to your own values.
