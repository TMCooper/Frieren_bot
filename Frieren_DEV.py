import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import get
import os
import json
import subprocess
import datetime
import time
import platform
import asyncio
import psutil # type: ignore
from dotenv import load_dotenv
from function.Maid import Maid
from function.Eru import Eru
from function.Yui import Yui
from function.Rias import Rias
from function.Holo import Holo
from function.AnimeView import *
from function.Frieren import Frieren
from function.Mita import Mita

# Variable globale pour stocker la tâche et le canal
aga_tasks = {}  # {guild_id: task}
aga_channels = {}  # {guild_id: channel}

# Chargement des variables d'environnement
load_dotenv()
TOKEN = os.getenv('TOKEN_DEV')
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
#rule34
@bot.tree.command(
    name="rule34",
    description="Donne une image rule34 avec les tags choisit",
)
@app_commands.describe(tags="Les tags pour la recherche")
async def rule34(interaction: discord.Interaction, tags: str):
    await interaction.response.defer()
    image_url = await Rias.rule34(tags)
    await interaction.followup.send(image_url)

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

# commande a retapper car étrangement long même si le test.py
@bot.tree.command(
    name="games_file",
    description="Vérifie si le fichier des jeux est accessible.",
)
async def games_file(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
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

#translate
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

#reboot
@bot.tree.command(
    name="reboot",
    description="redémarre le bot",
)
async def reboot(interaction: discord.Interaction):
    await interaction.response.defer()
    msg = await Holo.reboot(bot, interaction.user.id, interaction)
    if msg:
        await interaction.followup.send(msg)

#anime_refresh
@bot.tree.command(
    name="anime_refresh",
    description="Rafraîchit les données des animes",
)
async def anime_refresh(interaction: discord.Interaction):
    msg = await Maid.voiranime_scrap_catalogue(interaction.user.id, interaction)
    if msg == None:
        await interaction.response.send_message("Seul le développeur peut utiliser cette commande.")

#anime_search
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


#purge_anime_file
@bot.tree.command(
    name="purge_anime_file",
    description="Purge le fichier anime.json",
)
async def purge_anime_file(interaction: discord.Interaction):
    await interaction.response.defer()
    await Holo.purge_anime_file(interaction.user.id, interaction)

# update_bot
@bot.tree.command(
        name="update_bot",
        description="Update le bot"
    )
async def update_bot(interaction: discord.Integration):
    await interaction.response.defer()
    msg = await Holo.update(bot, interaction.user.id, interaction)
    if msg:
        await interaction.followup.send(msg)

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

#Dashboard

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
    guild_id = interaction.guild_id
    
    await interaction.response.defer()
    
    # Stocker le canal pour ce serveur spécifique
    aga_channels[guild_id] = interaction.channel
    
    try:
        # Arrêter la tâche précédente pour ce serveur si elle existe
        if guild_id in aga_tasks and not aga_tasks[guild_id].cancelled():
            aga_tasks[guild_id].cancel()
            print(f"[Guild {guild_id}] Ancienne tâche AGA arrêtée")
        
        # Démarrer la nouvelle tâche récurrente pour ce serveur
        aga_tasks[guild_id] = asyncio.create_task(aga_recurring_task(guild_id))
        
        # Calculer la prochaine exécution
        wait_seconds, next_time = Maid.get_next_5min_interval()
        next_time_str = next_time.strftime("%H:%M:%S")
        
        await interaction.followup.send(
            f"✅ Setup AGA terminé pour ce serveur ! Envoi automatique toutes les 5 minutes activé.\n"
            f"🕐 Prochaine exécution : {next_time_str}\n"
            f"📊 Serveurs actifs : {len(aga_tasks)}\n"
            f"🍎 Mentions des fruits activées\n"
            f"⚙️ Mentions des gears activées"
        )
        
    except Exception as e:
        print(f"[Guild {guild_id}] Erreur lors du setup AGA: {e}")
        await interaction.followup.send(f"❌ Erreur lors du setup: {e}")

async def aga_recurring_task(guild_id):
    """Tâche récurrente pour un serveur spécifique"""
    while True:
        try:
            # Calculer le temps d'attente jusqu'au prochain intervalle
            wait_seconds, next_time = Maid.get_next_5min_interval()
            print(f"[Guild {guild_id}] Attente de {wait_seconds:.1f} secondes jusqu'à {next_time.strftime('%H:%M:%S')}")
            
            # Attendre jusqu'au prochain intervalle
            await asyncio.sleep(wait_seconds)
            
            # Vérifier que le canal existe encore
            if guild_id not in aga_channels:
                print(f"[Guild {guild_id}] Canal non trouvé, arrêt de la tâche")
                break
                
            channel = aga_channels[guild_id]
            
            # Vérifier que le canal est encore accessible
            try:
                await channel.fetch_message(channel.last_message_id) if channel.last_message_id else None
            except:
                print(f"[Guild {guild_id}] Canal inaccessible, arrêt de la tâche")
                # Nettoyer les références
                if guild_id in aga_channels:
                    del aga_channels[guild_id]
                if guild_id in aga_tasks:
                    del aga_tasks[guild_id]
                break
            
            # Récupérer et envoyer les données avec support des gears
            result = await Maid.shop_aga(guild_id)
            
            # Gérer le tuple retourné
            if isinstance(result, tuple):
                embed, mentions = result
            else:
                embed = result
                mentions = None

            # Envoyer le message
            if mentions and mentions.strip():
                await channel.send(content=mentions, embed=embed, allowed_mentions=discord.AllowedMentions(roles=True))
                print(f"[Guild {guild_id}] Market AGA envoyé avec mentions (fruits + gears) à {datetime.datetime.now().strftime('%H:%M:%S')}")
            else:
                await channel.send(embed=embed)
                print(f"[Guild {guild_id}] Market AGA envoyé sans mentions à {datetime.datetime.now().strftime('%H:%M:%S')}")
            
        except asyncio.CancelledError:
            print(f"[Guild {guild_id}] Tâche AGA annulée")
            break
        except Exception as e:
            print(f"[Guild {guild_id}] Erreur dans la tâche AGA: {e}")
            await asyncio.sleep(60)

@bot.tree.command(
    name="imediat_aga",
    description="Test immédiat du market AGA avec mentions des fruits et gears"
)
async def imediat_aga(interaction: discord.Interaction):
    await interaction.response.defer()
    
    try:
        result = await Maid.shop_aga(interaction.guild_id)
        
        if isinstance(result, tuple):
            embed_result, mentions = result
            print(f"Mentions reçues (fruits + gears): {mentions}")
        else:
            embed_result = result
            mentions = None
        
        if isinstance(embed_result, discord.Embed):
            if mentions and mentions.strip():
                await interaction.followup.send(
                    content=f"🔔 {mentions}", 
                    embed=embed_result,
                    allowed_mentions=discord.AllowedMentions(roles=True)
                )
                print("Message envoyé avec mentions des fruits et gears")
            else:
                await interaction.followup.send(
                    content="ℹ️ **Test du market sans mentions** (aucun fruit/gear configuré trouvé)",
                    embed=embed_result
                )
                print("Message envoyé sans mentions")
        else:
            await interaction.followup.send(f"Erreur: {embed_result}")
            
    except Exception as e:
        print(f"Erreur complète: {e}")
        await interaction.followup.send(f"❌ Erreur lors du test: {e}")

# Commande pour arrêter la tâche
@bot.tree.command(
    name="stop_aga",
    description="Arrête l'envoi automatique du market AGA pour ce serveur"
)
async def stop_aga(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    
    await interaction.response.defer()
    
    try:
        # Arrêter la tâche pour ce serveur
        if guild_id in aga_tasks:
            if not aga_tasks[guild_id].cancelled():
                aga_tasks[guild_id].cancel()
            del aga_tasks[guild_id]
            
        # Supprimer le canal stocké
        if guild_id in aga_channels:
            del aga_channels[guild_id]
            
        await interaction.followup.send(
            f"✅ Tâche AGA arrêtée pour ce serveur.\n"
            f"📊 Serveurs encore actifs : {len(aga_tasks)}"
        )
        
    except Exception as e:
        print(f"[Guild {guild_id}] Erreur lors de l'arrêt AGA: {e}")
        await interaction.followup.send(f"❌ Erreur lors de l'arrêt: {e}")

# Commande pour vérifier le statut
@bot.tree.command(
    name="status_aga",
    description="Affiche le statut de l'envoi automatique AGA"
)
async def status_aga(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    
    await interaction.response.defer()
    
    # Statut pour ce serveur
    is_active = guild_id in aga_tasks and not aga_tasks[guild_id].cancelled()
    channel_set = guild_id in aga_channels
    
    # Prochaine exécution
    if is_active:
        wait_seconds, next_time = Maid.get_next_5min_interval()
        next_time_str = next_time.strftime("%H:%M:%S")
        status_msg = f"🟢 **Actif** - Prochaine exécution : {next_time_str}"
    else:
        status_msg = "🔴 **Inactif**"
    
    embed = discord.Embed(
        title="📊 Statut AGA Market",
        color=0x4CAF50 if is_active else 0xF44336
    )
    
    embed.add_field(
        name="Ce serveur",
        value=status_msg,
        inline=False
    )
    
    embed.add_field(
        name="Canal configuré",
        value=f"🟢 {aga_channels[guild_id].mention}" if channel_set else "🔴 Aucun",
        inline=True
    )
    
    embed.add_field(
        name="Total serveurs actifs",
        value=f"{len(aga_tasks)} serveur(s)",
        inline=True
    )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(
    name="fruit_role",
    description="Associe un fruit à un rôle à ping lors de l'affichage du market"
)
@app_commands.describe(fruit="Nom du fruit", role="Rôle à ping")
async def fruit_role(interaction: discord.Interaction, fruit: str, role: discord.Role):
    await interaction.response.defer(ephemeral=True)
    
    try:
        # Charger les rôles enregistrés
        if os.path.exists("fruit_roles.json"):
            with open("fruit_roles.json", "r", encoding="utf-8") as f:
                fruit_roles = json.load(f)
        else:
            fruit_roles = {}

        guild_id = str(interaction.guild_id)
        if guild_id not in fruit_roles:
            fruit_roles[guild_id] = {}

        # Normaliser le nom du fruit (utiliser l'identifier si possible)
        fruit_key = fruit.lower().strip()
        
        # Chercher les infos du fruit dans fruits.json pour avoir plus de détails
        fruit_info = None
        try:
            with open("fruits.json", "r", encoding="utf-8") as f:
                all_fruits = json.load(f)
            
            # Chercher le fruit par nom ou identifier
            for crop in all_fruits:
                if (crop.get("name", "").lower() == fruit.lower() or 
                    crop.get("identifier", "").lower() == fruit.lower()):
                    fruit_info = crop
                    fruit_key = crop.get("identifier", fruit.lower())  # Utiliser l'identifier comme clé
                    break
        except FileNotFoundError:
            pass

        # Enregistrer l'association fruit → role.id
        fruit_roles[guild_id][fruit_key] = role.id

        with open("fruit_roles.json", "w", encoding="utf-8") as f:
            json.dump(fruit_roles, f, ensure_ascii=False, indent=4)

        # Message de confirmation avec plus d'infos si disponibles
        if fruit_info:
            rarity = fruit_info.get("additional", {}).get("Rarity", "Unknown")
            harvest_type = fruit_info.get("additional", {}).get("Harvest Type", "Unknown")
            price = fruit_info.get("price", 0)
            
            embed = discord.Embed(
                title="✅ Association créée",
                description=f"Le fruit **{fruit_info['name']}** est maintenant associé au rôle {role.mention}",
                color=0x4CAF50
            )
            embed.add_field(
                name="📊 Informations",
                value=f"**Rareté:** {rarity}\n**Type:** {harvest_type}\n**Valeur:** {price:,}",
                inline=True
            )
            embed.set_thumbnail(url=fruit_info.get("image", ""))
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send(
                f"✅ Le fruit **{fruit}** est maintenant associé au rôle {role.mention}.", 
                ephemeral=True
            )

    except Exception as e:
        await interaction.followup.send(f"❌ Une erreur est survenue : {str(e)}", ephemeral=True)

@fruit_role.autocomplete("fruit")
async def fruit_autocomplete(interaction: discord.Interaction, current: str):
    try:
        with open("fruits.json", "r", encoding="utf-8") as f:
            all_fruits = json.load(f)
    except FileNotFoundError:
        return [app_commands.Choice(name="❌ Fichier fruits.json introuvable", value="error")]

    current_lower = current.lower()
    suggestions = []
    
    for fruit in all_fruits:
        fruit_name = fruit.get("name", "Unknown")
        fruit_identifier = fruit.get("identifier", "")
        rarity = fruit.get("additional", {}).get("Rarity", "")
        price = fruit.get("price", 0)
        
        # Chercher dans le nom et l'identifier
        if (current_lower in fruit_name.lower() or 
            current_lower in fruit_identifier.lower()):
            
            # Emoji selon la rareté
            rarity_emoji = {
                "Common": "🟢",
                "Uncommon": "🔵", 
                "Rare": "🟣",
                "Epic": "🟠",
                "Legendary": "🟡",
                "Mythical": "🔴",
                "Divine": "✨"
            }.get(rarity, "🍎")
            
            # Format: Emoji + Nom + (Rareté) + Prix
            display_name = f"{rarity_emoji} {fruit_name}"
            if rarity:
                display_name += f" ({rarity})"
            if price > 0:
                display_name += f" - {price:,}"
            
            # Utiliser l'identifier comme valeur pour la cohérence
            value = fruit_identifier if fruit_identifier else fruit_name.lower()
            
            suggestions.append(
                app_commands.Choice(name=display_name[:100], value=value)  # Limite Discord 100 chars
            )
    
    # Trier par rareté puis par prix (optionnel)
    rarity_order = {"Divine": 0, "Mythical": 1, "Legendary": 2, "Epic": 3, "Rare": 4, "Uncommon": 5, "Common": 6}
    
    try:
        suggestions.sort(key=lambda x: (
            rarity_order.get(
                next((f.get("additional", {}).get("Rarity", "Common") 
                      for f in all_fruits 
                      if f.get("identifier") == x.value or f.get("name").lower() == x.value), 
                     "Common"), 
                7
            ),
            -next((f.get("price", 0) 
                   for f in all_fruits 
                   if f.get("identifier") == x.value or f.get("name").lower() == x.value), 
                  0)
        ))
    except:
        pass  # Si le tri échoue, on garde l'ordre original

    return suggestions[:25]  # Discord n'autorise que 25 éléments

# Commande améliorée pour lister les fruits avec leurs infos
@bot.tree.command(
    name="list_fruit_roles",
    description="Affiche tous les fruits configurés avec leurs rôles et informations"
)
async def list_fruit_roles(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    
    try:
        if not os.path.exists("fruit_roles.json"):
            await interaction.followup.send("❌ Aucun fruit configuré.", ephemeral=True)
            return
            
        with open("fruit_roles.json", "r", encoding="utf-8") as f:
            fruit_roles = json.load(f)
        
        guild_id = str(interaction.guild_id)
        if guild_id not in fruit_roles or not fruit_roles[guild_id]:
            await interaction.followup.send("❌ Aucun fruit configuré pour ce serveur.", ephemeral=True)
            return
        
        # Charger les infos des fruits
        fruit_infos = {}
        try:
            with open("fruits.json", "r", encoding="utf-8") as f:
                all_fruits = json.load(f)
                for fruit in all_fruits:
                    identifier = fruit.get("identifier", fruit.get("name", "").lower())
                    fruit_infos[identifier] = fruit
        except FileNotFoundError:
            pass
        
        embed = discord.Embed(
            title="🍎 Fruits configurés",
            description="Liste des fruits avec leurs rôles associés",
            color=0x4CAF50
        )
        
        # Grouper par rareté pour un meilleur affichage
        fruits_by_rarity = {}
        
        for fruit_key, role_id in fruit_roles[guild_id].items():
            role = interaction.guild.get_role(role_id)
            role_mention = role.mention if role else f"❌ Rôle supprimé (ID: {role_id})"
            
            # Récupérer les infos du fruit
            fruit_info = fruit_infos.get(fruit_key, {})
            fruit_name = fruit_info.get("name", fruit_key.title())
            rarity = fruit_info.get("additional", {}).get("Rarity", "Unknown")
            price = fruit_info.get("price", 0)
            
            if rarity not in fruits_by_rarity:
                fruits_by_rarity[rarity] = []
            
            fruit_display = f"🍓 **{fruit_name}**"
            if price > 0:
                fruit_display += f" ({price:,})"
            fruit_display += f"\n└ {role_mention}"
            
            fruits_by_rarity[rarity].append(fruit_display)
        
        # Ajouter les champs par rareté
        rarity_order = ["Divine", "Mythical", "Legendary", "Epic", "Rare", "Uncommon", "Common", "Unknown"]
        
        for rarity in rarity_order:
            if rarity in fruits_by_rarity:
                rarity_emoji = {
                    "Common": "🟢", "Uncommon": "🔵", "Rare": "🟣",
                    "Epic": "🟠", "Legendary": "🟡", "Mythical": "🔴", 
                    "Divine": "✨", "Unknown": "❓"
                }.get(rarity, "❓")
                
                fruits_text = "\n\n".join(fruits_by_rarity[rarity])
                embed.add_field(
                    name=f"{rarity_emoji} {rarity} ({len(fruits_by_rarity[rarity])})",
                    value=fruits_text,
                    inline=False
                )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Erreur : {str(e)}", ephemeral=True)

# Commande pour supprimer un fruit avec autocomplétion
@bot.tree.command(
    name="remove_fruit_role",
    description="Supprime l'association d'un fruit avec un rôle"
)
@app_commands.describe(fruit="Nom du fruit à supprimer")
async def remove_fruit_role(interaction: discord.Interaction, fruit: str):
    await interaction.response.defer(ephemeral=True)
    
    try:
        if not os.path.exists("fruit_roles.json"):
            await interaction.followup.send("❌ Aucun fruit configuré.", ephemeral=True)
            return
            
        with open("fruit_roles.json", "r", encoding="utf-8") as f:
            fruit_roles = json.load(f)
        
        guild_id = str(interaction.guild_id)
        fruit_key = fruit.lower().strip()
        
        if guild_id not in fruit_roles or fruit_key not in fruit_roles[guild_id]:
            await interaction.followup.send(f"❌ Le fruit **{fruit}** n'est pas configuré.", ephemeral=True)
            return
        
        # Supprimer le fruit
        del fruit_roles[guild_id][fruit_key]
        
        # Nettoyer si le serveur n'a plus de fruits
        if not fruit_roles[guild_id]:
            del fruit_roles[guild_id]
        
        with open("fruit_roles.json", "w", encoding="utf-8") as f:
            json.dump(fruit_roles, f, ensure_ascii=False, indent=4)
        
        await interaction.followup.send(f"✅ Le fruit **{fruit}** a été supprimé.", ephemeral=True)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Erreur : {str(e)}", ephemeral=True)

@remove_fruit_role.autocomplete("fruit")
async def remove_fruit_autocomplete(interaction: discord.Interaction, current: str):
    """Autocomplétion pour supprimer - ne montre que les fruits configurés"""
    try:
        # Charger les fruits configurés pour ce serveur
        with open("fruit_roles.json", "r", encoding="utf-8") as f:
            fruit_roles = json.load(f)
        
        guild_id = str(interaction.guild_id)
        if guild_id not in fruit_roles:
            return []
        
        configured_fruits = fruit_roles[guild_id].keys()
        
        # Charger les infos détaillées
        fruit_infos = {}
        try:
            with open("fruits.json", "r", encoding="utf-8") as f:
                all_fruits = json.load(f)
                for fruit in all_fruits:
                    identifier = fruit.get("identifier", fruit.get("name", "").lower())
                    fruit_infos[identifier] = fruit
        except FileNotFoundError:
            pass
        
        suggestions = []
        current_lower = current.lower()
        
        for fruit_key in configured_fruits:
            fruit_info = fruit_infos.get(fruit_key, {})
            fruit_name = fruit_info.get("name", fruit_key.title())
            
            if current_lower in fruit_name.lower() or current_lower in fruit_key:
                rarity = fruit_info.get("additional", {}).get("Rarity", "")
                rarity_emoji = {
                    "Common": "🟢", "Uncommon": "🔵", "Rare": "🟣",
                    "Epic": "🟠", "Legendary": "🟡", "Mythical": "🔴", 
                    "Divine": "✨"
                }.get(rarity, "🍎")
                
                display_name = f"{rarity_emoji} {fruit_name}"
                if rarity:
                    display_name += f" ({rarity})"
                
                suggestions.append(
                    app_commands.Choice(name=display_name, value=fruit_key)
                )
        
        return suggestions[:25]
        
    except Exception as e:
        return [app_commands.Choice(name=f"❌ Erreur: {str(e)}", value="error")]

@bot.tree.command(name="test_ping", description="Test les pings de rôles")
async def test_ping(interaction: discord.Interaction, role_id: str):
    await interaction.response.send_message(f"<@&{role_id}>", allowed_mentions=discord.AllowedMentions(roles=True))

@bot.tree.command(name="list_roles", description="Liste tous les rôles et leurs IDs")
async def list_roles(interaction: discord.Interaction):
    await interaction.response.defer()
    
    guild = interaction.guild
    roles_info = []
    
    for role in guild.roles:
        if role.name != "@everyone":
            mentionable = "✅" if role.mentionable else "❌"
            roles_info.append(f"{mentionable} **{role.name}** - ID: `{role.id}`")
    
    # Diviser en chunks si trop long
    if len(roles_info) > 20:
        roles_info = roles_info[:20] + [f"... et {len(guild.roles) - 21} autres rôles"]
    
    embed = discord.Embed(
        title="📋 Liste des rôles",
        description="\n".join(roles_info),
        color=0x0099FF
    )
    embed.set_footer(text="✅ = Mentionnable, ❌ = Non mentionnable")
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="db_gag_refresh", description="Actualise la base de donnée pour l'autocomplete")
async def db_gag_refresh(interaction: discord.Interaction):
    await interaction.response.defer()
    msg = await Holo.db_gag_refresh(interaction.user.id, interaction)
    if msg:
        await interaction.followup.send(msg)
    
@bot.tree.command(
    name="gear_role",
    description="Associe un gear à un rôle à ping lors de l'affichage du market"
)
@app_commands.describe(gear="Nom du gear", role="Rôle à ping")
async def gear_role(interaction: discord.Interaction, gear: str, role: discord.Role):
    await interaction.response.defer(ephemeral=True)
    
    try:
        # Charger les rôles enregistrés
        if os.path.exists("gear_roles.json"):
            with open("gear_roles.json", "r", encoding="utf-8") as f:
                gear_roles = json.load(f)
        else:
            gear_roles = {}

        guild_id = str(interaction.guild_id)
        if guild_id not in gear_roles:
            gear_roles[guild_id] = {}

        # Normaliser le nom du gear (utiliser l'identifier si possible)
        gear_key = gear.lower().strip()
        
        # Chercher les infos du gear dans gear.json pour avoir plus de détails
        gear_info = None
        try:
            with open("gear.json", "r", encoding="utf-8") as f:
                all_gears = json.load(f)
            
            # Chercher le gear par nom ou identifier
            for item in all_gears:
                if (item.get("name", "").lower() == gear.lower() or 
                    item.get("identifier", "").lower() == gear.lower()):
                    gear_info = item
                    gear_key = item.get("identifier", gear.lower())  # Utiliser l'identifier comme clé
                    break
        except FileNotFoundError:
            pass

        # Enregistrer l'association gear → role.id
        gear_roles[guild_id][gear_key] = role.id

        with open("gear_roles.json", "w", encoding="utf-8") as f:
            json.dump(gear_roles, f, ensure_ascii=False, indent=4)

        # Message de confirmation avec plus d'infos si disponibles
        if gear_info:
            tier = gear_info.get("additional", {}).get("Tier", "Unknown")
            effects = gear_info.get("additional", {}).get("Effects", "Unknown")
            price = gear_info.get("price", 0)
            robux_price = gear_info.get("additional", {}).get("Robux Price", "N/A")
            
            embed = discord.Embed(
                title="✅ Association créée",
                description=f"Le gear **{gear_info['name']}** est maintenant associé au rôle {role.mention}",
                color=0x4CAF50
            )
            embed.add_field(
                name="📊 Informations",
                value=f"**Tier:** {tier}\n**Effets:** {effects}\n**Prix:** {price:,} Sheckles\n**Robux:** {robux_price}",
                inline=True
            )
            embed.set_thumbnail(url=gear_info.get("image", ""))
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send(
                f"✅ Le gear **{gear}** est maintenant associé au rôle {role.mention}.", 
                ephemeral=True
            )

    except Exception as e:
        await interaction.followup.send(f"❌ Une erreur est survenue : {str(e)}", ephemeral=True)

@gear_role.autocomplete("gear")
async def gear_autocomplete(interaction: discord.Interaction, current: str):
    try:
        with open("gear.json", "r", encoding="utf-8") as f:
            all_gears = json.load(f)
    except FileNotFoundError:
        return [app_commands.Choice(name="❌ Fichier gear.json introuvable", value="error")]

    current_lower = current.lower()
    suggestions = []
    
    for gear in all_gears:
        gear_name = gear.get("name", "Unknown")
        gear_identifier = gear.get("identifier", "")
        tier = gear.get("additional", {}).get("Tier", "")
        price = gear.get("price", 0)
        
        # Chercher dans le nom et l'identifier
        if (current_lower in gear_name.lower() or 
            current_lower in gear_identifier.lower()):
            
            # Emoji selon le tier
            tier_emoji = {
                "Common": "🟢",
                "Uncommon": "🔵", 
                "Rare": "🟣",
                "Epic": "🟠",
                "Legendary": "🟡",
                "Mythical": "🔴",
                "Divine": "✨"
            }.get(tier, "⚙️")
            
            # Format: Emoji + Nom + (Tier) + Prix
            display_name = f"{tier_emoji} {gear_name}"
            if tier:
                display_name += f" ({tier})"
            if price > 0:
                display_name += f" - {price:,}"
            
            # Utiliser l'identifier comme valeur pour la cohérence
            value = gear_identifier if gear_identifier else gear_name.lower()
            
            suggestions.append(
                app_commands.Choice(name=display_name[:100], value=value)  # Limite Discord 100 chars
            )
    
    # Trier par tier puis par prix (optionnel)
    tier_order = {"Divine": 0, "Mythical": 1, "Legendary": 2, "Epic": 3, "Rare": 4, "Uncommon": 5, "Common": 6}
    
    try:
        suggestions.sort(key=lambda x: (
            tier_order.get(
                next((g.get("additional", {}).get("Tier", "Common") 
                      for g in all_gears 
                      if g.get("identifier") == x.value or g.get("name").lower() == x.value), 
                     "Common"), 
                7
            ),
            -next((g.get("price", 0) 
                   for g in all_gears 
                   if g.get("identifier") == x.value or g.get("name").lower() == x.value), 
                  0)
        ))
    except:
        pass  # Si le tri échoue, on garde l'ordre original

    return suggestions[:25]  # Discord n'autorise que 25 éléments

# Commande améliorée pour lister les gears avec leurs infos
@bot.tree.command(
    name="list_gear_roles",
    description="Affiche tous les gears configurés avec leurs rôles et informations"
)
async def list_gear_roles(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    
    try:
        if not os.path.exists("gear_roles.json"):
            await interaction.followup.send("❌ Aucun gear configuré.", ephemeral=True)
            return
            
        with open("gear_roles.json", "r", encoding="utf-8") as f:
            gear_roles = json.load(f)
        
        guild_id = str(interaction.guild_id)
        if guild_id not in gear_roles or not gear_roles[guild_id]:
            await interaction.followup.send("❌ Aucun gear configuré pour ce serveur.", ephemeral=True)
            return
        
        # Charger les infos des gears
        gear_infos = {}
        try:
            with open("gear.json", "r", encoding="utf-8") as f:
                all_gears = json.load(f)
                for gear in all_gears:
                    identifier = gear.get("identifier", gear.get("name", "").lower())
                    gear_infos[identifier] = gear
        except FileNotFoundError:
            pass
        
        embed = discord.Embed(
            title="⚙️ Gears configurés",
            description="Liste des gears avec leurs rôles associés",
            color=0x4CAF50
        )
        
        # Grouper par tier pour un meilleur affichage
        gears_by_tier = {}
        
        for gear_key, role_id in gear_roles[guild_id].items():
            role = interaction.guild.get_role(role_id)
            role_mention = role.mention if role else f"❌ Rôle supprimé (ID: {role_id})"
            
            # Récupérer les infos du gear
            gear_info = gear_infos.get(gear_key, {})
            gear_name = gear_info.get("name", gear_key.title())
            tier = gear_info.get("additional", {}).get("Tier", "Unknown")
            price = gear_info.get("price", 0)
            
            if tier not in gears_by_tier:
                gears_by_tier[tier] = []
            
            gear_display = f"⚙️ **{gear_name}**"
            if price > 0:
                gear_display += f" ({price:,})"
            gear_display += f"\n└ {role_mention}"
            
            gears_by_tier[tier].append(gear_display)
        
        # Ajouter les champs par tier
        tier_order = ["Divine", "Mythical", "Legendary", "Epic", "Rare", "Uncommon", "Common", "Unknown"]
        
        for tier in tier_order:
            if tier in gears_by_tier:
                tier_emoji = {
                    "Common": "🟢", "Uncommon": "🔵", "Rare": "🟣",
                    "Epic": "🟠", "Legendary": "🟡", "Mythical": "🔴", 
                    "Divine": "✨", "Unknown": "❓"
                }.get(tier, "❓")
                
                gears_text = "\n\n".join(gears_by_tier[tier])
                embed.add_field(
                    name=f"{tier_emoji} {tier} ({len(gears_by_tier[tier])})",
                    value=gears_text,
                    inline=False
                )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Erreur : {str(e)}", ephemeral=True)

# Commande pour supprimer un gear avec autocomplétion
@bot.tree.command(
    name="remove_gear_role",
    description="Supprime l'association d'un gear avec un rôle"
)
@app_commands.describe(gear="Nom du gear à supprimer")
async def remove_gear_role(interaction: discord.Interaction, gear: str):
    await interaction.response.defer(ephemeral=True)
    
    try:
        if not os.path.exists("gear_roles.json"):
            await interaction.followup.send("❌ Aucun gear configuré.", ephemeral=True)
            return
            
        with open("gear_roles.json", "r", encoding="utf-8") as f:
            gear_roles = json.load(f)
        
        guild_id = str(interaction.guild_id)
        gear_key = gear.lower().strip()
        
        if guild_id not in gear_roles or gear_key not in gear_roles[guild_id]:
            await interaction.followup.send(f"❌ Le gear **{gear}** n'est pas configuré.", ephemeral=True)
            return
        
        # Supprimer le gear
        del gear_roles[guild_id][gear_key]
        
        # Nettoyer si le serveur n'a plus de gears
        if not gear_roles[guild_id]:
            del gear_roles[guild_id]
        
        with open("gear_roles.json", "w", encoding="utf-8") as f:
            json.dump(gear_roles, f, ensure_ascii=False, indent=4)
        
        await interaction.followup.send(f"✅ Le gear **{gear}** a été supprimé.", ephemeral=True)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Erreur : {str(e)}", ephemeral=True)

@remove_gear_role.autocomplete("gear")
async def remove_gear_autocomplete(interaction: discord.Interaction, current: str):
    """Autocomplétion pour supprimer - ne montre que les gears configurés"""
    try:
        # Charger les gears configurés pour ce serveur
        with open("gear_roles.json", "r", encoding="utf-8") as f:
            gear_roles = json.load(f)
        
        guild_id = str(interaction.guild_id)
        if guild_id not in gear_roles:
            return []
        
        configured_gears = gear_roles[guild_id].keys()
        
        # Charger les infos détaillées
        gear_infos = {}
        try:
            with open("gear.json", "r", encoding="utf-8") as f:
                all_gears = json.load(f)
                for gear in all_gears:
                    identifier = gear.get("identifier", gear.get("name", "").lower())
                    gear_infos[identifier] = gear
        except FileNotFoundError:
            pass
        
        suggestions = []
        current_lower = current.lower()
        
        for gear_key in configured_gears:
            gear_info = gear_infos.get(gear_key, {})
            gear_name = gear_info.get("name", gear_key.title())
            
            if current_lower in gear_name.lower() or current_lower in gear_key:
                tier = gear_info.get("additional", {}).get("Tier", "")
                tier_emoji = {
                    "Common": "🟢", "Uncommon": "🔵", "Rare": "🟣",
                    "Epic": "🟠", "Legendary": "🟡", "Mythical": "🔴", 
                    "Divine": "✨"
                }.get(tier, "⚙️")
                
                display_name = f"{tier_emoji} {gear_name}"
                if tier:
                    display_name += f" ({tier})"
                
                suggestions.append(
                    app_commands.Choice(name=display_name, value=gear_key)
                )
        
        return suggestions[:25]
        
    except Exception as e:
        return [app_commands.Choice(name=f"❌ Erreur: {str(e)}", value="error")]

@bot.tree.command(
    name="egg_role",
    description="Associe un œuf à un rôle à ping lors de l'affichage du market"
)
@app_commands.describe(egg="Nom de l'œuf", role="Rôle à ping")
async def egg_role(interaction: discord.Interaction, egg: str, role: discord.Role):
    await interaction.response.defer(ephemeral=True)

    try:
        if os.path.exists("egg_roles.json"):
            with open("egg_roles.json", "r", encoding="utf-8") as f:
                egg_roles = json.load(f)
        else:
            egg_roles = {}

        guild_id = str(interaction.guild_id)
        if guild_id not in egg_roles:
            egg_roles[guild_id] = {}

        egg_key = egg.lower().strip()
        egg_info = None

        try:
            with open("eggs.json", "r", encoding="utf-8") as f:
                all_eggs = json.load(f)
            for e in all_eggs:
                if (e.get("name", "").lower() == egg.lower() or 
                    e.get("identifier", "").lower() == egg.lower()):
                    egg_info = e
                    egg_key = e.get("identifier", egg.lower())
                    break
        except FileNotFoundError:
            pass

        egg_roles[guild_id][egg_key] = role.id

        with open("egg_roles.json", "w", encoding="utf-8") as f:
            json.dump(egg_roles, f, ensure_ascii=False, indent=4)

        if egg_info:
            rarity = egg_info.get("rarity", "Unknown")
            price = egg_info.get("base_value", "Inconnu")

            embed = discord.Embed(
                title="✅ Association créée",
                description=f"L'œuf **{egg_info['name']}** est maintenant associé au rôle {role.mention}",
                color=0x4CAF50
            )
            embed.add_field(name="📊 Informations", value=f"**Rareté:** {rarity}\n**Valeur:** {price}", inline=True)
            embed.set_thumbnail(url=egg_info.get("image", ""))

            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send(
                f"✅ L'œuf **{egg}** est maintenant associé au rôle {role.mention}.",
                ephemeral=True
            )

    except Exception as e:
        await interaction.followup.send(f"❌ Une erreur est survenue : {str(e)}", ephemeral=True)
@egg_role.autocomplete("egg")
async def egg_autocomplete(interaction: discord.Interaction, current: str):
    try:
        with open("eggs.json", "r", encoding="utf-8") as f:
            all_eggs = json.load(f)
    except FileNotFoundError:
        return [app_commands.Choice(name="❌ Fichier eggs.json introuvable", value="error")]

    current_lower = current.lower()
    suggestions = []

    for egg in all_eggs:
        name = egg.get("name", "Unknown")
        identifier = egg.get("identifier", "")
        rarity = egg.get("rarity", "")
        price = egg.get("base_value", 0)

        if current_lower in name.lower() or current_lower in identifier.lower():
            emoji = {
                "Common": "🟢", "Uncommon": "🔵", "Rare": "🟣",
                "Epic": "🟠", "Legendary": "🟡", "Mythical": "🔴",
                "Divine": "✨"
            }.get(rarity, "🥚")

            display = f"{emoji} {name}"
            if rarity: display += f" ({rarity})"
            if price: display += f" - {price}"

            value = identifier if identifier else name.lower()
            suggestions.append(app_commands.Choice(name=display[:100], value=value))

    return suggestions[:25]

@bot.tree.command(
    name="list_egg_roles",
    description="Affiche tous les œufs configurés avec leurs rôles"
)
async def list_egg_roles(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    try:
        if not os.path.exists("egg_roles.json"):
            await interaction.followup.send("❌ Aucun œuf configuré.", ephemeral=True)
            return

        with open("egg_roles.json", "r", encoding="utf-8") as f:
            egg_roles = json.load(f)

        guild_id = str(interaction.guild_id)
        if guild_id not in egg_roles or not egg_roles[guild_id]:
            await interaction.followup.send("❌ Aucun œuf configuré pour ce serveur.", ephemeral=True)
            return

        with open("eggs.json", "r", encoding="utf-8") as f:
            all_eggs = json.load(f)
            eggs_by_id = {
                egg.get("identifier", egg["name"].lower()): egg
                for egg in all_eggs
            }

        embed = discord.Embed(
            title="🥚 Œufs configurés",
            description="Liste des œufs avec leurs rôles associés",
            color=0x4CAF50
        )

        for egg_key, role_id in egg_roles[guild_id].items():
            egg = eggs_by_id.get(egg_key, {})
            name = egg.get("name", egg_key.title())
            rarity = egg.get("rarity", "Unknown")
            price = egg.get("base_value", "Inconnu")
            role = interaction.guild.get_role(role_id)
            role_mention = role.mention if role else f"❌ (ID: {role_id})"

            emoji = {
                "Common": "🟢", "Uncommon": "🔵", "Rare": "🟣",
                "Epic": "🟠", "Legendary": "🟡", "Mythical": "🔴",
                "Divine": "✨"
            }.get(rarity, "🥚")

            embed.add_field(
                name=f"{emoji} {name}",
                value=f"Rôle: {role_mention}\nValeur: {price}",
                inline=False
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

    except Exception as e:
        await interaction.followup.send(f"❌ Erreur : {str(e)}", ephemeral=True)

@bot.tree.command(
    name="remove_egg_role",
    description="Supprime l'association d'un œuf avec un rôle"
)
@app_commands.describe(egg="Nom de l'œuf à supprimer")
async def remove_egg_role(interaction: discord.Interaction, egg: str):
    await interaction.response.defer(ephemeral=True)

    try:
        if not os.path.exists("egg_roles.json"):
            await interaction.followup.send("❌ Aucun œuf configuré.", ephemeral=True)
            return

        with open("egg_roles.json", "r", encoding="utf-8") as f:
            egg_roles = json.load(f)

        guild_id = str(interaction.guild_id)
        egg_key = egg.lower().strip()

        if guild_id not in egg_roles or egg_key not in egg_roles[guild_id]:
            await interaction.followup.send(f"❌ L'œuf **{egg}** n'est pas configuré.", ephemeral=True)
            return

        del egg_roles[guild_id][egg_key]
        if not egg_roles[guild_id]:
            del egg_roles[guild_id]

        with open("egg_roles.json", "w", encoding="utf-8") as f:
            json.dump(egg_roles, f, ensure_ascii=False, indent=4)

        await interaction.followup.send(f"✅ L'œuf **{egg}** a été supprimé.", ephemeral=True)

    except Exception as e:
        await interaction.followup.send(f"❌ Erreur : {str(e)}", ephemeral=True)
@remove_egg_role.autocomplete("egg")
async def remove_egg_autocomplete(interaction: discord.Interaction, current: str):
    try:
        with open("egg_roles.json", "r", encoding="utf-8") as f:
            egg_roles = json.load(f)

        guild_id = str(interaction.guild_id)
        if guild_id not in egg_roles:
            return []

        configured_eggs = egg_roles[guild_id].keys()

        try:
            with open("eggs.json", "r", encoding="utf-8") as f:
                all_eggs = json.load(f)
                egg_info = {
                    egg.get("identifier", egg["name"].lower()): egg for egg in all_eggs
                }
        except:
            egg_info = {}

        suggestions = []
        current_lower = current.lower()

        for egg_key in configured_eggs:
            egg = egg_info.get(egg_key, {})
            name = egg.get("name", egg_key.title())
            if current_lower in name.lower() or current_lower in egg_key:
                rarity = egg.get("rarity", "")
                emoji = {
                    "Common": "🟢", "Uncommon": "🔵", "Rare": "🟣",
                    "Epic": "🟠", "Legendary": "🟡", "Mythical": "🔴",
                    "Divine": "✨"
                }.get(rarity, "🥚")

                suggestions.append(app_commands.Choice(name=f"{emoji} {name}", value=egg_key))

        return suggestions[:25]

    except Exception as e:
        return [app_commands.Choice(name=f"❌ Erreur : {str(e)}", value="error")]


# Démarrage du bot et le serveur web
subprocess.run(['python', '-m', 'playwright', 'install']) #pour la cloud version
delay = 3000 / 1000  # Convertir millisecondes en secondes
time.sleep(delay)  # Pause de 3 secondes
Yui.alive()
bot.run(TOKEN)
