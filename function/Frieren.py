from function.Cardinal import Cardinal
from function.Maid import Maid
import os
from dotenv import load_dotenv

# class to centralize functions linked to speedrun

load_dotenv() 
DEV_ID = os.getenv('DEV_ID')

class Frieren:
    @staticmethod
    async def speedrun_main(jeu):
        # Charger les jeux depuis le fichier
        games = await Cardinal.load_games_from_file()
        if games == "None":
            return"None"

        # Exemple de recherche de jeu
        response = await Maid.speedrun_scrap(jeu, games)

        return response
    
    async def speedrun_refresh(user_id):
        if int(user_id) == int(DEV_ID):
            # Scraper les jeux et les sauvegarder dans un fichier
            games = await Cardinal.get_all_games()
            await Cardinal.save_games_to_file(games)
            return("Actualisation des jeux terminée.")
        else:
            return("Vous n'êtes pas autorisé à effectuer cette action.")