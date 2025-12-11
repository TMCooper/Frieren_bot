import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
import platform
import psutil # type: ignore
import datetime

from function.Holo import Holo
from function.Mita import Mita
from function.Yui import Yui

class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.DEV_GUILD_ID = int(123456789) # Placeholder, will need to pass this or load env again if needed, but for now I'll assume commands don't need it explicitly unless checking IDs.
        # Actually, refresh_speedrun uses DEV_ID. System commands use mostly Holo functions which might use bot. 
    
    @app_commands.command(name="shutdown", description="down le bot")
    async def shutdown(self, interaction: discord.Interaction):
        await interaction.response.defer()
        msg = await Holo.shutdown(self.bot, interaction.user.id, interaction)
        if msg:
            await interaction.followup.send(msg)

    @app_commands.command(name="reboot", description="redémarre le bot")
    async def reboot(self, interaction: discord.Interaction):
        await interaction.response.defer()
        msg = await Holo.reboot(self.bot, interaction.user.id, interaction)
        if msg:
            await interaction.followup.send(msg)

    @app_commands.command(name="update_bot", description="Update le bot")
    async def update_bot(self, interaction: discord.Interaction):
        await interaction.response.defer()
        msg = await Holo.update(self.bot, interaction.user.id, interaction)
        if msg:
            await interaction.followup.send(msg)

    @app_commands.command(name="status", description="Donne quelque information de base du bot")
    async def status(self, interaction: discord.Interaction):
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

    @app_commands.command(name="info", description="Donne quelque lien utile pour le bot")
    async def info(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = discord.Embed(
            title="Informations utiles",
            description="Liens utiles pour accéder au dashboard du bot",
            color=discord.Color.blue()
        )
        embed.add_field(name="Documentation", value="https://github.com/TMCooper/Frieren_bot")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="dashboard", description="Donne quelque lien pour accéder au dashboard du bot")
    async def dashboard(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = discord.Embed(
            title="Dashboard du bot",
            description="Liens utiles pour le dashboard du bot",
            color=discord.Color.blue()
        )
        embed.add_field(name="Dashboard localhost du bot", value="http://127.0.0.1:8080/")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="games_file", description="Vérifie si le fichier des jeux est accessible.")
    async def games_file(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_id = interaction.user.id
        games_file_exists = await Mita.debug_game(user_id)
        if games_file_exists is True:
            await interaction.followup.send("Le fichier des jeux est accessible.")
        elif games_file_exists is False:
            await interaction.followup.send("Le fichier des jeux est introuvable ou illisible.")
        else:
            await interaction.followup.send(games_file_exists)

    @app_commands.command(name="ping_url", description="Ping lien de votre choix")
    @app_commands.describe(url="Url de votre choix")
    async def ping_url(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer()
        reponse = await Yui.simpleRequest(url)
        await interaction.followup.send(reponse)

    @app_commands.command(name="ping", description="Donne la latence du bot")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Pong ! {round(self.bot.latency * 1000)}ms")

    @app_commands.command(name="list_roles", description="Liste tous les rôles et leurs IDs")
    async def list_roles(self, interaction: discord.Interaction):
        await interaction.response.defer()
        guild = interaction.guild
        roles_info = []
        for role in guild.roles:
            if role.name != "@everyone":
                mentionable = "✅" if role.mentionable else "❌"
                roles_info.append(f"{mentionable} **{role.name}** - ID: `{role.id}`")
        if len(roles_info) > 20:
            roles_info = roles_info[:20] + [f"... et {len(guild.roles) - 21} autres rôles"]
        embed = discord.Embed(
            title="📋 Liste des rôles",
            description="\n".join(roles_info),
            color=0x0099FF
        )
        embed.set_footer(text="✅ = Mentionnable, ❌ = Non mentionnable")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="changestatus", description="Change le status du bot")
    @app_commands.describe(status="Satus disponible : ")
    @app_commands.choices(status=[
        app_commands.Choice(name="Online", value="online"),
        app_commands.Choice(name="Offline", value="offline"),
        app_commands.Choice(name="Ne pas déranger", value="do_not_disturb"),
        app_commands.Choice(name="Inactif", value="idle")
    ])
    async def changeStatus(self, interaction: discord.Interaction, status: app_commands.Choice[str]):
        await interaction.response.defer()
        await Holo.changeStatus(status.value, self.bot)
        await interaction.followup.send(f'Status changer avec succès vers : {status.name}')

    @app_commands.command(name="changeactivity", description="Change l'activité du bot")
    @app_commands.describe(activite="Activité disponible : ")
    @app_commands.choices(activite=[
        app_commands.Choice(name="Joue", value="playing"),
        app_commands.Choice(name="Stream", value="streaming"),
        app_commands.Choice(name="Ecoute", value="listening"),
        app_commands.Choice(name="Compétition", value="competing"),
        app_commands.Choice(name="Regarde", value="watching") 
    ])
    @app_commands.describe(nom="Nom", stream_url="Url du stream")
    async def changeActivity(self, interaction: discord.Interaction, activite: app_commands.Choice[str], nom: str, stream_url: Optional[str] = None):
        await interaction.response.defer()
        await Holo.changeActivity(interaction, activite, nom, stream_url, self.bot)

async def setup(bot):
    await bot.add_cog(System(bot))
