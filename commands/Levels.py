import discord
from discord import app_commands
from discord.ext import commands
import time, json, os, asyncio
from collections import defaultdict

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = "data/levels.json"
        self.data = self.load_data()
        self.voice_sessions = {}  # {guild_id: {user_id: timestamp}}
        self.spam_cooldowns = defaultdict(list)  # {user_id: [timestamps]}

        # Remplir voice_sessions pour les utilisateurs déjà en vocal au démarrage
        for guild in self.bot.guilds:
            for channel in guild.voice_channels:
                for member in channel.members:
                    if not member.bot:
                        if guild.id not in self.voice_sessions:
                            self.voice_sessions[guild.id] = {}
                        self.voice_sessions[guild.id][member.id] = time.time()
        
        self.bot.loop.create_task(self.voice_xp_loop())
        
    def load_data(self):
        """Load levels data from JSON file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_data(self):
        """Save levels data to JSON file"""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def get_user_data(self, guild_id: int, user_id: int):
        """Get or create user data for a specific guild"""
        guild_id_str = str(guild_id)
        user_id_str = str(user_id)
        
        if guild_id_str not in self.data:
            self.data[guild_id_str] = {}
        
        if user_id_str not in self.data[guild_id_str]:
            self.data[guild_id_str][user_id_str] = {
                "xp": 0,
                "level": 0,
                "total_voice_time": 0,
                "last_xp_time": 0,
                "pending_voice_seconds": 0
            }
        
        return self.data[guild_id_str][user_id_str]
    
    def calculate_xp_for_level(self, level: int) -> int:
        """Calculate total XP needed to reach a specific level"""
        total = 0
        for lvl in range(level):
            total += (lvl * 100) + 100
        return total
    
    def calculate_level_from_xp(self, xp: int) -> int:
        """Calculate level from total XP"""
        level = 0
        total_xp_needed = 0
        
        while True:
            xp_for_next = (level * 100) + 100
            if total_xp_needed + xp_for_next > xp:
                break
            total_xp_needed += xp_for_next
            level += 1
        
        return level
    
    def add_xp(self, guild_id: int, user_id: int, xp_amount: int) -> tuple[int, int, bool]:
        """
        Add XP to user and handle leveling
        Returns: (old_level, new_level, leveled_up)
        """
        user_data = self.get_user_data(guild_id, user_id)
        old_level = user_data["level"]
        user_data["xp"] += xp_amount
        
        # Recalculate level
        new_level = self.calculate_level_from_xp(user_data["xp"])
        user_data["level"] = new_level
        
        self.save_data()
        return old_level, new_level, new_level > old_level
    
    async def voice_xp_loop(self):
        """Distribue automatiquement l'XP pour les utilisateurs en vocal"""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            now = time.time()
            for guild_id, users in self.voice_sessions.items():
                for user_id, last_time in users.items():
                    duration = now - last_time
                    if duration <= 0:
                        continue

                    user_data = self.get_user_data(guild_id, user_id)
                    user_data["total_voice_time"] += duration
                    user_data["pending_voice_seconds"] += duration

                    # Distribuer XP toutes les 5 minutes
                    xp_blocks = int(user_data["pending_voice_seconds"] // 300)
                    if xp_blocks > 0:
                        xp_to_award = xp_blocks * 25
                        user_data["pending_voice_seconds"] %= 300
                        self.add_xp(guild_id, user_id, xp_to_award)

                    # Mettre à jour le timestamp
                    self.voice_sessions[guild_id][user_id] = now

            self.save_data()
            await asyncio.sleep(60)  # Vérifie toutes les 60 secondes

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        user_id = member.id
        guild_id = member.guild.id

        if guild_id not in self.voice_sessions:
            self.voice_sessions[guild_id] = {}

        # L’utilisateur rejoint un canal
        if before.channel is None and after.channel is not None:
            self.voice_sessions[guild_id][user_id] = time.time()

        # L’utilisateur quitte un canal
        if before.channel is not None and after.channel is None:
            if user_id in self.voice_sessions.get(guild_id, {}):
                del self.voice_sessions[guild_id][user_id]


    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Award XP for messages with anti-spam protection"""
        # Ignore bots and DMs
        if message.author.bot or not message.guild:
            return
        
        user_id = message.author.id
        guild_id = message.guild.id
        current_time = time.time()
        
        # Clean old timestamps (older than 3 seconds)
        self.spam_cooldowns[user_id] = [
            ts for ts in self.spam_cooldowns[user_id] 
            if current_time - ts < 3
        ]
        
        # Check spam limit (5 messages in 3 seconds)
        if len(self.spam_cooldowns[user_id]) >= 5:
            return  # No XP for spam
        
        # Add timestamp
        self.spam_cooldowns[user_id].append(current_time)
        
        # Award XP
        old_level, new_level, leveled_up = self.add_xp(guild_id, user_id, 2)
        
        # Optional: Notify on level up
        if leveled_up:
            await message.channel.send(f"{message.author.mention} a atteint le niveau {new_level}!")
    
    @app_commands.command(name="top_xp", description="Affiche le classement XP du serveur")
    async def top_xp(self, interaction: discord.Interaction):
        """Display XP leaderboard for the server"""
        await interaction.response.defer()
        
        guild_id_str = str(interaction.guild_id)
        
        if guild_id_str not in self.data or not self.data[guild_id_str]:
            await interaction.followup.send("Aucune donnée XP pour ce serveur.")
            return
        
        # Sort by level (desc), then by XP (desc)
        leaderboard = sorted(
            self.data[guild_id_str].items(),
            key=lambda x: (x[1]["level"], x[1]["xp"]),
            reverse=True
        )[:10]
        
        embed = discord.Embed(
            title="Classement XP",
            description="Top 10 des membres par niveau",
            color=discord.Color.gold()
        )
        
        for i, (user_id_str, user_data) in enumerate(leaderboard, 1):
            user = interaction.guild.get_member(int(user_id_str))
            if user:
                embed.add_field(
                    name=f"{i}. {user.display_name}",
                    value=f"**Niveau {user_data['level']}** • {user_data['xp']} XP",
                    inline=False
                )
        
        # Set thumbnail to top user's avatar
        if leaderboard:
            top_user = interaction.guild.get_member(int(leaderboard[0][0]))
            if top_user:
                embed.set_thumbnail(url=top_user.display_avatar.url)
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="xp_personnel", description="Affiche vos statistiques XP")
    async def xp_personnel(self, interaction: discord.Interaction):
        """Display personal XP stats"""
        await interaction.response.defer()
        
        user_data = self.get_user_data(interaction.guild_id, interaction.user.id)
        current_level = user_data["level"]
        current_xp = user_data["xp"]
        
        # Calculate XP for current and next level
        xp_for_current_level = self.calculate_xp_for_level(current_level)
        xp_for_next_level = self.calculate_xp_for_level(current_level + 1)
        
        xp_in_current_level = current_xp - xp_for_current_level
        xp_needed_for_next = xp_for_next_level - current_xp
        xp_required_this_level = (current_level * 100) + 100
        
        # Progress bar
        progress = xp_in_current_level / xp_required_this_level
        bar_length = 10
        filled = int(progress * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        embed = discord.Embed(
            title=f"📊 Statistiques de {interaction.user.display_name}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="Niveau", value=f"**{current_level}**", inline=True)
        embed.add_field(name="XP Total", value=f"{current_xp}", inline=True)
        embed.add_field(name="XP pour niveau suivant", value=f"{xp_needed_for_next}", inline=True)
        embed.add_field(
            name="Progression",
            value=f"`{bar}` {int(progress * 100)}%\n{xp_in_current_level}/{xp_required_this_level} XP",
            inline=False
        )
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="top_voc", description="Classement du temps passé en vocal")
    async def top_voc(self, interaction: discord.Interaction):
        await interaction.response.defer()
        guild_id_str = str(interaction.guild_id)

        if guild_id_str not in self.data or not self.data[guild_id_str]:
            await interaction.followup.send("Aucune donnée vocale pour ce serveur.")
            return

        leaderboard = sorted(
            self.data[guild_id_str].items(),
            key=lambda x: x[1]["total_voice_time"],
            reverse=True
        )[:10]

        leaderboard = [(uid, data) for uid, data in leaderboard if data["total_voice_time"] > 0]

        if not leaderboard:
            await interaction.followup.send("Aucune donnée vocale pour le moment.")
            return

        embed = discord.Embed(
            title="Classement Vocal",
            description="Top 10 du temps passé en vocal",
            color=discord.Color.purple()
        )

        for i, (user_id_str, user_data) in enumerate(leaderboard, 1):
            user = interaction.guild.get_member(int(user_id_str))
            if user:
                seconds = int(user_data["total_voice_time"])
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                embed.add_field(
                    name=f"{i}. {user.display_name}",
                    value=f"**{hours}h{minutes:02d}m**",
                    inline=False
                )

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Levels(bot))
