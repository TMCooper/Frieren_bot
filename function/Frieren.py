from function.Cardinal import Cardinal
from function.Maid import Maid
import os
import logging
from dotenv import load_dotenv

# class to centralize functions linked to speedrun

load_dotenv() 
DEV_ID = os.getenv('DEV_ID')

class Frieren:
    @staticmethod
    async def speedrun_main(jeu):
        try:
            # Charger les jeux depuis le fichier
            games = await Cardinal.load_games_from_file()
            if games == "None":
                return "None"

            # Recherche de jeu et extraction des données
            response = await Maid.speedrun_scrap(jeu, games)
            return response
        except Exception as e:
            logging.error(f"Erreur dans speedrun_main: {str(e)}")
            return f"Erreur lors de la récupération des données: {str(e)}"
    
    @staticmethod
    async def speedrun_refresh(user_id):
        if int(user_id) == int(os.getenv('DEV_ID')):
            try:
                # Scraper les jeux et les sauvegarder dans un fichier
                games = await Cardinal.get_all_games()
                if isinstance(games, list) and len(games) > 0:
                    await Cardinal.save_games_to_file(games)
                    return "Actualisation des jeux terminée. ✅ Nombre de jeux récupérés: " + str(len(games))
                else:
                    return "Erreur: Aucun jeu récupéré."
            except Exception as e:
                logging.error(f"Erreur dans speedrun_refresh: {str(e)}")
                return f"Erreur lors de l'actualisation: {str(e)}"
        else:
            return "Vous n'êtes pas autorisé à effectuer cette action."
        
    