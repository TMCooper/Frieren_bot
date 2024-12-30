import os
import logging

# class link to debugging

class Mita:
    @staticmethod
    def debug_game():
        logging.basicConfig(level=logging.DEBUG, filename='debug.log', filemode='w')

        logging.debug("Chemin actuel : %s", os.getcwd())
        logging.debug("Contenu de games.json :")
        try:
            with open('games.json', 'r') as file:
                logging.debug(file.read())
        except FileNotFoundError:
            logging.error("Le fichier games.json est introuvable.")