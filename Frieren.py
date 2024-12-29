import discord
from discord import app_commands
from discord.ext import commands
import os
import subprocess
from dotenv import load_dotenv
from function.Maid import Maid
from function.Eru import Eru
from function.Yui import Yui
from function.Rias import Rias
import time

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
#commands without selenium
@bot.tree.command(
    name="code",
    description="Pour obtenir les code d'échange de Genshin ou Honkai star rail",
)
@app_commands.describe(jeux_entrer="Le jeu pour lequel vous souhaitez récupérer les codes")
@app_commands.choices(jeux_entrer=[
    app_commands.Choice(name="Genshin", value="genshin"),
    app_commands.Choice(name="Honkai Star Rail", value="hsr")
])
# @app_commands.describe(jeux="Le jeu pour lequel vous souhaitez récupérer les codes")
async def code(interaction: discord.Interaction, jeux_entrer: app_commands.Choice[str]):
    # met les caractère en minuscule
    jeu = jeux_entrer.value.lower()

    # envoie une reponse temporaire afin de montrer que le bot traite la commande
    # await interaction.response.send_message("Frieren réfléchie", ephemeral=True)
    await interaction.response.defer(ephemeral=True)

    # appelle la fonction Maid.scrap() pour récupérer les codes
    code_scrap = await Maid.scrap(jeu)

    # envoie le code d'échange
    await interaction.followup.send(f"Code d'échange : \n{code_scrap}")

@bot.tree.command(
    name="my_id",
    description="Donne l'id de l'utilisateur",
)
async def my_id(interaction: discord.Interaction):
    
    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send(f"Votre ID : {interaction.user.id}")

#commands without selenium
@bot.tree.command(
    name="valorant_rank",
    description="Donne le rank de l'utilisateur sur valorant",
)
@app_commands.describe(pseudo="Le pseudo de l'utilisateur")
@app_commands.describe(tag="Le tag de l'utilisateur")
async def valorant_rank(interaction: discord.Interaction, pseudo: str, tag: str):
    await interaction.response.defer(ephemeral=True)
    rank = await Maid.valorant_tracker_rank(pseudo, tag)
    await interaction.followup.send(f"Le rank de {pseudo}#{tag} est : {rank}")

#commands without selenium
@bot.tree.command(
    name="waifu",
    description="Donne une waifu aléatoire",
)
async def waifu(interaction: discord.Interaction):
    await interaction.response.defer()
    name, alternate_name, age, birthday, height, weight, blood_type, waifu_classification, description, like_rank, popularity_rank, image_url = await Eru.random_waifu()

    embed = discord.Embed(title=name, description=description, color=discord.Color.blue())
    embed.set_thumbnail(url=image_url)
    embed.add_field(name="Alternate Name", value=alternate_name, inline=True)
    embed.add_field(name="Age", value=age, inline=True)
    embed.add_field(name="Birthday", value=birthday, inline=True)
    embed.add_field(name="Height", value=height, inline=True)
    embed.add_field(name="Weight", value=weight, inline=True)
    embed.add_field(name="Blood Type", value=blood_type, inline=True)
    embed.add_field(name="Waifu Classification", value=waifu_classification, inline=True)
    embed.add_field(name="Like Rank", value=like_rank, inline=True)
    embed.add_field(name="Popularity Rank", value=popularity_rank, inline=True)

    await interaction.followup.send(embed=embed)

#commands without selenium
@bot.tree.command(
    name="rule34",
    description="Donne une image rule34 avec les tags choisit",
)
@app_commands.describe(tags="Les tags pour la recherche")
async def rule34(interaction: discord.Interaction, tags: str):
    await interaction.response.defer()
    image_url = await Rias.rule34(tags)
    await interaction.followup.send(image_url)

# Démarrage du bot et le serveur web
subprocess.run(['python', '-m', 'playwright', 'install']) #pour la cloud version
delay = 3000 / 1000  # Convertir millisecondes en secondes
time.sleep(delay)  # Pause de 3 secondes
Yui.alive()
bot.run(TOKEN)
