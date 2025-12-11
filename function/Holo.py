import os
import sys
from dotenv import load_dotenv
from googletrans import Translator # type: ignore
import signal
import subprocess
import time
from pathlib import Path
# import platform
from function.Yui import *
from function.Maid import *

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
            if os.path.exists('data/anime.json'):
                os.remove('data/anime.json')
            # Crée un fichier vide
            with open('data/anime.json', 'w') as f:
                pass
        else:
            await interaction.followup.send("Vous n'êtes pas autorisé à purger le fichier...")

    async def update(bot, ID, interaction):
        if int(ID) == int(DEV_ID):
            await interaction.followup.send("Mise a jour du bot...")

            # Mettre à jour le bot
            await bot.close()
            os.kill(os.getpid(), signal.SIGINT)
            subprocess.run("git pull origin cloud", shell=True)
            subprocess.run("pip install -r requirements.txt", shell=True)
            time.sleep(1.5)
        
            os.execv(sys.executable, ['python'] + sys.argv)
        else:
            await interaction.followup.send("Vous n'êtes pas autorisé à mettre à jour le bot.")
    
    async def db_gag_refresh(ID, interaction):
        if int(ID) == int(DEV_ID):
            await interaction.followup.send("Actualisation de la liste...")

            await Maid.extract_gear_names()
            await Maid.extract_fruit_names()
            await Maid.extract_egg_names()
        else :
            return "Permission d'actualisation non accorder"
        
    async def changeStatus(status, bot):
        if status == "do_not_disturb":
            await bot.change_presence(status=discord.Status.do_not_disturb)
        elif status == "idle":
            await bot.change_presence(status=discord.Status.idle)
        elif status == "offline":
            await bot.change_presence(status=discord.Status.offline)
        elif status == "online":
            await bot.change_presence(status=discord.Status.online)
        
        return status
    
    async def changeActivity(interaction, activite, nom, stream_url, bot): #Fonction a update acutellement incomplete
        if activite.value != "streaming":
            await bot.change_presence(
                activity=discord.Activity(type=discord.ActivityType[activite.value] , name=nom)
            )
            await interaction.followup.send("Le status a bien été changé !")

        else:
            if not stream_url:
                await interaction.followup.send("Tu dois fournir un lien Twitch/YouTube pour le mode streaming")
            else:
                await bot.change_presence(activity=discord.Streaming(name=nom, url=stream_url))
                await interaction.followup.send("Le status a bien été changé !")