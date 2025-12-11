import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from function.Maid import Maid

class Genshin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.genshin_taks = {} # Sic: original variable name typo preserved
        self.genshin_channels = {}

    async def genshin_recurring_task(self, guild_id, itoken_v2, ituid_v2, uid):
        """Tâche récurrente pour un serveur spécifique"""
        while True:
            try:
                # Calculer le temps d'attente jusqu'au prochain intervalle
                wait_seconds, next_time = Maid.get_next_24hours_interval()
                print(f"[Guild {guild_id}] Attente de {wait_seconds:.1f} secondes jusqu'à {next_time.strftime('%H:%M:%S')}")
                
                # Attendre jusqu'au prochain intervalle
                await asyncio.sleep(wait_seconds)
                
                # Vérifier que le canal existe encore
                if guild_id not in self.genshin_channels:
                    print(f"[Guild {guild_id}] Canal non trouvé, arrêt de la tâche")
                    break
                    
                channel = self.genshin_channels[guild_id]
                
                # Vérifier que le canal est encore accessible
                try:
                    await channel.fetch_message(channel.last_message_id) if channel.last_message_id else None
                except:
                    print(f"[Guild {guild_id}] Canal inaccessible, arrêt de la tâche")
                    # Nettoyer les références
                    if guild_id in self.genshin_channels:
                        del self.genshin_channels[guild_id]
                    if guild_id in self.genshin_taks:
                        del self.genshin_taks[guild_id]
                    break
                
                # Récupérer et envoyer les données
                result = await Maid.genshinCheckIn(itoken_v2, ituid_v2, uid)
                await channel.send(result)
                
            except asyncio.CancelledError:
                print(f"[Guild {guild_id}] Tâche genshin annulée")
                break
            except Exception as e:
                print(f"[Guild {guild_id}] Erreur dans la tâche gensin: {e}")
                await asyncio.sleep(60)

    @app_commands.command(name="genshin_setup", description="Initialise le daily check in pour genshin")
    @app_commands.describe(itoken_v2 ="Votre itoken_v2")
    @app_commands.describe(ituid_v2 ="Votre ituid_v2")
    @app_commands.describe(uid="Votre UID")
    async def genshin_setup(self, interaction: discord.Interaction, itoken_v2: str, ituid_v2: str, uid: int):
        guild_id = interaction.guild_id
        
        await interaction.response.defer()
        
        # Stocker le canal pour ce serveur spécifique
        self.genshin_channels[guild_id] = interaction.channel
        
        try:
            # Arrêter la tâche précédente pour ce serveur si elle existe
            if guild_id in self.genshin_taks and not self.genshin_taks[guild_id].cancelled():
                self.genshin_taks[guild_id].cancel()
                print(f"[Guild {guild_id}] Ancienne tâche genshin arrêtée")
            
            # Démarrer la nouvelle tâche récurrente pour ce serveur
            self.genshin_taks[guild_id] = asyncio.create_task(self.genshin_recurring_task(guild_id, itoken_v2, ituid_v2, uid))
            
            # Calculer la prochaine exécution
            wait_seconds, next_time = Maid.get_next_24hours_interval()
            next_time_str = next_time.strftime("%H:%M:%S")
            
            await interaction.followup.send(
                f"✅ Setup genshin terminé pour ce serveur ! Envoi automatique toutes les 24 heur activé.\n"
                f"🕐 Prochaine exécution : {next_time_str}\n"
                f"📊 Serveurs actifs : {len(self.genshin_taks)}\n"
            )
            
        except Exception as e:
            print(f"[Guild {guild_id}] Erreur lors du setup genshin : {e}")
            await interaction.followup.send(f"❌ Erreur lors du setup: {e}")

    @app_commands.command(name="stop_genshin", description="Arrête le claim automatique des daily genshin pour ce serveur")
    async def stop_genshin(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        await interaction.response.defer()
        try:
            # Arrêter la tâche pour ce serveur
            if guild_id in self.genshin_taks:
                if not self.genshin_taks[guild_id].cancelled():
                    self.genshin_taks[guild_id].cancel()
                del self.genshin_taks[guild_id]
            # Supprimer le canal stocké
            if guild_id in self.genshin_channels:
                del self.genshin_channels[guild_id]
            await interaction.followup.send(
                f"✅ Tâche arrêtée pour ce serveur.\n"
                f"📊 Serveurs encore actifs : {len(self.genshin_taks)}"
            )
        except Exception as e:
            print(f"[Guild {guild_id}] Erreur lors de l'arrêt : {e}")
            await interaction.followup.send(f"❌ Erreur lors de l'arrêt: {e}")

    @app_commands.command(name="status_genshin", description="Affiche le statut de le claim automatique genshin")
    async def status_genshin(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        await interaction.response.defer()
        
        # Statut pour ce serveur
        is_active = guild_id in self.genshin_taks and not self.genshin_taks[guild_id].cancelled()
        channel_set = guild_id in self.genshin_channels
        
        # Prochaine exécution
        if is_active:
            wait_seconds, next_time = Maid.get_next_24hours_interval()
            next_time_str = next_time.strftime("%H:%M:%S")
            status_msg = f"🟢 **Actif** - Prochaine exécution : {next_time_str}"
        else:
            status_msg = "🔴 **Inactif**"
        
        embed = discord.Embed(title="📊 Statut genshin", color=0x4CAF50 if is_active else 0xF44336)
        embed.add_field(name="Ce serveur", value=status_msg, inline=False)
        embed.add_field(name="Canal configuré", value=f"🟢 {self.genshin_channels[guild_id].mention}" if channel_set else "🔴 Aucun", inline=True)
        embed.add_field(name="Total serveurs actifs", value=f"{len(self.genshin_taks)} serveur(s)", inline=True)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="daily_genshin", description="Claim Manuellement la daily genshin")
    @app_commands.describe(itoken_v2 ="Votre itoken_v2")
    @app_commands.describe(ituid_v2 ="Votre ituid_v2")
    @app_commands.describe(uid="Votre UID")
    async def daily_genshin(self, interaction: discord.Interaction, itoken_v2: str, ituid_v2: str, uid: int):
        guild_id = interaction.guild_id
        await interaction.response.defer()
        try:
            result = await Maid.genshinCheckIn(itoken_v2, ituid_v2, uid)
            await interaction.followup.send(result)
        except Exception as e:
            print(f"[Guild {guild_id}] Erreur  : {e}")
            await interaction.followup.send(f"❌ Erreur : {e}")

async def setup(bot):
    await bot.add_cog(Genshin(bot))
