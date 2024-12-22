from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

class Yui:
    def request(URL):
        # Chemins pour ChromeDriver et Chrome
        chrome_driver_path = 'function/chromedriver-win64/chromedriver.exe'  # Remplace par ton chemin ChromeDriver
        chrome_path = r'function/chrome-win64/chrome.exe'  # Chemin vers Chrome

        # Configuration du driver Chrome
        chrome_options = Options()
        chrome_options.binary_location = chrome_path  # Utiliser un chemin Chrome personnalisé si nécessaire
        chrome_options.add_argument("--headless")  # Exécute le navigateur en mode headless
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-webgl")  # Désactiver WebGL pour éviter les erreurs liées à WebGL
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Masquer le mode headless
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")  # User-Agent personnalisé
        chrome_options.add_argument("--log-level=3")

        # Lancer le service WebDriver avec Chrome
        service = Service(executable_path=chrome_driver_path)

        # Lancer le service WebDriver avec Chrome
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Chargement de la page
        driver.get(URL)

        # Attendre que la page soit complètement chargée (tu peux ajuster le temps d'attente)
        driver.implicitly_wait(10)

        # Récupération du contenu HTML de la page
        page_source = driver.page_source

        # Fermeture du driver
        driver.quit()

        # Utilisation de BeautifulSoup pour parser le contenu HTML
        soup = BeautifulSoup(page_source, 'html.parser')

        return soup

    def requet_code(jeu):

        # URL de la page à scraper
        if jeu == "genshin":
            URL = "https://www.jeuxvideo.com/news/1880539/codes-genshin-impact-primo-gemmes-tous-les-redeem-codes-actifs-en-mai-2024.htm"
        
        elif jeu == "hsr":
            URL = "https://www.jeuxvideo.com/news/1875084/codes-honkai-star-rail-jades-stellaires-guides-du-voyageur-tous-les-codes-actifs-du-mois-d-avril-2024.htm"

        soup = Yui.request(URL)

        links = soup.find_all('li')

        return links

    def valorant_request(pseudo, tag):
        # URL de la page à scraper
        URL = f"https://tracker.gg/valorant/profile/riot/{pseudo}%23{tag}/overview"
        soup = Yui.request(URL)

        return soup
    
    def ping_waifu():

        URL = "https://mywaifulist.moe/random"
        soup = Yui.request(URL)
        
        return soup