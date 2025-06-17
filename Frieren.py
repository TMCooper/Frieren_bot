import discord
from discord import app_commands
from discord.ext import commands
import os
import json
import subprocess
import psutil
import datetime
import time
import platform
import asyncio
from dotenv import load_dotenv
from function.Maid import Maid
from function.Eru import Eru
from function.Yui import Yui
from function.Rias import Rias
from function.Holo import Holo
from function.AnimeView import *
from function.Frieren import Frieren
from function.Mita import Mita

# Chargement des variables d'environnement
load_dotenv()
TOKEN = os.getenv('TOKEN')
DEV_GUILD_ID = int(os.getenv('DEV_GUILD_ID'))
DEV_ID = int(os.getenv('DEV_ID'))

# Configuration du bot
intents = discord.Intents.all()
# intents.message_content = True
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

# Commande : /code
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

# Commande : /translate
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

# shutdown
@bot.tree.command(
    name="shutdown",
    description="down le bot",
)

async def shudown(interaction: discord.Interaction):
    await interaction.response.defer()
    msg = await Holo.shutdown(bot, interaction.user.id, interaction)
    if msg:
        await interaction.followup.send(msg)

# reboot
@bot.tree.command(
    name="reboot",
    description="redémarre le bot",
)
async def reboot(interaction: discord.Interaction):
    await interaction.response.defer()
    msg = await Holo.reboot(bot, interaction.user.id, interaction)
    if msg:
        await interaction.followup.send(msg)

# Commande : /anime_refresh
@bot.tree.command(
    name="anime_refresh",
    description="Rafraîchit les données des animes",
)
async def anime_refresh(interaction: discord.Interaction):
    msg = await Maid.voiranime_scrap_catalogue(interaction.user.id, interaction)
    if msg == None:
        await interaction.response.send_message("Seul le développeur peut utiliser cette commande.")

# Commande : /animate_search
@bot.tree.command(
    name="anime_search",
    description="Rechercher un anime par son nom"
)
@app_commands.describe(nom="Nom de l'anime à rechercher")
async def anime_search(interaction: discord.Interaction, nom: str):
    await interaction.response.defer()

    try:
        with open("anime.json", "r", encoding="utf-8") as file:
            anime_data = json.load(file)

        seen_anime = set()  # Pour éviter les doublons
        matching_animes = []

        for anime in anime_data:
            anime_name = anime["anime_name"].strip().lower()
            if nom.lower() in anime_name and anime_name not in seen_anime:
                matching_animes.append(anime)
                seen_anime.add(anime_name)  # Ajout au set pour éviter un doublon

        if not matching_animes:
            await interaction.followup.send(
                f"❌ Aucun anime trouvé pour '{nom}'. Essayez avec un autre nom.",
                ephemeral=True
            )
            return

        # Créer un embed pour montrer les résultats
        embed = discord.Embed(
            title=f"🔍 Recherche d'anime : {nom}",
            description=f"J'ai trouvé {len(matching_animes)} résultats",
            color=discord.Color.blue()
        )

        # Afficher la première image trouvée comme thumbnail
        if matching_animes[0].get("image_url"):
            embed.set_thumbnail(url=matching_animes[0]["image_url"])

        view = AnimeView(matching_animes)
        await interaction.followup.send(embed=embed, view=view)

    except Exception as e:
        await interaction.followup.send(
            "Une erreur s'est produite lors de la recherche. Veuillez réessayer.",
            ephemeral=True
        )
        print(f"Erreur: {e}")

# purge_anime_file
@bot.tree.command(
    name="purge_anime_file",
    description="Purge le fichier anime.json",
)
async def purge_anime_file(interaction: discord.Interaction):
    await interaction.response.defer()
    await Holo.purge_anime_file(interaction.user.id, interaction)

#update_bot
@bot.tree.command(
    name="update_bot",
    description="Update le bot"
)
async def update_bot(interaction: discord.Integration):
    await interaction.response.defer()
    msg = await Holo.update(bot, interaction.user.id, interaction)
    if msg:
        await interaction.followup.send(msg)

#status
@bot.tree.command(
    name="status",
    description="Donne quelque information de base du bot",
)
async def status(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(
        title="Status du bot",
        description=f"Utilisant Python {platform.python_version()}",
        color=discord.Color.blue()
    )
    embed.add_field(name="Utilisation mémoire", value=f"{psutil.virtual_memory().percent:.2f}%")
    embed.add_field(name="Utilisation CPU", value=f"{psutil.cpu_percent()}%")
    embed.add_field(name="Utilisation de la bande passante", value=f"{psutil.net_io_counters().bytes_sent / 1024 / 1024:.2f} MB/s")
    embed.set_footer(text=f"Bot par TMCooper")
    await interaction.followup.send(embed=embed)

# info
@bot.tree.command(
    name="info",
    description="Donne quelque lien utile pour le bot",
)
async def info(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(
        title="Informations utiles",
        description="Liens utiles pour accéder au dashboard du bot",
        color=discord.Color.blue()
    )
    embed.add_field(name="Documentation", value="https://github.com/TMCooper/Frieren_bot")
    # embed.add_field(name="Aide Discord", value="https://discord.gg/j99Xw9d")
    await interaction.followup.send(embed=embed)

# refresh_speedrun (Admin seulement)
@bot.tree.command(
    name="refresh_speedrun",
    description="Actualise la base de données des jeux pour les speedruns (Admin seulement)"
)
async def refresh_speedrun(interaction: discord.Interaction):
    await interaction.response.defer()
    if interaction.user.id == DEV_ID:
        try:
            # Vérification des permissions
            result = await Frieren.speedrun_refresh(interaction.user.id)
            
            # Création d'un embed pour la réponse
            embed = discord.Embed(
                title="📊 Actualisation de la base de données Speedrun",
                description=result,
                color=discord.Color.blue() if "terminée" in result else discord.Color.red()
            )
            
            embed.set_footer(text="Base de données mise à jour le")
            embed.timestamp = datetime.datetime.now()
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            error_message = f"Une erreur s'est produite: {str(e)}"
            await interaction.followup.send(error_message)
    
    else :
        await interaction.followup.send("Vous n'êtes pas autorisé à utiliser cette commande.")

# speedrun
@bot.tree.command(
    name="speedrun",
    description="Affiche le classement mondial des speedruns Any% pour le jeu de votre choix"
)
@app_commands.describe(jeu="Nom du jeu dont vous voulez voir les records")
async def speedrun(interaction: discord.Interaction, jeu: str):
    await interaction.response.defer()
    
    try:
        top_speedrun_data = await Frieren.speedrun_main(jeu)
        
        if top_speedrun_data == "None":
            return await interaction.followup.send("Fichier introuvable. Demandez au créateur d'utiliser la commande `/refresh_speedrun` pour créer la base de données des jeux.")
        
        if isinstance(top_speedrun_data, str):
            return await interaction.followup.send(top_speedrun_data)
        
        # Création de l'embed avec un style amélioré
        embed = discord.Embed(
            title=f"🏃‍♂️ Classement Mondial Speedrun Any% 🏆",
            description=f"**{jeu}**",
            color=discord.Color.gold()  # Couleur or pour un aspect plus premium
        )

        # Ajout de l'image du jeu avec une taille optimisée
        if 'Image URL' in top_speedrun_data and top_speedrun_data['Image URL'] != "Image non trouvée":
            try:
                embed.set_thumbnail(url=top_speedrun_data['Image URL'])
            except Exception as e:
                print(f"Erreur lors de l'ajout de l'image: {str(e)}")
                # Continue même si l'image ne peut pas être ajoutée

        # Ajout d'informations supplémentaires dans l'en-tête
        embed.add_field(
            name="ℹ️ Informations",
            value="Classement basé sur les meilleurs temps en Any%\nMis à jour via speedrun.com",
            inline=False
        )

        # Création du classement avec des emojis pour les médailles
        if 'Top Results' in top_speedrun_data and isinstance(top_speedrun_data['Top Results'], list):
            # Mapping des médailles
            medals = {
                "1": "🥇",
                "2": "🥈",
                "3": "🥉",
                "1er": "🥇",
                "2ème": "🥈", 
                "3ème": "🥉"
            }
            
            for i, rank in enumerate(top_speedrun_data['Top Results'], 1):
                # Fallback si le rang n'est pas bien détecté
                rank_display = rank.get('Rank', str(i))
                medal = medals.get(rank_display, medals.get(str(i), "🎮"))
                
                # Formatage amélioré des informations de chaque run
                player_name = rank.get('Player', 'Inconnu')
                country = f"({rank.get('Country', '??')})" if rank.get('Country') != "N/A" else ""
                time_formatted = f"⏱️ {rank.get('Time', 'Temps inconnu')}"
                date_formatted = f"📅 {rank.get('Date', 'Date inconnue')}"
                
                value_text = (
                    f"👤 **{player_name}** {country}\n"
                    f"{time_formatted}\n"
                    f"{date_formatted}\n"
                    "┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄"  # Séparateur décoratif
                )
                
                embed.add_field(
                    name=f"{medal} {rank_display if rank_display != 'N/A' else f'{i}ème'} Place",
                    value=value_text,
                    inline=False
                )
        elif 'Top Results' in top_speedrun_data and isinstance(top_speedrun_data['Top Results'], str):
            # Cas où top_speedrun_data['Top Results'] est un message d'erreur
            embed.add_field(
                name="Résultats",
                value=top_speedrun_data['Top Results'],
                inline=False
            )
        else:
            embed.add_field(
                name="Résultats",
                value="Aucun résultat trouvé pour ce jeu en catégorie Any%.",
                inline=False
            )

        # Pied de page amélioré
        embed.set_footer(
            text="Données fournies par speedrun.com | Utilisez /speedrun <jeu> pour voir d'autres classements",
            icon_url="https://www.speedrun.com/favicon.ico"  # Icône de speedrun.com
        )

        # Timestamp pour montrer quand les données ont été récupérées
        embed.timestamp = datetime.datetime.now()

        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        error_message = f"Une erreur s'est produite lors de la récupération des données: {str(e)}"
        print(error_message)
        await interaction.followup.send(error_message)

# game_file
@bot.tree.command(
    name="games_file",
    description="Vérifie si le fichier des jeux est accessible.",
)
async def games_file(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if interaction.user.id == DEV_ID:
        user_id = interaction.user.id

        # Vérifie si le fichier existe
        games_file_exists = await Mita.debug_game(user_id)
        
        # Vérifie la valeur retournée par debug_game
        if games_file_exists is True:
            await interaction.followup.send("Le fichier des jeux est accessible.")
        elif games_file_exists is False:
            await interaction.followup.send("Le fichier des jeux est introuvable ou illisible.")
        else:  # Si un message est retourné (par exemple, utilisateur non autorisé)
            await interaction.followup.send(games_file_exists)
    else :
        await interaction.followup.send("Vous n'êtes pas autorisé à utiliser cette commande.")

# dashboard
@bot.tree.command(
    name="dashboard",
    description="Donne quelque lien pour accéder au dashboard du bot",
)
async def dashboard(interaction: discord.Interaction):
    await interaction.response.defer()
    embed = discord.Embed(
        title="Dashboard du bot",
        description="Liens utiles pour le dashboard du bot",
        color=discord.Color.blue()
    )
    embed.add_field(name="Dashboard localhost du bot", value="http://127.0.0.1:8080/")
    await interaction.followup.send(embed=embed)

@bot.tree.command(
    name="setup_aga",
    description="Initialise le market de grow a garden avec envoi automatique toutes les 5 minutes"
)
async def setup_aga(interaction: discord.Interaction):
    global aga_task, aga_channel
    
    await interaction.response.defer()
    
    # Stocker le canal pour les envois futurs
    aga_channel = interaction.channel
    
    try:
        # Arrêter la tâche précédente si elle existe
        if aga_task and not aga_task.cancelled():
            aga_task.cancel()
            print("Ancienne tâche AGA arrêtée")
        
        # Démarrer la nouvelle tâche récurrente SANS faire le premier appel
        aga_task = asyncio.create_task(aga_recurring_task())
        
        # Calculer la prochaine exécution
        wait_seconds, next_time = Maid.get_next_5min_interval()
        next_time_str = next_time.strftime("%H:%M:%S")
        
        await interaction.followup.send(f"✅ Setup AGA terminé ! Envoi automatique toutes les 5 minutes activé.\n🕐 Prochaine exécution : {next_time_str}")
        
    except Exception as e:
        print(f"Erreur lors du setup AGA: {e}")
        await interaction.followup.send(f"❌ Erreur lors du setup: {e}")

async def aga_recurring_task():
    """Tâche récurrente qui s'exécute à des heures fixes (multiples de 5 minutes + 30s buffer)"""
    global aga_channel
    
    try:
        while True:
            # Attendre jusqu'au prochain multiple de 5 minutes + buffer
            wait_seconds, next_time = Maid.get_next_5min_interval()
            print(f"Prochaine exécution prévue à {next_time.strftime('%H:%M:%S')} (attente de {wait_seconds:.0f} secondes)")
            await asyncio.sleep(wait_seconds)
            
            if aga_channel:
                try:
                    embed_result = await Maid.shop_aga()
                    
                    # Vérifier que le résultat est bien un embed et non un message d'erreur
                    if isinstance(embed_result, discord.Embed):
                        # Déboguer l'embed avant envoi
                        print(f"Embed title: {embed_result.title}")
                        print(f"Embed description: {embed_result.description}")
                        print(f"Nombre de fields: {len(embed_result.fields)}")
                        
                        # Envoyer l'embed
                        await aga_channel.send(embed=embed_result)
                        current_time = datetime.datetime.now().strftime("%H:%M:%S")
                        print(f"Envoi AGA automatique effectué à {current_time}")
                    
                except Exception as e:
                    print(f"Erreur lors de l'envoi automatique AGA: {e}")
                    # Optionnel: envoyer un message d'erreur dans le canal
                    # await aga_channel.send(f"❌ Erreur lors de la mise à jour automatique: {e}")
            
    except asyncio.CancelledError:
        print("Tâche récurrente AGA annulée")
    except Exception as e:
        print(f"Erreur dans la tâche récurrente AGA: {e}")

@bot.tree.command(
    name="imediat_aga",
    description="Test immédiat du market AGA"
)
async def imediat_aga(interaction: discord.Interaction):
    await interaction.response.defer()
    
    try:
        embed_result = await Maid.shop_aga()
        
        if isinstance(embed_result, discord.Embed):
            await interaction.followup.send(embed=embed_result)
        else:
            await interaction.followup.send(f"Erreur: {embed_result}")
            
    except Exception as e:
        await interaction.followup.send(f"❌ Erreur lors du test: {e}")

# Commande optionnelle pour arrêter la tâche
@bot.tree.command(
    name="stop_aga",
    description="Arrête l'envoi automatique du market AGA"
)
async def stop_aga(interaction: discord.Interaction):
    global aga_task
    
    await interaction.response.defer()
    
    if aga_task and not aga_task.cancelled():
        aga_task.cancel()
        aga_task = None
        await interaction.followup.send("⏹️ Envoi automatique AGA arrêté.")
    else:
        await interaction.followup.send("ℹ️ Aucune tâche AGA active à arrêter.")

# Optionnel: Commande pour vérifier le statut
@bot.tree.command(
    name="status_aga",
    description="Vérifie le statut de la tâche automatique AGA"
)
async def status_aga(interaction: discord.Interaction):
    global aga_task, aga_channel
    
    if aga_task and not aga_task.cancelled():
        channel_name = aga_channel.name if aga_channel else "Canal inconnu"
        
        # Calculer la prochaine exécution
        _, next_time = Maid.get_next_5min_interval()
        next_time_str = next_time.strftime("%H:%M")
        
        await interaction.response.send_message(
            f"✅ Tâche AGA active dans #{channel_name}\n🕐 Prochaine exécution : {next_time_str}"
        )
    else:
        await interaction.response.send_message("❌ Aucune tâche AGA active")

# Démarrage du bot et le serveur web
subprocess.run('source ./venv/bin/activate', shell=True)
subprocess.run(['python', '-m', 'playwright', 'install']) #pour la cloud version
delay = 3000 / 1000  # Convertir millisecondes en secondes
time.sleep(delay)  # Pause de 3 secondes
Yui.alive()
bot.run(TOKEN)