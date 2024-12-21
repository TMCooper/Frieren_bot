from interactions import slash_command, SlashContext, Client, Intents, listen, user_context_menu, Member, OptionType, ContextMenuContext, Message, message_context_menu
from interactions.api.events import MessageCreate, ChannelCreate

from function.Maid import Maid
import os
import subprocess
from dotenv import load_dotenv 


load_dotenv()

TOKEN = os.getenv('TOKEN')

# prefix = "?"

# Définissez les intents avant de créer le bot
# intents = discord.Intents.default()
# intents.message_content = True

# Passez les intents lors de la création du bot
bot = Client(intents=Intents.DEFAULT | Intents.MESSAGE_CONTENT)

@listen()  # this decorator tells snek that it needs to listen for the corresponding event, and run this coroutine
async def on_ready():
    # This event is called when the bot is ready to respond to commands
    subprocess.run('cls', shell=True)
    print(f"Le créateur est : {bot.owner}")
    print(f"{bot.user} est Réveiller !\n")


# .split('{"')[1].split('"}')[0] 

@listen()
async def message_create(event: MessageCreate):
    try:
        if event.message.author == bot.user.id:
            return  # Skip si le bot envoie un message
        # Accéder au membre qui a envoyé le message
        member = event.message.author  # L'auteur du message
        message_content = event.message.content # Contenu du message
        nom_serv = event.message.guild.name # Nom du serveur où le message a été envoyé
        print(f'Sur le serveur : {nom_serv} \nMessage de {member.username} : {message_content}')  # Affiche le nom d'utilisateur complet
        # print(f"Channel du message : {event.message.jump_url}")  # Affiche l'URL du message
    except Exception as e:
        print(f"Erreur lors de la réception du message : {e}")


@slash_command(
    name="hello",
    description="Petit bonjour de Frieren",
    options=[
        {
            "name": "member",
            "description": "Le membre à saluer",
            "type": OptionType.USER,  # Indique que l'option attend un utilisateur
            "required": True,         # Rend l'option obligatoire
        }
    ],
)
async def command(ctx: SlashContext, member: Member):
    # Envoyer un message mentionnant le membre
    await ctx.send(f"Hello {member.mention} :kiss:")


@slash_command(
        name="hello_world", 
        description="Un petit hello world ma fois aussi simple que ça :)"
        )
async def my_command_function(ctx: SlashContext):
    await ctx.send("Hello World")

@slash_command(
    name="code_honkai_star_rail", 
    description="Recupère les code d'échange de honkai-star-rail"
    )
async def code_honkai_star_rail(ctx: SlashContext):
    await ctx.send("Scraping...")
    code = Maid.scrap()
    await ctx.respond(f"Code d'échange Honkai Star Rail : \n{code}")

@slash_command(
    name="test",
    description="Test",
    options=[
        {
            "name": "Jeux",
            "description": "Le jeux ou vous souhaité recuperer les code",
            "required": True,
            "type": OptionType.STRING,
            "autocomplete": True,
        }
    ],
)
async def commande(ctx: SlashContext, string_option: str):
    await ctx.send(f"You input {string_option}")

bot.start(TOKEN)