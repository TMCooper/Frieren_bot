import discord
from discord import app_commands
from discord.ext import commands
from function.Eru import Eru
from function.Rias import Rias

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="waifu", description="Donne une waifu aléatoire")
    async def waifu(self, interaction: discord.Interaction):
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

    @app_commands.command(name="rule34", description="Donne une image rule34 avec les tags choisit")
    @app_commands.describe(tags="Les tags pour la recherche")
    async def rule34(self, interaction: discord.Interaction, tags: str):
        await interaction.response.defer()
        image_url = await Rias.rule34(tags)
        await interaction.followup.send(image_url)

async def setup(bot):
    await bot.add_cog(Fun(bot))
