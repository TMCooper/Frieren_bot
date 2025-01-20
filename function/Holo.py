import os
from dotenv import load_dotenv
from googletrans import Translator
import signal
from function.Yui import *

translator = Translator()
load_dotenv()

DEV_ID = os.getenv('DEV_ID')

class Holo:
    async def shutdown(bot, ID, interaction):
        print(f"ID : {ID} DEV_ID : {DEV_ID}")
        if int(ID) == int(DEV_ID):
            await interaction.followup.send("Le bot va se fermer...") # Envoyer un message au bot sur Discord

            await bot.close()  # Fermer le bot proprement
            print("Bot has been shut down. Sending Ctrl+C signal...")

            os.kill(os.getpid(), signal.SIGINT)  # Envoie un signal Ctrl+C au processus

            return True
        else:
            print("Unauthorized attempt to shut down the bot.")
            return "Non autorisé à down le bot."

    async def Translate(phrase, langue):
        trad = translator.translate(phrase, dest=langue)

        formated_traduction = trad.text
        prononce = trad.pronunciation
        
        return formated_traduction, prononce