from function.Yui import Yui
from playwright.async_api import async_playwright
import logging

# class linked to all that is scraping

class Maid:
    async def scrap(jeu):
        links = await Yui.requet_code(jeu)
        codes = []
        # Extraire le texte de chaque lien et chercher le code
        for link in links:
            # Vérifie si l'élément contient un attribut href
            href = link.find('a', href=True)
            if href and 'gift?code=' in href['href']:
                # Extraire le code depuis l'attribut href
                code = href['href'].split('gift?code=')[1].split('&')[0]
                codes.append(code)
            elif 'gift?code=' in link.get_text():
                # Extraire le code depuis le texte brut
                code = link.get_text().split('gift?code=')[1].split('&')[0]
                codes.append(code)

        code_syntax = []
        code_syntax.append("Liste sous forme de tableau :")
        code_syntax.append("+----+-------------------+")
        code_syntax.append("| #  | Code              |")
        code_syntax.append("+----+-------------------+")
        for i, code in enumerate(codes, 1):
            code_syntax.append(f"| {i:<2} | {code:<17} |")
        code_syntax.append("+----+-------------------+")

        # Joindre toutes les lignes avec des sauts de ligne
        table = "\n".join(code_syntax)
        code_discord_version = f"```\n{table}\n```"

        # Encapsuler dans des balises Markdown
        return code_discord_version
    
    async def valorant_tracker_rank(pseudo, tag):
        soup = await Yui.valorant_request(pseudo, tag)
        stat_value = soup.find('span', class_='stat__value')
        if stat_value:
            rank = stat_value.get_text(strip=True)
            return rank
        else:
            return "Rank not found"

    @staticmethod
    async def speedrun_scrap(jeu, games):
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
        
        # Parcours des jeux pour trouver celui correspondant
        for game in games:
            if game["title"].lower() == jeu.lower():
                game_url = game["link"]
                
                try:
                    async with async_playwright() as p:
                        # Lancer le navigateur
                        browser = await p.chromium.launch(headless=True)
                        page = await browser.new_page()

                        # Accéder à la page du jeu
                        await page.goto(game_url)

                        # Attendre que la page soit complètement chargée
                        await page.wait_for_timeout(3000)  # Attente de 3 secondes

                        try:
                            # Chercher plusieurs variations de texte pour le bouton de consentement
                            consent_button = await page.query_selector('button:has-text("Accepter")') or await page.query_selector('button:has-text("J\'ACCEPTE")')

                            # Si un bouton est trouvé, essayer de cliquer dessus
                            if consent_button:
                                await consent_button.click()
                                logging.info('Fenêtre de consentement fermée.')
                            else:
                                logging.info('Aucune fenêtre de consentement trouvée.')

                        except Exception as e:
                            logging.warning(f"Erreur lors de la fermeture de la fenêtre de consentement: {str(e)}")

                        # Extraire l'image de couverture
                        game_img_url = await page.get_attribute('img.object-cover', 'src')
                        if not game_img_url:
                            game_img_url = "Image non trouvée"

                        # Reconstituer l'URL de l'image si elle est relative
                        if game_img_url.startswith('/'):
                            game_img_url = f"https://www.speedrun.com{game_img_url}"

                        # Chercher le bouton correspondant à "Any%" et cliquer dessus
                        any_percent_button = await page.query_selector('button:has-text("Any%")')
                        
                        if any_percent_button:
                            await any_percent_button.click()
                            logging.info('Clic sur le bouton "Any%" effectué.')

                            # Attendre que la page soit actualisée
                            await page.wait_for_timeout(3000)

                            # Extraire les résultats des top 3 joueurs
                            results = []
                            rows = await page.query_selector_all('tr.cursor-pointer')
                            for row in rows[:3]:  # Limiter aux 3 premiers résultats
                                rank_img = await row.query_selector('td img[alt]')
                                rank = await rank_img.get_attribute('alt') if rank_img else "N/A"
                                
                                player_link = await row.query_selector('a.x-username')
                                player_name = await player_link.inner_text() if player_link else "N/A"
                                
                                country_img = await player_link.query_selector('img[alt]') if player_link else None
                                country = await country_img.get_attribute('alt') if country_img else "N/A"
                                
                                time_link = await row.query_selector('a[href*="runs"] span span span span')
                                time = await time_link.inner_text() if time_link else "N/A"
                                
                                date_span = await row.query_selector('.x-timestamp')
                                date = await date_span.inner_text() if date_span else "N/A"
                                
                                # Ajouter le résultat au tableau
                                results.append({
                                    "Rank": rank,
                                    "Player": player_name,
                                    "Country": country,
                                    "Time": time,
                                    "Date": date
                                })

                            # Fermer le navigateur après l'extraction des données
                            await browser.close()

                            # Retourner les résultats
                            return {
                                "Image URL": game_img_url,
                                "Top Results": results if results else "Top speedrun non trouvé pour cette catégorie."
                            }
                        else:
                            await browser.close()
                            return "Catégorie 'Any%' non trouvée."

                except Exception as e:
                    logging.error(f"Erreur lors du scraping de la page : {str(e)}")
                    return f"Erreur lors du scraping de la page : {str(e)}"

        return "Jeu non trouvé."

