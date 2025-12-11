import discord
from discord.ext import commands
import os
import subprocess
import platform
import asyncio
import time
from dotenv import load_dotenv
from function.Yui import Yui

# Chargement des variables d'environnement
load_dotenv()
TOKEN = os.getenv('TOKEN_DEV')
DEV_GUILD_ID = int(os.getenv('DEV_GUILD_ID'))
DEV_ID = int(os.getenv('DEV_ID'))

# Configuration du bot
intents = discord.Intents.all()
# # intents.message_content = True
intents.voice_states = True
intents.guilds = True
intents.members = True  # nécessaire pour les IDs utilisateurs
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    if platform.system() == "Windows":
        subprocess.run('cls', shell=True)
    elif platform.system() == "Linux":
         subprocess.run('clear', shell=True)
    print(f"{bot.user} est Réveillé !\n")
    print(f"ID du serveur configuré : {DEV_GUILD_ID}")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s) synchroniser")
    except Exception as e:
        print(f"Erreur lors de la synchronisation des commandes : {e}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    try:
        member = message.author
        message_content = message.content
        nom_serv = message.guild.name
        print(f'Sur le serveur : {nom_serv} \nMessage de {member.name} : {message_content}')
    except Exception as e:
        print(f"Erreur lors de la réception du message : {e}")

    await bot.process_commands(message)

async def load_extensions():
    for filename in os.listdir('./commands'):
        if filename.endswith('.py') and filename != "__init__.py":
            try:
                await bot.load_extension(f'commands.{filename[:-3]}')
                print(f'Extension {filename} chargée.')
            except Exception as e:
                print(f'Erreur lors du chargement de {filename}: {e}')

async def main():
    async with bot:
        await load_extensions()
        # Démarrage du bot et le serveur web
        # Note: subprocess for playwright install might be needed but simpler to keep it if original had it.
        # Original: subprocess.run(['python', '-m', 'playwright', 'install'])
        if platform.system() == "Windows" or platform.system() == "Linux": # Keeping logic similar
             subprocess.run(['python', '-m', 'playwright', 'install']) 
        
        delay = 3000 / 1000
        time.sleep(delay)
        Yui.alive()
        await bot.start(TOKEN)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Handle graceful shutdown if needed
        pass
