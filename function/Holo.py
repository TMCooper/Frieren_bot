import os
import sys
from dotenv import load_dotenv
from googletrans import Translator # type: ignore
import signal
import subprocess
import time
from pathlib import Path
import platform
from function.Yui import *

translator = Translator()
load_dotenv()

PATH = os.path.dirname(os.path.abspath(__file__))
DEV_ID = os.getenv('DEV_ID')

class Holo:
    async def shutdown(bot, ID, interaction):
        # print(f"ID : {ID} DEV_ID : {DEV_ID}")
        if int(ID) == int(DEV_ID):
            await interaction.followup.send("Le bot se ferme...") # Envoyer un message au bot sur Discord

            await bot.close()  # Fermer le bot proprement
            print("Bot has been shut down. Sending Ctrl+C signal...")

            os.kill(os.getpid(), signal.SIGINT)
            Holo.manage_api("stop")

            return True
        else:
            print("Unauthorized attempt to shut down the bot.")
            return "Non autorisé à down le bot."

    async def reboot(bot, ID, interaction):
        # print(f"ID : {ID} DEV_ID : {DEV_ID}")
        if int(ID) == int(DEV_ID):

            # Envoyer un message confirmant le redémarrage
            await interaction.followup.send("Le bot redémare...")
            await bot.close()  # Fermer le bot proprement
            print("Bot has been shut down. Restarting...")
            os.kill(os.getpid(), signal.SIGINT)

            # Relancer le script
            os.execv(sys.executable, ['python'] + sys.argv)
            Holo.manage_api("restart")

        else:
            # Si l'utilisateur n'est pas autorisé
            await interaction.followup.send("Vous n'êtes pas autorisé à redémarrer ce bot.")
        return False

    async def Translate(phrase, langue):
        trad = translator.translate(phrase, dest=langue)

        formated_traduction = trad.text
        prononce = trad.pronunciation
        
        return formated_traduction, prononce
    
    async def purge_anime_file(id, interaction):
        if int(id) == int(DEV_ID):
            await interaction.followup.send("Purge du fichier anime.json...")
            if os.path.exists('anime.json'):
                os.remove('anime.json')
            # Crée un fichier vide
            with open('anime.json', 'w') as f:
                pass
        else:
            await interaction.followup.send("Vous n'êtes pas autorisé à purger le fichier...")

    async def update(bot, ID, interaction):
        if int(ID) == int(DEV_ID):
        
            original_dir = Path.cwd()
            target_dir = original_dir / "API_Grow_Garden"

            await interaction.followup.send("Mise a jour du bot...")

            # Mettre à jour le bot
            await bot.close()
            os.kill(os.getpid(), signal.SIGINT)
            subprocess.run("git pull origin cloud", shell=True)
            subprocess.run("pip install -r requirements.txt", shell=True)
            os.chdir(target_dir)
            subprocess.run("sh ./auto_install.sh", shell=True)
            os.chdir(original_dir)
            time.sleep(1.5)
        
            os.execv(sys.executable, ['python'] + sys.argv)
        else:
            await interaction.followup.send("Vous n'êtes pas autorisé à mettre à jour le bot.")

    async def manage_api(action):
        
        original_dir = Path.cwd()
        target_dir = original_dir / "API_Grow_Garden"
        
        try:
            os.chdir(target_dir)
            
            if action == "start":
                subprocess.run(["pm2", "start", "Server.js", "--name", "API-grow-a-garden"], check=True)
                print("✅ API démarrée avec succès !")
                
            elif action == "stop":
                subprocess.run(["pm2", "stop", "API-grow-a-garden"], check=True)
                print("⏹️ API arrêtée avec succès !")
                
            elif action == "restart":
                subprocess.run(["pm2", "restart", "API-grow-a-garden"], check=True)
                print("🔄 API redémarrée avec succès !")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de l'opération : {e}")
            return False
        finally:
            os.chdir(original_dir)
        
        return True