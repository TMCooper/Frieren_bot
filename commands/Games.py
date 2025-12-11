import discord
from discord import app_commands
from discord.ext import commands
import os
import datetime
from function.Maid import Maid
from function.Frieren import Frieren

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.DEV_ID = int(os.getenv('DEV_ID') or 0) # Fallback to 0 if not set, preventing error

    @app_commands.command(name="valorant_rank", description="Donne le rank de l'utilisateur sur valorant")
    @app_commands.describe(pseudo="Le pseudo de l'utilisateur")
    @app_commands.describe(tag="Le tag de l'utilisateur")
    async def valorant_rank(self, interaction: discord.Interaction, pseudo: str, tag: str):
        await interaction.response.defer(ephemeral=True)
        rank = await Maid.valorant_tracker_rank(pseudo, tag)
        await interaction.followup.send(f"Le rank de {pseudo}#{tag} est : {rank}")

    @app_commands.command(name="code", description="Pour obtenir les code d'échange de Genshin ou Honkai star rail")
    @app_commands.describe(jeux_entrer="Le jeu pour lequel vous souhaitez récupérer les codes")
    @app_commands.choices(jeux_entrer=[
        app_commands.Choice(name="Genshin", value="genshin"),
        app_commands.Choice(name="Honkai Star Rail", value="hsr")
    ])
    async def code(self, interaction: discord.Interaction, jeux_entrer: app_commands.Choice[str]):
        jeu = jeux_entrer.value.lower()
        await interaction.response.defer(ephemeral=True)
        code_scrap = await Maid.scrap(jeu)
        await interaction.followup.send(f"Code d'échange : \n{code_scrap}")

    @app_commands.command(name="speedrun", description="Affiche le classement mondial des speedruns Any% pour le jeu de votre choix")
    @app_commands.describe(jeu="Nom du jeu dont vous voulez voir les records")
    async def speedrun(self, interaction: discord.Interaction, jeu: str):
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
                color=discord.Color.gold()
            )

            # Ajout de l'image du jeu avec une taille optimisée
            if 'Image URL' in top_speedrun_data and top_speedrun_data['Image URL'] != "Image non trouvée":
                try:
                    embed.set_thumbnail(url=top_speedrun_data['Image URL'])
                except Exception as e:
                    print(f"Erreur lors de l'ajout de l'image: {str(e)}")

            # Ajout d'informations supplémentaires dans l'en-tête
            embed.add_field(
                name="ℹ️ Informations",
                value="Classement basé sur les meilleurs temps en Any%\nMis à jour via speedrun.com",
                inline=False
            )

            # Création du classement avec des emojis pour les médailles
            if 'Top Results' in top_speedrun_data and isinstance(top_speedrun_data['Top Results'], list):
                medals = {
                    "1": "🥇", "2": "🥈", "3": "🥉",
                    "1er": "🥇", "2ème": "🥈", "3ème": "🥉"
                }
                
                for i, rank in enumerate(top_speedrun_data['Top Results'], 1):
                    rank_display = rank.get('Rank', str(i))
                    medal = medals.get(rank_display, medals.get(str(i), "🎮"))
                    
                    player_name = rank.get('Player', 'Inconnu')
                    country = f"({rank.get('Country', '??')})" if rank.get('Country') != "N/A" else ""
                    time_formatted = f"⏱️ {rank.get('Time', 'Temps inconnu')}"
                    date_formatted = f"📅 {rank.get('Date', 'Date inconnue')}"
                    
                    value_text = (
                        f"👤 **{player_name}** {country}\n"
                        f"{time_formatted}\n"
                        f"{date_formatted}\n"
                        "┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄"
                    )
                    
                    embed.add_field(
                        name=f"{medal} {rank_display if rank_display != 'N/A' else f'{i}ème'} Place",
                        value=value_text,
                        inline=False
                    )
            elif 'Top Results' in top_speedrun_data and isinstance(top_speedrun_data['Top Results'], str):
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

            embed.set_footer(
                text="Données fournies par speedrun.com | Utilisez /speedrun <jeu> pour voir d'autres classements",
                icon_url="https://www.speedrun.com/favicon.ico"
            )
            embed.timestamp = datetime.datetime.now()
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            error_message = f"Une erreur s'est produite lors de la récupération des données: {str(e)}"
            print(error_message)
            await interaction.followup.send(error_message)

    @app_commands.command(name="refresh_speedrun", description="Actualise la base de données des jeux pour les speedruns (Admin seulement)")
    async def refresh_speedrun(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if interaction.user.id == self.DEV_ID:
            try:
                result = await Frieren.speedrun_refresh(interaction.user.id)
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

async def setup(bot):
    await bot.add_cog(Games(bot))
