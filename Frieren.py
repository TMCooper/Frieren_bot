import discord
from discord.ext import commands
import os
import subprocess
from dotenv import load_dotenv
from function.Maid import Maid
import asyncio

# Chargement des variables d'environnement
load_dotenv()
TOKEN = os.getenv('TOKEN')
DEV_GUILD_ID = int(os.getenv('DEV_GUILD_ID'))

# Configuration du bot
intents = discord.Intents.all()
# intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    subprocess.run('cls', shell=True)  # Efface la console (Windows uniquement)
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

# Commande : /hello
@bot.tree.command(
    name="hello",
    description="Petit bonjour de Frieren",
)
async def hello(interaction: discord.Interaction, member: discord.Member):
    if member is None:
        await interaction.response.send_message("Veuillez mentionner un membre valide.", ephemeral=True)
        return
    await interaction.response.send_message(f"Hello {member.mention} :kiss:")

# Commande : /hello_world
@bot.tree.command(
    name="hello_world",
    description="Un petit hello world ma foi aussi simple que ça :)",
)
async def hello_world(interaction: discord.Interaction):
    await interaction.response.send_message("Hello World")

# Commande : /code
@bot.tree.command(
    name="code",
    description="Pour obtenir les code d'échange de Genshin ou hsr",
)
# @app_commands.describe(jeux="Le jeu pour lequel vous souhaitez récupérer les codes")
async def code(interaction: discord.Interaction, jeux_entrer: str):
    # met les caractère en minuscule
    jeu = jeux_entrer.lower()

    # envoie une reponse temporaire afin de montrer que le bot traite la commande
    await interaction.response.send_message("Frieren réfléchie", ephemeral=True)

    # appelle la fonction Maid.scrap() pour récupérer les codes
    code_scrap = Maid.scrap(jeu)

    # delay de 3 seconde
    await asyncio.sleep(3)

    # envoie le code d'échange
    await interaction.response.send_message(f"Code d'échange Genshin Impact : \n{code_scrap}")

@bot.tree.command(
    name="my_id",
    description="Donne l'id de l'utilisateur",
)
async def my_id(interaction: discord.Interaction):
    
    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send(f"Votre ID : {interaction.user.id}")

# Démarrage du bot
bot.run(TOKEN)
