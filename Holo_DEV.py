import discord
from discord import app_commands
from discord.ext import commands
import os
import subprocess
# import datetime
import time
from dotenv import load_dotenv
from function.Maid import Maid
from function.Eru import Eru
from function.Yui import Yui
from function.Rias import Rias
from function.Holo import Holo
# from function.Frieren import Frieren
# from function.Mita import Mita

# Chargement des variables d'environnement
load_dotenv()
TOKEN = os.getenv('TOKEN_DEV')
DEV_GUILD_ID = int(os.getenv('DEV_GUILD_ID'))
DEV_ID = int(os.getenv('DEV_GUILD_ID'))

# Configuration du bot
intents = discord.Intents.all()
# intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    subprocess.run('cls', shell=True)
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

# @bot.tree.command(
#     name="speedrun",
#     description="Affiche le classement mondial des speedruns Any% pour le jeu de votre choix"
# )
# @app_commands.describe(jeu="Nom du jeu dont vous voulez voir les records")
# async def speedrun(interaction: discord.Interaction, jeu: str):
#     await interaction.response.defer()
#     top_speedrun_data = await Frieren.speedrun_main(jeu)
#     if top_speedrun_data == "None":
#         await interaction.followup.send("Fichier introuvable. demander au créateur d'utiliser la ``/refresh_speedrun`` pour le créer.")

#     elif top_speedrun_data != "None":
#         # Création de l'embed avec un style amélioré
#         embed = discord.Embed(
#             title=f"🏃‍♂️ Classement Mondial Speedrun Any% 🏆",
#             description=f"**{jeu}**",
#             color=discord.Color.gold()  # Couleur or pour un aspect plus premium
#         )

#         # Ajout de l'image du jeu avec une taille optimisée
#         if 'Image URL' in top_speedrun_data:
#             embed.set_thumbnail(url=top_speedrun_data['Image URL'])

#         # Ajout d'informations supplémentaires dans l'en-tête
#         embed.add_field(
#             name="ℹ️ Informations",
#             value="Classement basé sur les meilleurs temps en Any%\nMis à jour régulièrement via speedrun.com",
#             inline=False
#         )

#         # Création du classement avec des emojis pour les médailles
#         if 'Top Results' in top_speedrun_data:
#             # On garde le tri par rang plutôt que par nom de joueur pour un vrai classement
#             medals = {
#                 "1er": "🥇",
#                 "2ème": "🥈",
#                 "3ème": "🥉"
#             }
            
#             for rank in top_speedrun_data['Top Results']:
#                 medal = medals.get(rank['Rank'], "🎮")
                
#                 # Formatage amélioré des informations de chaque run
#                 time_formatted = f"⏱️ {rank['Time']}"
#                 date_formatted = f"📅 {rank['Date']}"
                
#                 embed.add_field(
#                     name=f"{medal} {rank['Rank']} Place",
#                     value=(
#                         f"👤 **{rank['Player']}** ({rank['Country']})\n"
#                         f"{time_formatted}\n"
#                         f"{date_formatted}\n"
#                         "┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄"  # Séparateur décoratif
#                     ),
#                     inline=False
#                 )

#         # Pied de page amélioré
#         embed.set_footer(
#             text="Données fournies par speedrun.com | Utilisez /speedrun <jeu> pour voir d'autres classements",
#             icon_url="https://www.speedrun.com/favicon.ico"  # Icône de speedrun.com
#         )

#         # Timestamp pour montrer quand les données ont été récupérées
#         embed.timestamp = datetime.datetime.utcnow()

#         await interaction.followup.send(embed=embed)


# commande a retapper car étrangement long même si le test.py
# @bot.tree.command(
#     name="games_file",
#     description="Vérifie si le fichier des jeux est accessible.",
# )
# async def games_file(interaction: discord.Interaction):
#     await interaction.response.defer(ephemeral=True)
#     user_id = interaction.user.id

#     # Vérifie si le fichier existe
#     games_file_exists = await Mita.debug_game(user_id)
    
#     # Vérifie la valeur retournée par debug_game
#     if games_file_exists is True:
#         await interaction.followup.send("Le fichier des jeux est accessible.")
#     elif games_file_exists is False:
#         await interaction.followup.send("Le fichier des jeux est introuvable ou illisible.")
#     else:  # Si un message est retourné (par exemple, utilisateur non autorisé)
#         await interaction.followup.send(games_file_exists)

@bot.tree.command(
    name="translate",
    description="Traduit une phrase dans la langue de votre choix",
)
@app_commands.describe(phrase="Phrase à traduire")
@app_commands.describe(langues="Langues disponibles : Japonais, Français, Anglais, Espagnole, Allemand, Chinois, Italien, Russe, Portugais, Polonais, Catalan, Grecque, Danois, Hollandais, Suédois")
@app_commands.choices(langues=[
    app_commands.Choice(name="Japonais", value="ja"),
    app_commands.Choice(name="Français", value="fr"),
    app_commands.Choice(name="Anglais", value="en"),
    app_commands.Choice(name="Espagnole", value="es"),
    app_commands.Choice(name="Allemand", value="de"),
    app_commands.Choice(name="Chinois", value="zh-CN"),
    app_commands.Choice(name="Italien", value="it"),
    app_commands.Choice(name="Russe", value="ru"),
    app_commands.Choice(name="Portugaisse", value="pt-BR"),
    app_commands.Choice(name="Polonais", value="pl"),
    app_commands.Choice(name="Catalan", value="ca"),
    app_commands.Choice(name="Grecque", value="el"),
    app_commands.Choice(name="Danois", value="da"),
    app_commands.Choice(name="Hollandais", value="nl"),
    app_commands.Choice(name="Suédois", value="sv")
])
async def translate(interaction: discord.Interaction, phrase: str, langues: app_commands.Choice[str]):
    await interaction.response.defer()
    formated_traduction, prononce = await Holo.Translate(phrase, langues.value)
    await interaction.followup.send(f'Phrase : ``{phrase}`` Vers : ``{langues.name}`` \n Traduction : ``{formated_traduction}`` \n Prononciation : ``{prononce}``')

@bot.tree.command(
    name="shutdown",
    description="down le bot",
)

async def shudown(interaction: discord.Interaction):
    await interaction.response.defer()
    msg = await Holo.shutdown(bot, interaction.user.id, interaction)
    if msg:
        await interaction.followup.send(msg)
    
@bot.tree.command(
    name="reboot",
    description="redémarre le bot",
)
async def reboot(interaction: discord.Interaction):
    await interaction.response.defer()
    msg = await Holo.reboot(bot, interaction.user.id, interaction)
    if msg:
        await interaction.followup.send(msg)

# Démarrage du bot et le serveur web
subprocess.run(['python', '-m', 'playwright', 'install']) #pour la cloud version
delay = 3000 / 1000  # Convertir millisecondes en secondes
time.sleep(delay)  # Pause de 3 secondes
Yui.alive()
bot.run(TOKEN)
