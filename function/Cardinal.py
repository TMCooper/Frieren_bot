import json
from function.Yui import Yui

# class to manage the folder

class Cardinal:
    async def get_all_games():
        base_url = "https://www.speedrun.com/fr-FR/games"
        games = []
        page_number = 1

        while True:
            url = f"{base_url}?page={page_number}"
            soup = await Yui.requets(url)
            game_links = soup.find_all('a', class_="x-focus-outline")

            if not game_links:
                break

            for link in game_links:
                game_name = link.find('img')['alt']
                game_href = link['href']
                games.append({"title": game_name, "link": f"https://www.speedrun.com{game_href}"})

            page_number += 1

        return games

    async def save_games_to_file(games):
        with open('games.json', 'w', encoding='utf-8') as file:
            json.dump(games, file, ensure_ascii=False, indent=4)

    async def load_games_from_file():
        try:
            with open('games.json', 'r', encoding='utf-8') as file:
                games = json.load(file)
        except FileNotFoundError:
            return "None"
        return games