from function.Yui import Yui

class Maid:
    def scrap():
        
        # Trouver tous les liens
        links = Yui.requet_hsr()
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