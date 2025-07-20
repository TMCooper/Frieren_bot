import random
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

# class bind to all that is of the order of the network and requests

app = Flask('')

class Yui:
    @staticmethod
    async def request(URL):
        async with async_playwright() as p:
            # Liste de User-Agents réalistes
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            ]

            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-extensions",
                    "--disable-gpu",
                    "--no-sandbox",
                    '--disable-infobars',
                    '--start-maximized', # Lancer en plein écran
                    '--disable-dev-shm-usage'
                ]
            )

            # Créer un contexte de navigateur plus humain
            context = await browser.new_context(
                user_agent=random.choice(user_agents), # Utiliser un User-Agent aléatoire
                java_script_enabled=True,
                accept_downloads=True,
                is_mobile=False,
                has_touch=False,
                # Simuler une résolution d'écran courante
                viewport={'width': 1920, 'height': 1080},
                # Emuler une locale
                locale='fr-FR',
                timezone_id='Europe/Paris',
                # Emuler les permissions
                permissions=['geolocation'],
                # Ajouter des headers HTTP réalistes
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Sec-Ch-Ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": '"Windows"',
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1"
                }
            )

            page = await context.new_page()

            # Désactiver les traces de WebDriver de manière plus robuste
            await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            try:
                # Naviguer vers l'URL avec un timeout plus long
                await page.goto(URL, wait_until='domcontentloaded', timeout=60000)

                # Attendre un peu pour simuler un comportement humain
                await page.wait_for_timeout(random.randint(2000, 5000))

                # Récupérer le HTML après exécution du JavaScript
                page_source = await page.content()

            except Exception as e:
                print(f"Erreur lors de la navigation ou de la récupération du contenu : {e}")
                # Prendre une capture d'écran pour le débogage en cas d'erreur
                await page.screenshot(path='error_screenshot.png')
                return None
            finally:
                # Fermer le navigateur
                await browser.close()

            # Utilisation de BeautifulSoup pour parser le HTML
            soup = BeautifulSoup(page_source, 'html.parser')
            return soup

    async def requet_code(jeu):

        # URL de la page à scraper
        if jeu == "genshin":
            URL = "https://www.jeuxvideo.com/news/1880539/codes-genshin-impact-primo-gemmes-tous-les-redeem-codes-actifs-en-mai-2024.htm"
        
        elif jeu == "hsr":
            URL = "https://www.jeuxvideo.com/news/1875084/codes-honkai-star-rail-jades-stellaires-guides-du-voyageur-tous-les-codes-actifs-du-mois-d-avril-2024.htm"

        soup = await Yui.request(URL)

        links = soup.find_all('li')

        return links

    def valorant_request(pseudo, tag):
        # URL de la page à scraper
        URL = f"https://tracker.gg/valorant/profile/riot/{pseudo}%23{tag}/overview"
        soup = Yui.request(URL)

        return soup
    
    async def ping_waifu():
        URL = "https://mywaifulist.moe/random"
        soup = await Yui.request(URL)
        
        return soup
    
    async def ping_voiranime_catalogue(URL):
        soup = await Yui.request(URL)
        
        return soup

    @app.route('/')
    def home():
        return "Infomation de Yui : Frieren est bien en ligne..."

    def run():
        app.run(host='0.0.0.0', port=8080)

    def alive():
        t = Thread(target=Yui.run)
        t.start()
        print("Server lance...")
        