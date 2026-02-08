import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import datetime
from function.Maid import Maid
from function.Holo import Holo

class GrowAGarden(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.aga_tasks = {}  # {guild_id: task}
        self.aga_channels = {}  # {guild_id: channel}

    async def aga_recurring_task(self, guild_id):
        """Tâche récurrente pour un serveur spécifique"""
        while True:
            try:
                # Calculer le temps d'attente jusqu'au prochain intervalle
                wait_seconds, next_time = Maid.get_next_5min_interval()
                # print(f"[Guild {guild_id}] Attente de {wait_seconds:.1f} secondes jusqu'à {next_time.strftime('%H:%M:%S')}")
                
                # Attendre jusqu'au prochain intervalle
                await asyncio.sleep(wait_seconds)
                
                # Vérifier que le canal existe encore
                if guild_id not in self.aga_channels:
                    print(f"[Guild {guild_id}] Canal non trouvé, arrêt de la tâche")
                    break
                    
                channel = self.aga_channels[guild_id]
                
                # Vérifier que le canal est encore accessible
                try:
                    await channel.fetch_message(channel.last_message_id) if channel.last_message_id else None
                except:
                    print(f"[Guild {guild_id}] Canal inaccessible, arrêt de la tâche")
                    # Nettoyer les références
                    if guild_id in self.aga_channels:
                        del self.aga_channels[guild_id]
                    if guild_id in self.aga_tasks:
                        del self.aga_tasks[guild_id]
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

    @app_commands.command(name="setup_aga", description="Initialise le market de grow a garden avec envoi automatique toutes les 5 minutes")
    async def setup_aga(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        
        await interaction.response.defer()
        
        # Stocker le canal pour ce serveur spécifique
        self.aga_channels[guild_id] = interaction.channel
        
        try:
            # Arrêter la tâche précédente pour ce serveur si elle existe
            if guild_id in self.aga_tasks and not self.aga_tasks[guild_id].cancelled():
                self.aga_tasks[guild_id].cancel()
                print(f"[Guild {guild_id}] Ancienne tâche AGA arrêtée")
            
            # Démarrer la nouvelle tâche récurrente pour ce serveur
            self.aga_tasks[guild_id] = asyncio.create_task(self.aga_recurring_task(guild_id))
            
            # Calculer la prochaine exécution
            wait_seconds, next_time = Maid.get_next_5min_interval()
            next_time_str = next_time.strftime("%H:%M:%S")
            
            await interaction.followup.send(
                f"✅ Setup AGA terminé pour ce serveur ! Envoi automatique toutes les 5 minutes activé.\n"
                f"🕐 Prochaine exécution : {next_time_str}\n"
                f"📊 Serveurs actifs : {len(self.aga_tasks)}\n"
                f"🍎 Mentions des fruits activées\n"
                f"⚙️ Mentions des gears activées"
            )
            
        except Exception as e:
            print(f"[Guild {guild_id}] Erreur lors du setup AGA: {e}")
            await interaction.followup.send(f"❌ Erreur lors du setup: {e}")

    @app_commands.command(name="imediat_aga", description="Test immédiat du market AGA avec mentions des fruits et gears")
    async def imediat_aga(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            # Note: Maid.shop_aga likely requires data/ paths if it reads JSONs.
            # I am not touching Maid.py, but if it breaks, I'll need to fix it.
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

    @app_commands.command(name="stop_aga", description="Arrête l'envoi automatique du market AGA pour ce serveur")
    async def stop_aga(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        
        await interaction.response.defer()
        
        try:
            # Arrêter la tâche pour ce serveur
            if guild_id in self.aga_tasks:
                if not self.aga_tasks[guild_id].cancelled():
                    self.aga_tasks[guild_id].cancel()
                del self.aga_tasks[guild_id]
                
            # Supprimer le canal stocké
            if guild_id in self.aga_channels:
                del self.aga_channels[guild_id]
                
            await interaction.followup.send(
                f"✅ Tâche AGA arrêtée pour ce serveur.\n"
                f"📊 Serveurs encore actifs : {len(self.aga_tasks)}"
            )
            
        except Exception as e:
            print(f"[Guild {guild_id}] Erreur lors de l'arrêt AGA: {e}")
            await interaction.followup.send(f"❌ Erreur lors de l'arrêt: {e}")

    @app_commands.command(name="status_aga", description="Affiche le statut de l'envoi automatique AGA")
    async def status_aga(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        
        await interaction.response.defer()
        
        # Statut pour ce serveur
        is_active = guild_id in self.aga_tasks and not self.aga_tasks[guild_id].cancelled()
        channel_set = guild_id in self.aga_channels
        
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
        
        embed.add_field(name="Ce serveur", value=status_msg, inline=False)
        embed.add_field(name="Canal configuré", value=f"🟢 {self.aga_channels[guild_id].mention}" if channel_set else "🔴 Aucun", inline=True)
        embed.add_field(name="Total serveurs actifs", value=f"{len(self.aga_tasks)} serveur(s)", inline=True)
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="db_gag_refresh", description="Actualise la base de donnée pour l'autocomplete")
    async def db_gag_refresh(self, interaction: discord.Interaction):
        await interaction.response.defer()
        msg = await Holo.db_gag_refresh(interaction.user.id, interaction)
        if msg:
            await interaction.followup.send(msg)

async def setup(bot):
    await bot.add_cog(GrowAGarden(bot))
