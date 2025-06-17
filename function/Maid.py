from function.Yui import Yui
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import time
import datetime
import json
import logging
import discord
import os
from collections import defaultdict

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
    
    async def shop_aga(channel=None):
            """Version automatique de shop_aga qui récupère et traite les données en une seule méthode"""
            try:
                # Récupérer les données API avec Yui.request
                # api_response = await Yui.request("https://growagardenapi.vercel.app/api/stock/GetStock")
                api_response = await Yui.request("http://127.0.0.1:3000/api/stock/GetStock")
                
                # Extraire le JSON du HTML BeautifulSoup si nécessaire
                if hasattr(api_response, 'find'):
                    pre_tag = api_response.find('pre')
                    if pre_tag:
                        json_text = pre_tag.get_text()
                        try:
                            api_data = json.loads(json_text)
                            print("JSON extrait avec succès du HTML")
                        except json.JSONDecodeError as e:
                            print(f"Erreur de parsing JSON: {e}")
                            return "Erreur: JSON malformé de l'API"
                    else:
                        print("Pas de balise <pre> trouvée dans le HTML")
                        return "Erreur: Format HTML inattendu"
                else:
                    api_data = api_response
                
                # Vérifier la structure de l'API et extraire les données
                if 'Data' not in api_data:
                    print("Erreur: Clé 'Data' non trouvée dans la réponse API")
                    return "Erreur: Structure API inattendue"
                
                api_aga = api_data['Data']
                print(f"Données API récupérées: {len(api_aga)} sections")
                
                # Configuration des catégories (mise à jour pour correspondre au nouveau format)
                categories_config = {
                    'seeds': {'name': 'Graines', 'emoji': '🌱', 'default_emoji': '🌱'},
                    'gear': {'name': 'Outils', 'emoji': '🛠️', 'default_emoji': '🛠️'},
                    'egg': {'name': 'Œufs', 'emoji': '🥚', 'default_emoji': '🥚'},
                    'honey': {'name': 'Articles Miel', 'emoji': '🍯', 'default_emoji': '🍯'},
                    'cosmetics': {'name': 'Cosmétiques', 'emoji': '✨', 'default_emoji': '✨'}
                }
                
                def clean_and_group_items(items_list, default_emoji='📦'):
                    """Nettoie et regroupe les items identiques"""
                    if not items_list:
                        return [], 0
                    
                    item_counts = defaultdict(lambda: {'stock': 0, 'emoji': ''})
                    
                    for item in items_list:
                        # Nettoyage des données
                        name = str(item.get('name', 'Unknown')).strip()
                        try:
                            stock = int(item.get('stock', 0))
                        except (ValueError, TypeError):
                            stock = 0
                        
                        if stock > 0:  # Ne traiter que les items avec un stock > 0
                            item_counts[name]['stock'] += stock
                            
                            # Garder le premier emoji trouvé (si disponible)
                            if not item_counts[name]['emoji'] and item.get('emoji'):
                                item_counts[name]['emoji'] = item['emoji']
                    
                    # Convertir en liste finale
                    final_items = []
                    total_count = 0
                    
                    for name, data in item_counts.items():
                        emoji = data['emoji'] or default_emoji
                        final_items.append({
                            'name': name,
                            'stock': data['stock'],
                            'emoji': emoji
                        })
                        total_count += data['stock']
                    
                    # Trier par stock décroissant
                    final_items.sort(key=lambda x: x['stock'], reverse=True)
                    
                    return final_items, total_count
                
                def format_items_text(items, max_length=1024):
                    """Formate la liste d'items en texte pour Discord"""
                    if not items:
                        return "Aucun item disponible"
                    
                    text_lines = []
                    for item in items:
                        line = f"{item['emoji']} **{item['name']}** - x{item['stock']}"
                        text_lines.append(line)
                    
                    full_text = "\n".join(text_lines)
                    
                    # Tronquer si trop long
                    if len(full_text) > max_length:
                        truncated_lines = []
                        current_length = 0
                        for line in text_lines:
                            if current_length + len(line) + 1 > max_length - 20:
                                truncated_lines.append("... (tronqué)")
                                break
                            truncated_lines.append(line)
                            current_length += len(line) + 1
                        full_text = "\n".join(truncated_lines)
                    
                    return full_text
                
                # Créer l'embed principal
                embed = discord.Embed(
                    title="🌱 Grow A Garden - Market",
                    description="Boutique disponible dans le jeu",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.utcnow()
                )
                
                # Ajouter l'information de mise à jour si disponible
                if 'updatedAt' in api_aga:
                    try:
                        # Convertir le timestamp en date lisible
                        updated_timestamp = api_aga['updatedAt'] / 1000  # Convertir de millisecondes
                        updated_date = datetime.datetime.fromtimestamp(updated_timestamp, tz=datetime.timezone.utc)
                        embed.add_field(
                            name="📅 Dernière mise à jour",
                            value=updated_date.strftime("%d/%m/%Y à %H:%M UTC"),
                            inline=False
                        )
                    except (ValueError, TypeError) as e:
                        print(f"Erreur lors du parsing du timestamp: {e}")
                
                # Traitement de toutes les catégories
                grand_total = 0
                categories_processed = 0
                
                for category_key, config in categories_config.items():
                    if category_key in api_aga and api_aga[category_key]:
                        print(f"Traitement de {category_key}...")
                        
                        # Nettoyer et regrouper les items
                        items, total_count = clean_and_group_items(
                            api_aga[category_key], 
                            config['default_emoji']
                        )
                        
                        if items:  # Seulement ajouter si il y a des items
                            formatted_text = format_items_text(items)
                            
                            embed.add_field(
                                name=f"{config['emoji']} {config['name']} (Total: {total_count})",
                                value=formatted_text,
                                inline=True
                            )
                            
                            grand_total += total_count
                            categories_processed += 1
                            print(f"✅ {config['name']}: {len(items)} types d'items, {total_count} total")
                        else:
                            print(f"⚠️ {config['name']}: Aucun item valide trouvé")
                    else:
                        print(f"⚠️ {category_key}: Catégorie vide ou inexistante")
                
                # Ajouter un résumé si on a des données
                if grand_total > 0:
                    embed.add_field(
                        name="📊 Résumé",
                        value=f"**Total général:** {grand_total} items\n**Catégories actives:** {categories_processed}",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="⚠️ Information",
                        value="Aucun item disponible dans la boutique actuellement",
                        inline=False
                    )
                
                embed.set_footer(text="Mise à jour automatique toutes les 5 minutes")
                
                print(f"Embed créé avec {len(embed.fields)} fields - Total: {grand_total} items")
                
                # Envoyer l'embed ou le retourner
                if channel:
                    await channel.send(embed=embed)
                    return f"Embed envoyé dans {channel.mention} - {grand_total} items affichés"
                else:
                    return embed
                    
            except Exception as e:
                error_msg = f"Erreur lors de la récupération des données : {str(e)}"
                print(f"Exception dans shop_aga: {e}")
                import traceback
                traceback.print_exc()
                
                if channel:
                    error_embed = discord.Embed(
                        title="❌ Erreur",
                        description=error_msg,
                        color=discord.Color.red()
                    )
                    await channel.send(embed=embed)
                return error_msg
        
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
        next_time += datetime.timedelta(seconds=30)
        
        # Calculer le temps d'attente en secondes
        wait_seconds = (next_time - now).total_seconds()
        return wait_seconds, next_time