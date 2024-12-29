from playwright.async_api import async_playwright
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

app = Flask('')

class Yui:
    @staticmethod
    async def request(URL):
        async with async_playwright() as p:
            # Lancer le navigateur avec des options pour minimiser la détection
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-extensions",
                    "--disable-gpu",
                    "--no-sandbox",
                    "--disable-popup-blocking",
                    "--disable-web-security",
                    "--log-level=3",
                ]
            )

            # Créer une nouvelle page
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.198 Safari/537.36"
            )
            page = await context.new_page()

            # Désactiver les traces de WebDriver avec du JavaScript
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            """)

            # Charger la page
            await page.goto(URL)

            # Attendre que le contenu dynamique soit chargé
            await page.wait_for_selector('body')  # S'assurer que la page est complètement chargée

            # Récupérer le HTML après exécution du JavaScript
            page_source = await page.content()

            # Fermer le navigateur
            await browser.close()

            # Utilisation de BeautifulSoup pour parser le HTML
            soup = BeautifulSoup(page_source, 'html.parser')
            return soup

    # def request(URL):
    #     # Chemins pour ChromeDriver et Chrome
    #     chrome_driver_path = 'function/chromedriver-win64/chromedriver.exe'  # Remplace par ton chemin ChromeDriver
    #     chrome_path = r'function/chrome-win64/chrome.exe'  # Chemin vers Chrome

    #     # Configuration du driver Chrome
    #     chrome_options = Options()
    #     chrome_options.binary_location = chrome_path  # Utiliser un chemin Chrome personnalisé si nécessaire
    #     chrome_options.add_argument("--headless")  # Exécute le navigateur en mode headless
    #     chrome_options.add_argument("--disable-gpu")
    #     chrome_options.add_argument("--no-sandbox")
    #     chrome_options.add_argument("--disable-dev-shm-usage")
    #     chrome_options.add_argument("--disable-webgl")  # Désactiver WebGL pour éviter les erreurs liées à WebGL
    #     chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Masquer le mode headless
    #     chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")  # User-Agent personnalisé
    #     chrome_options.add_argument("--log-level=3")

    #     # Lancer le service WebDriver avec Chrome
    #     service = Service(executable_path=chrome_driver_path)

    #     # Lancer le service WebDriver avec Chrome
    #     driver = webdriver.Chrome(service=service, options=chrome_options)

    #     # Chargement de la page
    #     driver.get(URL)

    #     # Attendre que la page soit complètement chargée (tu peux ajuster le temps d'attente)
    #     driver.implicitly_wait(10)

    #     # Récupération du contenu HTML de la page
    #     page_source = driver.page_source

    #     # Fermeture du driver
    #     driver.quit()

    #     # Utilisation de BeautifulSoup pour parser le contenu HTML
    #     soup = BeautifulSoup(page_source, 'html.parser')

    #     return soup

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
    
    @app.route('/')
    def lobby():
        return "Infomation de Yui : Frieren est bien en ligne..."
    
    def run():
        app.run(host='0.0.0.0', port=8080)

    def alive():
        t = Thread(target=Yui.run)
        t.start()
        print("Server lance...")