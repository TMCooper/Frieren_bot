import discord
from typing import List

class AnimeView(discord.ui.View):
    def __init__(self, animes: List[dict]):
        super().__init__(timeout=180)  # Timeout après 3 minutes
        
        self.animes = animes
        self.current_page = 0
        self.items_per_page = 10
        self.total_pages = (len(animes) - 1) // self.items_per_page + 1
        
        # Menu déroulant
        self.update_select_menu()
        
    def update_select_menu(self):
        # Retirer l'ancien menu s'il existe
        for item in self.children[:]:
            if isinstance(item, discord.ui.Select):
                self.remove_item(item)
        
        # Calculer les indices pour la page actuelle
        start_idx = self.current_page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.animes))
        
        select = discord.ui.Select(
            placeholder=f"📺 Choisissez un anime (Page {self.current_page + 1}/{self.total_pages})",
            options=[
                discord.SelectOption(
                    label=anime["anime_name"][:100],
                    value=str(i + start_idx),
                    description="🎬 Cliquez pour voir les détails"
                )
                for i, anime in enumerate(self.animes[start_idx:end_idx])
            ]
        )
        
        async def select_callback(interaction: discord.Interaction):
            selected_anime = self.animes[int(select.values[0])]
            
            # Créer un embed plus attractif
            embed = discord.Embed(
                title=f"🎯 {selected_anime['anime_name']}",
                url=selected_anime["lien"],
                color=discord.Color.blue(),
                description="Voici les détails de l'anime que vous avez sélectionné."
            )
            
            # Ajouter l'image si disponible
            if selected_anime.get("image_url"):
                embed.set_thumbnail(url=selected_anime["image_url"])
            
            embed.add_field(
                name="🔗 Lien direct",
                value=f"[Cliquez ici pour regarder]({selected_anime['lien']})",
                inline=False
            )
            
            embed.set_footer(text="VoirAnime - Votre source d'anime en français")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        select.callback = select_callback
        self.add_item(select)
        
        # Ajouter les boutons de navigation si nécessaire
        if self.total_pages > 1:
            # Bouton précédent
            prev_button = discord.ui.Button(
                style=discord.ButtonStyle.gray,
                label="◀",
                disabled=self.current_page == 0,
                custom_id="prev"
            )
            
            # Bouton suivant
            next_button = discord.ui.Button(
                style=discord.ButtonStyle.gray,
                label="▶",
                disabled=self.current_page == self.total_pages - 1,
                custom_id="next"
            )
            
            async def button_callback(interaction: discord.Interaction, direction: int):
                self.current_page = max(0, min(self.current_page + direction, self.total_pages - 1))
                self.update_select_menu()
                await interaction.response.edit_message(view=self)
            
            prev_button.callback = lambda i: button_callback(i, -1)
            next_button.callback = lambda i: button_callback(i, 1)
            
            self.add_item(prev_button)
            self.add_item(next_button)