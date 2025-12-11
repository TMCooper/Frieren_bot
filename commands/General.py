import discord
from discord import app_commands
from discord.ext import commands
from function.Holo import Holo

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hello", description="Petit bonjour de Frieren")
    async def hello(self, interaction: discord.Interaction, member: discord.Member):
        if member is None:
            await interaction.response.send_message("Veuillez mentionner un membre valide.", ephemeral=True)
            return
        await interaction.response.send_message(f"Hello {member.mention} :kiss:")

    @app_commands.command(name="hello_world", description="Un petit hello world ma foi aussi simple que ça :)")
    async def hello_world(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hello World")

    @app_commands.command(name="my_id", description="Donne l'id de l'utilisateur")
    async def my_id(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(f"Votre ID : {interaction.user.id}")

    @app_commands.command(name="translate", description="Traduit une phrase dans la langue de votre choix")
    @app_commands.describe(phrase="Phrase à traduire")
    @app_commands.describe(langues="Langues disponibles : Japonais, Français, Anglais, Espagnole, Allemand, Chinois, Italien, Russe, Portugais, Polonais, Catalan, Grecque, Danois, Hollandais, Suédois")
    @app_commands.choices(langues=[
        app_commands.Choice(name="Japonais", value="ja"),
        app_commands.Choice(name="Français", value="fr"),
        app_commands.Choice(name="Anglais", value="en"),
        app_commands.Choice(name="Espagnole", value="es"),
        app_commands.Choice(name="Allemand", value="de"),
        app_commands.Choice(name="Chinois", value="zh-CN"),
        app_commands.Choice(name="Italien", value="it"),
        app_commands.Choice(name="Russe", value="ru"),
        app_commands.Choice(name="Portugaisse", value="pt-BR"),
        app_commands.Choice(name="Polonais", value="pl"),
        app_commands.Choice(name="Catalan", value="ca"),
        app_commands.Choice(name="Grecque", value="el"),
        app_commands.Choice(name="Danois", value="da"),
        app_commands.Choice(name="Hollandais", value="nl"),
        app_commands.Choice(name="Suédois", value="sv")
    ])
    async def translate(self, interaction: discord.Interaction, phrase: str, langues: app_commands.Choice[str]):
        await interaction.response.defer()
        formated_traduction, prononce = await Holo.Translate(phrase, langues.value)
        await interaction.followup.send(f'Phrase : ``{phrase}`` Vers : ``{langues.name}`` \n Traduction : ``{formated_traduction}`` \n Prononciation : ``{prononce}``')

async def setup(bot):
    await bot.add_cog(General(bot))
