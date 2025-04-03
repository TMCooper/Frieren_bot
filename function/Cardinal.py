import json
import logging
from function.Yui import Yui

# class to manage the folder

class Cardinal:
    @staticmethod
    async def get_all_games():
        base_url = "https://www.speedrun.com/fr-FR/games"
        games = []
        page_number = 1
        max_pages = 50  # Limite de sécurité pour éviter une boucle infinie
        
        try:
            for _ in range(max_pages):
                url = f"{base_url}?page={page_number}"
                soup = await Yui.request(url)
                
                if not soup:
                    logging.warning(f"Aucune donnée reçue pour la page {page_number}")
                    break
                    
                game_links = soup.find_all('a', class_="x-focus-outline")

                if not game_links:
                    logging.info(f"Fin des résultats à la page {page_number}")
                    break

                for link in game_links:
                    try:
                        game_img = link.find('img')
                        if game_img and 'alt' in game_img.attrs:
                            game_name = game_img['alt']
                            game_href = link['href']
                            games.append({"title": game_name, "link": f"https://www.speedrun.com{game_href}"})
                    except Exception as e:
                        logging.error(f"Erreur lors de l'extraction d'un jeu: {str(e)}")
                        continue

                page_number += 1
                
            logging.info(f"Total de {len(games)} jeux récupérés")
            return games
            
        except Exception as e:
            logging.error(f"Erreur dans get_all_games: {str(e)}")
            return []

    @staticmethod
    async def save_games_to_file(games):
        try:
            with open('games.json', 'w', encoding='utf-8') as file:
                json.dump(games, file, ensure_ascii=False, indent=4)
            logging.info(f"Fichier games.json sauvegardé avec {len(games)} jeux")
            return True
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde du fichier: {str(e)}")
            return False

    @staticmethod
    async def load_games_from_file():
        try:
            with open('games.json', 'r', encoding='utf-8') as file:
                games = json.load(file)
            logging.info(f"Fichier games.json chargé avec {len(games)} jeux")
            return games
        except FileNotFoundError:
            logging.warning("Le fichier games.json n'existe pas")
            return "None"
        except json.JSONDecodeError:
            logging.error("Le fichier games.json est corrompu ou mal formaté")
            return "None"
        except Exception as e:
            logging.error(f"Erreur lors du chargement du fichier: {str(e)}")
            return "None"