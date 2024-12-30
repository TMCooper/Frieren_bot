import os
import logging
import json
from dotenv import load_dotenv

# class to centralize functions linked to debug

load_dotenv() 
DEV_ID = os.getenv('DEV_ID')

class Mita:
    @staticmethod
    async def debug_game(user_id):
        if int(user_id) == int(DEV_ID):
            # logging.basicConfig(level=logging.DEBUG, filename='debug.log', filemode='w')
            logging.debug("Chemin actuel : %s", os.getcwd())
            try:
                with open('games.json', 'r', encoding='utf-8') as file:
                    content = file.read()
                    logging.debug("Contenu de games.json : %s", content)
                    return True  # Indique que le fichier est présent
            except FileNotFoundError:
                logging.error("Le fichier games.json est introuvable.")
                return False
            except UnicodeDecodeError as e:
                logging.error("Erreur d'encodage lors de la lecture du fichier games.json : %s", str(e))
                return False
            except json.JSONDecodeError as e:
                logging.error("Erreur lors de l'analyse JSON : %s", str(e))
                return False
        else:
            return "Vous n'êtes pas autorisé à effectuer cette action."