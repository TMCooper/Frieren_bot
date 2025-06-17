from function.Yui import Yui
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from collections import defaultdict
import time
import datetime
import json
import logging
import discord
import os

load_dotenv()

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
                print(game_url)
                try:
                    async with async_playwright() as p:
                        # Lancer le navigateur
                        browser = await p.chromium.launch(headless=True)
                        page = await browser.new_page()

                        # Accéder à la page du jeu
                        await page.goto(game_url)

                        # Attendre que la page soit complètement chargée
                        await page.wait_for_load_state("networkidle", timeout=10000)
                        
                        # Nouvelle méthode améliorée pour gérer le popup de consentement
                        try:
                            # Vérifier si le popup spécifique de Quantcast est présent
                            consent_popup = page.locator('div#qc-cmp2-container')
                            is_visible = await consent_popup.is_visible(timeout=3000)
                            
                            if is_visible:
                                # Essayer plusieurs sélecteurs pour le bouton d'acceptation
                                selectors = [
                                    'button.qc-cmp2-button-primary', 
                                    'button[mode="primary"]',
                                    'button:has-text("Accepter")',
                                    'button:has-text("J\'ACCEPTE")',
                                    'button:has-text("Accept")',
                                    'button:has-text("ACCEPT")',
                                    'button:has-text("Agree")'
                                ]
                                
                                for selector in selectors:
                                    try:
                                        consent_button = page.locator(selector).first
                                        if await consent_button.is_visible(timeout=1000):
                                            # Utiliser JavaScript pour cliquer (plus fiable)
                                            await page.evaluate(f'document.querySelector("{selector}").click()')
                                            logging.info(f'Fenêtre de consentement fermée via {selector}')
                                            
                                            # Attendre que le popup disparaisse
                                            await page.wait_for_timeout(2000)
                                            break
                                    except Exception as e:
                                        continue
                                        
                                # Si toujours visible, essayer de cliquer sur le conteneur principal
                                if await consent_popup.is_visible(timeout=1000):
                                    # Essayer de fermer en utilisant JavaScript pour cibler l'élément exact
                                    await page.evaluate('''() => {
                                        const buttons = document.querySelectorAll('#qc-cmp2-container button');
                                        for (let btn of buttons) {
                                            if (btn.textContent.includes('Accept') || 
                                                btn.textContent.includes('Accepter') || 
                                                btn.textContent.includes('Agree')) {
                                                btn.click();
                                                break;
                                            }
                                        }
                                    }''')
                                    logging.info('Tentative JavaScript pour fermer le popup')
                                    await page.wait_for_timeout(2000)
                        except Exception as e:
                            logging.warning(f"Erreur lors de la gestion de la fenêtre de consentement: {str(e)}")

                        # Continuer avec le reste du code...
                        # Extraire l'image de couverture
                        try:
                            game_img_url = await page.get_attribute('img.object-cover', 'src')
                            if not game_img_url:
                                game_img_url = "Image non trouvée"

                            # Reconstituer l'URL de l'image si elle est relative
                            if game_img_url and game_img_url.startswith('/'):
                                game_img_url = f"https://www.speedrun.com{game_img_url}"
                        except Exception as e:
                            logging.warning(f"Erreur lors de l'extraction de l'image: {str(e)}")
                            game_img_url = "Image non trouvée"

                        # Chercher le bouton correspondant à "Any%" et cliquer dessus
                        try:
                            # Essayer de trouver le bouton Any% avec différentes approches
                            any_percent_button = None
                            selectors = [
                                'button:has-text("Any%")',
                                'button:text("Any%")',
                                'a:has-text("Any%")'
                            ]
                            
                            for selector in selectors:
                                any_percent_button = await page.query_selector(selector)
                                if any_percent_button:
                                    # Essayer d'abord un clic normal
                                    try:
                                        await any_percent_button.click(timeout=5000)
                                        logging.info(f'Clic sur le bouton "Any%" effectué via {selector}')
                                        break
                                    except Exception:
                                        # Si le clic normal échoue, essayer avec force
                                        try:
                                            await page.evaluate('(element) => element.click()', any_percent_button)
                                            logging.info('Clic JavaScript sur le bouton "Any%" effectué')
                                            break
                                        except Exception as e:
                                            logging.warning(f"Échec du clic JavaScript: {str(e)}")
                                            continue
                            
                            if any_percent_button:
                                # Attendre que la page soit actualisée
                                await page.wait_for_timeout(5000)

                                # Prendre une capture d'écran pour le débogage si nécessaire
                                await page.screenshot(path=f"speedrun_debug_{jeu.replace(' ', '_')}.png")

                                # Extraire les résultats des top 3 joueurs
                                # [Reste du code inchangé]
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
                            # Prendre une capture d'écran pour le débogage
                            await page.screenshot(path=f"speedrun_error_{jeu.replace(' ', '_')}.png")
                            logging.error(f"Erreur lors de la recherche du bouton Any%: {str(e)}")
                            await browser.close()
                            return f"Erreur lors de la recherche de la catégorie Any%: {str(e)}"

                except Exception as e:
                    logging.error(f"Erreur lors du scraping de la page : {str(e)}")
                    return f"Erreur lors du scraping de la page : {str(e)}"

        return "Jeu non trouvé."
    
    async def voiranime_scrap_catalogue(id, interaction):
        if id != int(os.getenv('DEV_ID')):
            return await interaction.response.send_message("Cette commande ne peut être exécutée que par un bot développé pour Voiranime.")
        
        i = 1
        if i == 1:
            await interaction.response.send_message("Actualisation en cours...") 
        
        while True:
            # Boucle infinie pour récupérer les données du catalogue de VoiAnime
            URL = f"https://v6.voiranime.com/liste-danimes/page/{i}"

            # Obtenir le contenu de la page
            soup = await Yui.ping_voiranime_catalogue(URL)

            # Vérifier si la page contient le message "Nothing Found"
            nothing_found = soup.find('h1', class_='page-title', string="Nothing Found")
            if nothing_found:
                print(f"Fin de la pagination atteinte à la page {i}.")
                break

            # Extraire la liste des animes
            titres = soup.find_all('h3', class_='h5')
            images = soup.find_all('img', class_='img-responsive')

            titre_animes = []
            links = []

            # Vérifier si le fichier existe déjà
            anime_file = "anime.json"
            if os.path.exists(anime_file) and os.path.getsize(anime_file) > 0:
                with open(anime_file, "r", encoding="utf-8") as f:
                    try:
                        anime_data = json.load(f)
                    except json.JSONDecodeError:
                        anime_data = []
            else:
                anime_data = []

            for index, titre in enumerate(titres):
                # Extraire le titre de l'anime
                titre_anime = titre.get_text(strip=True)
                titre_animes.append(titre_anime)

                # Extraire le lien de l'anime
                link = titre.find('a', href=True)
                if link:
                    link = link['href']
                    links.append(link)
                else:
                    link = "N/A"

                # Extraire l'image correspondante
                if index < len(images):
                    # Vérifier si l'image a un attribut srcset
                    srcset = images[index].get("srcset", "")
                    if srcset:
                        # Extraire toutes les URLs du srcset
                        srcset_urls = [url.strip().split(" ")[0] for url in srcset.split(",")]
                        # Prendre la dernière URL qui est généralement la plus grande résolution
                        image_url = srcset_urls[-1] if srcset_urls else images[index].get("src", "N/A")
                    else:
                        # Si pas de srcset, utiliser le src par défaut
                        image_url = images[index].get("src", "N/A")
                else:
                    image_url = "N/A"

                # Ajouter les données dans le fichier JSON
                anime_entry = {
                    "anime_name": titre_anime,
                    "lien": link,
                    "image_url": image_url
                }
                anime_data.append(anime_entry)

            # Écrire dans le fichier JSON
            with open(anime_file, "w", encoding="utf-8") as f:
                json.dump(anime_data, f, ensure_ascii=False, indent=4)
            
            i += 1

        return titre_animes, links

    @staticmethod
    async def shop_aga():
        url = "https://growagardenpro.com/stock/"
        soup = await Yui.request(url)
        cleaned_html = soup.body.prettify() if soup.body else soup.prettify()
        soup = BeautifulSoup(cleaned_html, "html.parser")

        # Mapping des catégories avec emojis
        categories = {
            "Seeds": {"name": "Graines", "emoji": "🌱"},
            "Gear": {"name": "Outils", "emoji": "🔧"}, 
            "Eggs": {"name": "Œufs", "emoji": "🥚"},
            "Honey": {"name": "Articles Miel", "emoji": "🍯"},
            "Cosmetics": {"name": "Cosmétiques", "emoji": "✨"},
        }

        stock_by_category = {key: [] for key in categories}

        # Parsing du contenu (même logique que l'original)
        for section in soup.find_all("h2"):
            section_name = section.get_text(strip=True)
            parent_div = section.find_parent("div", class_="bg-[rgb(72,32,14)]")
            if not parent_div:
                continue

            for key in categories:
                if key.lower() in section_name.lower():
                    for item in parent_div.select(".card-hover"):
                        try:
                            rarity_div = item.select_one(".border.text-xs")
                            rarity = rarity_div.get_text(strip=True).capitalize() if rarity_div else "?"

                            name_tag = item.find("h3")
                            name = name_tag.get_text(strip=True) if name_tag else "Unknown"

                            stock_tag = item.find(string=lambda x: x and "Stock:" in x)
                            stock = int(stock_tag.strip().split("x")[-1]) if stock_tag else 0

                            stock_by_category[key].append({
                                "name": name,
                                "stock": stock,
                                "rarity": rarity,
                            })
                        except Exception:
                            continue

        # Création de l'embed
        embed = discord.Embed(
            title="🌱 Grow A Garden - Market",
            description="Boutique disponible dans le jeu",
            color=0x4CAF50,  # Vert nature
            timestamp=datetime.datetime.utcnow()
        )

        # Dernière mise à jour
        now = datetime.datetime.utcnow()
        embed.add_field(
            name="📅 Dernière mise à jour",
            value=f"{now.strftime('%d/%m/%Y à %H:%M')} UTC",
            inline=False
        )

        # Création des colonnes (2 par ligne pour un affichage compact)
        categories_items = [(key, data, stock_by_category[key]) for key, data in categories.items() if stock_by_category[key]]
        
        # Traitement par paires pour avoir 2 colonnes
        for i in range(0, len(categories_items), 2):
            # Première colonne
            cat_key1, cat_data1, items1 = categories_items[i]
            items1.sort(key=lambda x: x["stock"], reverse=True)
            
            emoji1 = cat_data1["emoji"]
            name1 = cat_data1["name"]
            total1 = sum(item['stock'] for item in items1)
            
            items_list1 = []
            for item in items1:
                items_list1.append(f"{emoji1} **{item['name']}** - x{item['stock']}")
            
            field1_value = "\n".join(items_list1)
            
            # Deuxième colonne (si elle existe)
            field2_name = "\u200b"  # Field vide par défaut
            field2_value = "\u200b"
            
            if i + 1 < len(categories_items):
                cat_key2, cat_data2, items2 = categories_items[i + 1]
                items2.sort(key=lambda x: x["stock"], reverse=True)
                
                emoji2 = cat_data2["emoji"]
                name2 = cat_data2["name"]
                total2 = sum(item['stock'] for item in items2)
                
                items_list2 = []
                for item in items2:
                    items_list2.append(f"{emoji2} **{item['name']}** - x{item['stock']}")
                
                field2_name = f"{emoji2} **{name2} (Total: {total2})**"
                field2_value = "\n".join(items_list2)
            
            # Ajout des fields
            embed.add_field(
                name=f"{emoji1} **{name1} (Total: {total1})**",
                value=field1_value,
                inline=True
            )
            embed.add_field(
                name=field2_name,
                value=field2_value,
                inline=True
            )
            # Field vide pour forcer le retour à la ligne
            embed.add_field(name="\u200b", value="\u200b", inline=True)

        # Résumé final
        total_items = sum(sum(item['stock'] for item in items) for items in stock_by_category.values())
        active_categories = sum(1 for items in stock_by_category.values() if items)
        
        embed.add_field(
            name="📊 Résumé",
            value=f"**Total général:** {total_items} items\n**Catégories actives:** {active_categories}",
            inline=False
        )

        # Footer
        embed.set_footer(text="Mise à jour automatique toutes les 5 minutes • Hier à 22:30")
        
        return embed

        
    def get_next_5min_interval():
        """Calcule le temps d'attente jusqu'au prochain multiple de 5 minutes + 30 secondes de buffer"""
        now = datetime.datetime.now()
        
        # Calculer la prochaine heure qui est un multiple de 5 minutes
        minutes = now.minute
        next_minute = ((minutes // 5) + 1) * 5
        
        if next_minute >= 60:
            # Si on dépasse 60 minutes, passer à l'heure suivante
            next_time = now.replace(hour=now.hour + 1, minute=0, second=0, microsecond=0)
            if next_time.hour >= 24:
                next_time = next_time.replace(hour=0) + datetime.timedelta(days=1)
        else:
            next_time = now.replace(minute=next_minute, second=0, microsecond=0)
        
        # Ajouter 30 secondes de buffer pour être sûr que l'API soit mise à jour
        next_time += datetime.timedelta(seconds=150)
        
        # Calculer le temps d'attente en secondes
        wait_seconds = (next_time - now).total_seconds()
        return wait_seconds, next_time