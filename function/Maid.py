from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

class Maid:
    def scrap():
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

        # Lancer le service WebDriver avec Chrome
        service = Service(executable_path=chrome_driver_path)

        # Lancer le service WebDriver avec Chrome
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # URL de la page à scraper
        URL = "https://www.jeuxvideo.com/news/1875084/codes-honkai-star-rail-jades-stellaires-guides-du-voyageur-tous-les-codes-actifs-du-mois-d-avril-2024.htm"

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

        # Trouver tous les liens
        links = soup.find_all('li')
        # print(links)

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