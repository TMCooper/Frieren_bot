import discord
import os
import subprocess
from dotenv import load_dotenv 

load_dotenv()

TOKEN = os.getenv('TOKEN')

class MyClient(discord.Client):
    async def on_ready(self):
        subprocess.run('cls', shell=True)
        print(f'{self.user} est reveiller !')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(TOKEN)