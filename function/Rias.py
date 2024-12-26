import random
from function.Yui import Yui

class Rias:
    @staticmethod
    def rule34_request(tags):
        page = random.randint(1, 100)
        limitation = random.randint(1, 1000)
        BASE_URL = 'http://api.rule34.xxx/'
        url = BASE_URL + f'index.php?page=dapi&s=post&q=index&tags={tags}&limit={limitation}, &pid={page}'

        # https://api.rule34.xxx//index.php?page=dapi&s=post&q=index&tags=creampie+&limit=100&pid=2
        
        soup = Yui.request(url)

        return soup  # Utilise le parser XML

    @staticmethod
    def get_image_url(soup):
            posts = soup.find_all('post')  # Trouver tous les éléments <post>
            if not posts:
                return None
            
            # Sélectionner jusqu'à 5 URLs d'images
            image_urls = []
            for _ in range(min(5, len(posts))):  # Limite au nombre de posts disponibles
                post = random.choice(posts)
                image_url = post.get('file_url')  # Récupérer l'URL de l'image
                if image_url:  # Vérifier que l'URL est valide
                    image_urls.append(image_url)
            
            return image_urls if image_urls else None

    @staticmethod
    def discord_format(url_images, tags):
        formattage = []
        if not url_images:
            return "Aucune image trouvée. 😢"

        formattage = f"Voici les images trouvées avec le(s) tag(s) : {tags}\n\n"
        for i, code in enumerate(url_images, 1):
            formattage += (f"{i:<2} : {code:<17}\n")
        return formattage

    @staticmethod
    def rule34(tags):
        soup = Rias.rule34_request(tags)
        url_images = Rias.get_image_url(soup)
        formatage = Rias.discord_format(url_images, tags)
        return formatage