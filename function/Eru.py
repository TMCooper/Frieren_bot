from function.Yui import Yui

# class juste for the command /waifu to scrap the information we need

class Eru:
    @staticmethod
    async def random_waifu():
        soup = await Yui.ping_waifu()

        # Extraction des informations avec gestion d'éléments manquants
        name_element = soup.find('h1', class_='my-3 text-xl font-bold text-gray-900 dark:text-gray-200')
        name = name_element.text.strip() if name_element else "Nom non trouvé"

        alternate_name = soup.find('span', id='alternate-name')
        alternate_name = alternate_name.text.strip() if alternate_name else "Non disponible"

        age = soup.find('span', id='age')
        age = age.text.strip() if age else "Non précisé"

        # Ajouter les autres éléments de la même manière
        birthday = soup.find('span', id='birthday')
        birthday = birthday.text.strip() if birthday else "Non précisé"

        height = soup.find('span', id='height')
        height = height.text.strip() if height else "Non précisé"

        weight = soup.find('span', id='weight')
        weight = weight.text.strip() if weight else "Non précisé"

        blood_type = soup.find('span', id='blood-type')
        blood_type = blood_type.text.strip() if blood_type else "Non précisé"

        waifu_classification = soup.find('span', id='waifu-classification')
        waifu_classification = waifu_classification.text.strip() if waifu_classification else "Waifu"

        description = soup.find('p', id='description')
        description = description.text.strip() if description else "Non disponible"

        like_rank = soup.find('div', id='like-rank')
        like_rank = like_rank.text.strip() if like_rank else "Non précisé"

        popularity_rank = soup.find('div', id='popularity-rank')
        popularity_rank = popularity_rank.text.strip() if popularity_rank else "Non précisé"

        image_url = soup.find('img', class_='h-full w-full object-cover object-center')
        image_url = image_url['src'] if image_url else "Image non disponible"

        # Vérifier la classification pour éviter les erreurs de classification
        if waifu_classification.lower() in ["husbando"]:
            return await Eru.random_waifu()
        elif waifu_classification == "":
            waifu_classification = "Waifu"

        return name, alternate_name, age, birthday, height, weight, blood_type, waifu_classification, description, like_rank, popularity_rank, image_url
