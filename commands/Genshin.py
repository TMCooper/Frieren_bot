import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import json
import os
import genshin
from function.Maid import Maid

class Genshin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tasks = {} 
        self.channels = {}
        self.user_data_file = "data/genshin_users.json"
        self.user_data = self.load_user_data()

    async def cog_load(self):
        """Lance les tâches automatiques pour tous les utilisateurs enregistrés au démarrage du bot"""
        # On lance l'initialisation dans une tâche séparée pour ne pas bloquer le chargement du bot
        asyncio.create_task(self.initialize_tasks())

    async def initialize_tasks(self):
        # Attendre que le bot soit prêt pour avoir accès aux canaux
        await self.bot.wait_until_ready()
        
        for guild_id, users in self.user_data.items():
            for user_id, data in users.items():
                for game_key in ["GENSHIN", "STARRAIL", "ZZZ"]:
                    if game_key in data:
                        game_type = getattr(genshin.Game, game_key)
                        task_key = f"{guild_id}_{user_id}_{game_key}"
                        if task_key not in self.tasks:
                            self.tasks[task_key] = asyncio.create_task(
                                self.recurring_task(int(guild_id), int(user_id), game_type)
                            )
        print(f"✅ {len(self.tasks)} tâches Genshin/HSR/ZZZ relancées.")

    def load_user_data(self):
        if os.path.exists(self.user_data_file):
            try:
                with open(self.user_data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_user_data(self):
        os.makedirs(os.path.dirname(self.user_data_file), exist_ok=True)
        with open(self.user_data_file, "w", encoding="utf-8") as f:
            json.dump(self.user_data, f, ensure_ascii=False, indent=4)

    async def recurring_task(self, guild_id, user_id, game_type):
        """Tâche récurrente pour un utilisateur et un jeu spécifique"""
        task_key = f"{guild_id}_{user_id}_{game_type.name}"
        while True:
            try:
                # Calculer le temps d'attente jusqu'au prochain intervalle
                wait_seconds, next_time = Maid.get_next_24hours_interval()
                # print(f"[{task_key}] Attente de {wait_seconds:.1f} secondes jusqu'à {next_time.strftime('%H:%M:%S')}")
                
                await asyncio.sleep(wait_seconds)
                
                # Récupérer les données de l'utilisateur
                guild_str = str(guild_id)
                user_str = str(user_id)
                if guild_str not in self.user_data or user_str not in self.user_data[guild_str]:
                    break
                
                data = self.user_data[guild_str][user_str]
                if game_type.name not in data:
                    break
                
                game_data = data[game_type.name]
                
                # Récupérer le canal
                channel_id = data.get("channel_id")
                channel = self.bot.get_channel(channel_id)
                if not channel:
                    break

                # Exécuter le claim
                result = await Maid.claim_daily_reward(
                    game_data["ituid_v2"], 
                    game_data["itoken_v2"], 
                    game_data["uid"], 
                    game=game_type
                )
                
                try:
                    user = await self.bot.fetch_user(user_id)
                    await channel.send(f"🔔 **Rappel Daily - {user.mention}**\n{result}")
                except:
                    await channel.send(f"🔔 **Rappel Daily**\n{result}")
                
            except asyncio.CancelledError:
                print(f"[{task_key}] Tâche annulée")
                break
            except Exception as e:
                print(f"[{task_key}] Erreur : {e}")
                await asyncio.sleep(60)

    async def setup_game(self, interaction, itoken_v2, ituid_v2, uid, game_type):
        guild_id = str(interaction.guild_id)
        user_id = str(interaction.user.id)
        
        await interaction.response.defer(ephemeral=True)
        
        if guild_id not in self.user_data:
            self.user_data[guild_id] = {}
        if user_id not in self.user_data[guild_id]:
            self.user_data[guild_id][user_id] = {"channel_id": interaction.channel_id}
        
        self.user_data[guild_id][user_id][game_type.name] = {
            "itoken_v2": itoken_v2,
            "ituid_v2": ituid_v2,
            "uid": uid
        }
        self.user_data[guild_id][user_id]["channel_id"] = interaction.channel_id
        self.save_user_data()

        task_key = f"{guild_id}_{user_id}_{game_type.name}"
        if task_key in self.tasks and not self.tasks[task_key].cancelled():
            self.tasks[task_key].cancel()
        
        self.tasks[task_key] = asyncio.create_task(self.recurring_task(interaction.guild_id, interaction.user.id, game_type))
        
        # Calculer la prochaine exécution
        wait_seconds, next_time = Maid.get_next_24hours_interval()
        next_time_str = next_time.strftime("%H:%M:%S")
        
        game_name = "Genshin Impact" if game_type == genshin.Game.GENSHIN else "Honkai: Star Rail" if game_type == genshin.Game.STARRAIL else "Zenless Zone Zero"

        await interaction.followup.send(
            f"✅ Configuration réussie pour **{game_name}** !\n"
            f"🕐 Prochaine exécution : {next_time_str}\n"
            f"📺 Canal de notification : {interaction.channel.mention}",
            ephemeral=True
        )

    async def stop_game(self, interaction, game_type):
        guild_id = str(interaction.guild_id)
        user_id = str(interaction.user.id)
        task_key = f"{guild_id}_{user_id}_{game_type.name}"
        
        await interaction.response.defer(ephemeral=True)
        
        if task_key in self.tasks:
            if not self.tasks[task_key].cancelled():
                self.tasks[task_key].cancel()
            del self.tasks[task_key]
        
        if guild_id in self.user_data and user_id in self.user_data[guild_id]:
            if game_type.name in self.user_data[guild_id][user_id]:
                del self.user_data[guild_id][user_id][game_type.name]
                self.save_user_data()
        
        game_name = "Genshin Impact" if game_type == genshin.Game.GENSHIN else "Honkai: Star Rail" if game_type == genshin.Game.STARRAIL else "Zenless Zone Zero"
        await interaction.followup.send(f"✅ Tâche automatique arrêtée pour **{game_name}**.", ephemeral=True)

    async def daily_claim(self, interaction, game_type):
        guild_id = str(interaction.guild_id)
        user_id = str(interaction.user.id)
        
        await interaction.response.defer()
        
        if guild_id not in self.user_data or user_id not in self.user_data[guild_id] or game_type.name not in self.user_data[guild_id][user_id]:
            return await interaction.followup.send("❌ Vous n'avez pas configuré vos accès pour ce jeu. Utilisez `/setup_[jeu]` d'abord.")
        
        data = self.user_data[guild_id][user_id][game_type.name]
        result = await Maid.claim_daily_reward(data["ituid_v2"], data["itoken_v2"], data["uid"], game=game_type)
        await interaction.followup.send(result)

    # --- Commands GENSHIN ---
    @app_commands.command(name="genshin_setup", description="Initialise le claim daily pour Genshin Impact")
    @app_commands.describe(
        itoken_v2="Votre ltoken_v2 (récupéré sur HoYoLAB)", 
        ituid_v2="Votre ltuid_v2 (récupéré sur HoYoLAB)", 
        uid="Votre UID en jeu"
    )
    async def genshin_setup(self, interaction: discord.Interaction, itoken_v2: str, ituid_v2: str, uid: int):
        """Configure le claim auto pour Genshin Impact.
        Tip: Récupérez vos tokens v2 via l'inspecteur d'élément sur hoyolab.com (Cookies: ltoken_v2, ltuid_v2).
        """
        await self.setup_game(interaction, itoken_v2, ituid_v2, uid, genshin.Game.GENSHIN)

    @app_commands.command(name="stop_genshin", description="Arrête le claim automatique pour Genshin Impact")
    async def stop_genshin(self, interaction: discord.Interaction):
        await self.stop_game(interaction, genshin.Game.GENSHIN)

    @app_commands.command(name="daily_genshin", description="Claim manuellement la quotidienne Genshin Impact")
    async def daily_genshin(self, interaction: discord.Interaction):
        await self.daily_claim(interaction, genshin.Game.GENSHIN)

    # --- Commands HSR ---
    @app_commands.command(name="hsr_setup", description="Initialise le claim daily pour Honkai: Star Rail")
    @app_commands.describe(
        itoken_v2="Votre ltoken_v2", 
        ituid_v2="Votre ltuid_v2", 
        uid="Votre UID en jeu"
    )
    async def hsr_setup(self, interaction: discord.Interaction, itoken_v2: str, ituid_v2: str, uid: int):
        await self.setup_game(interaction, itoken_v2, ituid_v2, uid, genshin.Game.STARRAIL)

    @app_commands.command(name="stop_hsr", description="Arrête le claim automatique pour Honkai: Star Rail")
    async def stop_hsr(self, interaction: discord.Interaction):
        await self.stop_game(interaction, genshin.Game.STARRAIL)

    @app_commands.command(name="daily_hsr", description="Claim manuellement la quotidienne Honkai: Star Rail")
    async def daily_hsr(self, interaction: discord.Interaction):
        await self.daily_claim(interaction, genshin.Game.STARRAIL)

    # --- Commands ZZZ ---
    @app_commands.command(name="zzz_setup", description="Initialise le claim daily pour Zenless Zone Zero")
    @app_commands.describe(
        itoken_v2="Votre ltoken_v2", 
        ituid_v2="Votre ltuid_v2", 
        uid="Votre UID en jeu"
    )
    async def zzz_setup(self, interaction: discord.Interaction, itoken_v2: str, ituid_v2: str, uid: int):
        await self.setup_game(interaction, itoken_v2, ituid_v2, uid, genshin.Game.ZZZ)

    @app_commands.command(name="stop_zzz", description="Arrête le claim automatique pour Zenless Zone Zero")
    async def stop_zzz(self, interaction: discord.Interaction):
        await self.stop_game(interaction, genshin.Game.ZZZ)

    @app_commands.command(name="daily_zzz", description="Claim manuellement la quotidienne Zenless Zone Zero")
    async def daily_zzz(self, interaction: discord.Interaction):
        await self.daily_claim(interaction, genshin.Game.ZZZ)

    @app_commands.command(name="genshin_status", description="Affiche vos comptes configurés et leur statut")
    async def genshin_status(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild_id)
        user_id = str(interaction.user.id)
        
        if guild_id not in self.user_data or user_id not in self.user_data[guild_id]:
            return await interaction.response.send_message("❌ Aucun compte configuré.", ephemeral=True)
        
        data = self.user_data[guild_id][user_id]
        embed = discord.Embed(title=f"📊 Statut HoYoLAB - {interaction.user.display_name}", color=0x4CAF50)
        
        games = {
            "GENSHIN": "Genshin Impact",
            "STARRAIL": "Honkai: Star Rail",
            "ZZZ": "Zenless Zone Zero"
        }
        
        for key, name in games.items():
            if key in data:
                task_key = f"{guild_id}_{user_id}_{key}"
                is_active = task_key in self.tasks and not self.tasks[task_key].cancelled()
                status = "🟢 Automatique" if is_active else "⚪ Manuel uniquement"
                embed.add_field(name=name, value=f"UID: {data[key]['uid']}\nStatut: {status}", inline=False)
        
        if data.get("channel_id"):
            channel = self.bot.get_channel(data["channel_id"])
            embed.set_footer(text=f"Notifications dans: #{channel.name if channel else 'Inconnu'}")
            
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Genshin(bot))
