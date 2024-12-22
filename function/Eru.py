from function.Yui import Yui

class Eru:
    def random_waifu():
        soup = Yui.ping_waifu()

        # Extraction des informations
        name = soup.find('h1', class_='my-3 text-xl font-bold text-gray-900 dark:text-gray-200').text.strip()
        alternate_name = soup.find('span', id='alternate-name').text.strip() if soup.find('span', id='alternate-name') else ""
        age = soup.find('span', id='age').text.strip() if soup.find('span', id='age') else ""
        birthday = soup.find('span', id='birthday').text.strip() if soup.find('span', id='birthday') else ""
        height = soup.find('span', id='height').text.strip() if soup.find('span', id='height') else ""
        weight = soup.find('span', id='weight').text.strip() if soup.find('span', id='weight') else ""
        blood_type = soup.find('span', id='blood-type').text.strip() if soup.find('span', id='blood-type') else ""
        waifu_classification = soup.find('span', id='waifu-classification').text.strip() if soup.find('span', id='waifu-classification') else ""
        description = soup.find('p', id='description').text.strip() if soup.find('p', id='description') else ""
        like_rank = soup.find('div', id='like-rank').text.strip() if soup.find('div', id='like-rank') else ""
        popularity_rank = soup.find('div', id='popularity-rank').text.strip() if soup.find('div', id='popularity-rank') else ""
        image_url = soup.find('img', class_='h-full w-full object-cover object-center')['src']


        if waifu_classification.lower() in ["husbando"]:
            return Eru.random_waifu()
        elif waifu_classification == "":
            waifu_classification = "Waifu"

        return name, alternate_name, age, birthday, height, weight, blood_type, waifu_classification, description, like_rank, popularity_rank, image_url