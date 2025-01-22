import discord
from typing import List

# Class entièrement dedier a la creation d'un petit embed avec un menu déroulant pour afficher des informations sur des animes.
class AnimeView(discord.ui.View):
    def __init__(self, animes: List[dict]):
        super().__init__(timeout=180)  # Timeout après 3 minutes
        
        # Créer le menu déroulant
        select = discord.ui.Select(
            placeholder="Choisissez un anime",
            options=[
                discord.SelectOption(
                    label=anime["anime_name"][:100],  # Discord limite les labels à 100 caractères
                    value=str(i),
                    description="Cliquez pour voir le lien"
                )
                for i, anime in enumerate(animes)
            ]
        )
        
        async def select_callback(interaction: discord.Interaction):
            selected_anime = animes[int(select.values[0])]
            embed = discord.Embed(
                title=selected_anime["anime_name"],
                url=selected_anime["lien"],
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Lien direct",
                value=f"[Cliquez ici pour regarder]({selected_anime['lien']})",
                inline=False
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        select.callback = select_callback
        self.add_item(select)
