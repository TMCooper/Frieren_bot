import discord
from discord.ext import commands
import os
import subprocess
from dotenv import load_dotenv 

load_dotenv()

TOKEN = os.getenv('TOKEN')

startup_extensions = ["get_message"]

prefix = "?"

# Définissez les intents avant de créer le bot
intents = discord.Intents.default()
intents.message_content = True

# Passez les intents lors de la création du bot
bot = commands.Bot(command_prefix=prefix, intents=intents)
bot.remove_command("help")

@bot.event
async def on_ready():
    subprocess.run('cls', shell=True)
    print(f'{bot.user} est réveillé !')

@bot.event
async def on_message(message):
    if not message.author.bot:  # Évite de répondre aux messages des autres bots
        print(f'Message from {message.author}: {message.content}')
    
    # Important : traitez les commandes
    await bot.process_commands(message)

@bot.command(pass_context=True)
async def hello(ctx):
    msg = f'Hello {ctx.author.mention}'
    await ctx.send(msg)

@bot.command(pass_context=True)
async def valo_shop(ctx):
    valorant_shop = f'{ctx.author.mention} la fonction valorant store en préparation'
    await ctx.send(valorant_shop)

bot.run(TOKEN)