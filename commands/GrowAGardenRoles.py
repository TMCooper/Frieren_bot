import discord
from discord import app_commands
from discord.ext import commands
import json
import os

class GrowAGardenRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="fruit_role", description="Associe un fruit à un rôle à ping lors de l'affichage du market")
    @app_commands.describe(fruit="Nom du fruit", role="Rôle à ping")
    async def fruit_role(self, interaction: discord.Interaction, fruit: str, role: discord.Role):
        await interaction.response.defer(ephemeral=True)
        try:
            if os.path.exists("data/fruit_roles.json"):
                with open("data/fruit_roles.json", "r", encoding="utf-8") as f:
                    fruit_roles = json.load(f)
            else:
                fruit_roles = {}
            guild_id = str(interaction.guild_id)
            if guild_id not in fruit_roles:
                fruit_roles[guild_id] = {}
            fruit_key = fruit.lower().strip()
            fruit_info = None
            try:
                with open("data/fruits.json", "r", encoding="utf-8") as f:
                    all_fruits = json.load(f)
                for crop in all_fruits:
                    if (crop.get("name", "").lower() == fruit.lower() or crop.get("identifier", "").lower() == fruit.lower()):
                        fruit_info = crop
                        fruit_key = crop.get("identifier", fruit.lower())
                        break
            except FileNotFoundError:
                pass
            fruit_roles[guild_id][fruit_key] = role.id
            os.makedirs("data", exist_ok=True)
            with open("data/fruit_roles.json", "w", encoding="utf-8") as f:
                json.dump(fruit_roles, f, ensure_ascii=False, indent=4)
            if fruit_info:
                rarity = fruit_info.get("additional", {}).get("Rarity", "Unknown")
                harvest_type = fruit_info.get("additional", {}).get("Harvest Type", "Unknown")
                price = fruit_info.get("price", 0)
                embed = discord.Embed(title="✅ Association créée", description=f"Le fruit **{fruit_info['name']}** est maintenant associé au rôle {role.mention}", color=0x4CAF50)
                embed.add_field(name="📊 Informations", value=f"**Rareté:** {rarity}\n**Type:** {harvest_type}\n**Valeur:** {price:,}", inline=True)
                embed.set_thumbnail(url=fruit_info.get("image", ""))
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(f"✅ Le fruit **{fruit}** est maintenant associé au rôle {role.mention}.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Une erreur est survenue : {str(e)}", ephemeral=True)

    @fruit_role.autocomplete("fruit")
    async def fruit_autocomplete(self, interaction: discord.Interaction, current: str):
        try:
            with open("data/fruits.json", "r", encoding="utf-8") as f:
                all_fruits = json.load(f)
        except FileNotFoundError:
            return [app_commands.Choice(name="❌ Fichier fruits.json introuvable", value="error")]
        current_lower = current.lower()
        suggestions = []
        for fruit in all_fruits:
            fruit_name = fruit.get("name", "Unknown")
            fruit_identifier = fruit.get("identifier", "")
            if current_lower in fruit_name.lower() or current_lower in fruit_identifier.lower():
                rarity = fruit.get("additional", {}).get("Rarity", "")
                price = fruit.get("price", 0)
                rarity_emoji = {"Common": "🟢", "Uncommon": "🔵", "Rare": "🟣", "Epic": "🟠", "Legendary": "🟡", "Mythical": "🔴", "Divine": "✨"}.get(rarity, "🍎")
                display_name = f"{rarity_emoji} {fruit_name}"
                if rarity: display_name += f" ({rarity})"
                if price > 0: display_name += f" - {price:,}"
                value = fruit_identifier if fruit_identifier else fruit_name.lower()
                suggestions.append(app_commands.Choice(name=display_name[:100], value=value))
        return suggestions[:25]

    @app_commands.command(name="remove_fruit_role", description="Supprime l'association d'un fruit avec un rôle")
    @app_commands.describe(fruit="Nom du fruit à supprimer")
    async def remove_fruit_role(self, interaction: discord.Interaction, fruit: str):
        await interaction.response.defer(ephemeral=True)
        try:
            if not os.path.exists("data/fruit_roles.json"):
                await interaction.followup.send("❌ Aucun fruit configuré.", ephemeral=True)
                return
            with open("data/fruit_roles.json", "r", encoding="utf-8") as f:
                fruit_roles = json.load(f)
            guild_id = str(interaction.guild_id)
            fruit_key = fruit.lower().strip()
            if guild_id not in fruit_roles or fruit_key not in fruit_roles[guild_id]:
                await interaction.followup.send(f"❌ Le fruit **{fruit}** n'est pas configuré.", ephemeral=True)
                return
            del fruit_roles[guild_id][fruit_key]
            if not fruit_roles[guild_id]:
                del fruit_roles[guild_id]
            os.makedirs("data", exist_ok=True)
            with open("data/fruit_roles.json", "w", encoding="utf-8") as f:
                json.dump(fruit_roles, f, ensure_ascii=False, indent=4)
            await interaction.followup.send(f"✅ Le fruit **{fruit}** a été supprimé.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur : {str(e)}", ephemeral=True)

    @fruit_role.autocomplete("fruit")
    async def remove_fruit_autocomplete(self, interaction: discord.Interaction, current: str):
        try:
            with open("data/fruit_roles.json", "r", encoding="utf-8") as f:
                fruit_roles = json.load(f)
            guild_id = str(interaction.guild_id)
            if guild_id not in fruit_roles: return []
            configured_fruits = fruit_roles[guild_id].keys()
            fruit_infos = {}
            try:
                with open("data/fruits.json", "r", encoding="utf-8") as f:
                    all_fruits = json.load(f)
                    for fruit in all_fruits:
                        identifier = fruit.get("identifier", fruit.get("name", "").lower())
                        fruit_infos[identifier] = fruit
            except FileNotFoundError: pass
            suggestions = []
            current_lower = current.lower()
            for fruit_key in configured_fruits:
                fruit_info = fruit_infos.get(fruit_key, {})
                fruit_name = fruit_info.get("name", fruit_key.title())
                if current_lower in fruit_name.lower() or current_lower in fruit_key:
                    rarity = fruit_info.get("additional", {}).get("Rarity", "")
                    rarity_emoji = {"Common": "🟢", "Uncommon": "🔵", "Rare": "🟣", "Epic": "🟠", "Legendary": "🟡", "Mythical": "🔴", "Divine": "✨"}.get(rarity, "🍎")
                    display_name = f"{rarity_emoji} {fruit_name}"
                    if rarity: display_name += f" ({rarity})"
                    suggestions.append(app_commands.Choice(name=display_name, value=fruit_key))
            return suggestions[:25]
        except Exception as e:
            return [app_commands.Choice(name=f"❌ Erreur: {str(e)}", value="error")]

    @app_commands.command(name="list_fruit_roles", description="Affiche tous les fruits configurés avec leurs rôles et informations")
    async def list_fruit_roles(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            if not os.path.exists("data/fruit_roles.json"):
                await interaction.followup.send("❌ Aucun fruit configuré.", ephemeral=True)
                return
            with open("data/fruit_roles.json", "r", encoding="utf-8") as f:
                fruit_roles = json.load(f)
            guild_id = str(interaction.guild_id)
            if guild_id not in fruit_roles or not fruit_roles[guild_id]:
                await interaction.followup.send("❌ Aucun fruit configuré pour ce serveur.", ephemeral=True)
                return
            fruit_infos = {}
            try:
                with open("data/fruits.json", "r", encoding="utf-8") as f:
                    all_fruits = json.load(f)
                    for fruit in all_fruits:
                        identifier = fruit.get("identifier", fruit.get("name", "").lower())
                        fruit_infos[identifier] = fruit
            except FileNotFoundError: pass
            embed = discord.Embed(title="🍎 Fruits configurés", description="Liste des fruits avec leurs rôles associés", color=0x4CAF50)
            fruits_by_rarity = {}
            for fruit_key, role_id in fruit_roles[guild_id].items():
                role = interaction.guild.get_role(role_id)
                role_mention = role.mention if role else f"❌ Rôle supprimé (ID: {role_id})"
                fruit_info = fruit_infos.get(fruit_key, {})
                fruit_name = fruit_info.get("name", fruit_key.title())
                rarity = fruit_info.get("additional", {}).get("Rarity", "Unknown")
                price = fruit_info.get("price", 0)
                if rarity not in fruits_by_rarity: fruits_by_rarity[rarity] = []
                fruit_display = f"🍓 **{fruit_name}**"
                if price > 0: fruit_display += f" ({price:,})"
                fruit_display += f"\n└ {role_mention}"
                fruits_by_rarity[rarity].append(fruit_display)
            rarity_order = ["Divine", "Mythical", "Legendary", "Epic", "Rare", "Uncommon", "Common", "Unknown"]
            for rarity in rarity_order:
                if rarity in fruits_by_rarity:
                    rarity_emoji = {"Common": "🟢", "Uncommon": "🔵", "Rare": "🟣", "Epic": "🟠", "Legendary": "🟡", "Mythical": "🔴", "Divine": "✨", "Unknown": "❓"}.get(rarity, "❓")
                    fruits_text = "\n\n".join(fruits_by_rarity[rarity])
                    embed.add_field(name=f"{rarity_emoji} {rarity} ({len(fruits_by_rarity[rarity])})", value=fruits_text, inline=False)
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur : {str(e)}", ephemeral=True)

    @app_commands.command(name="gear_role", description="Associe un gear à un rôle à ping lors de l'affichage du market")
    @app_commands.describe(gear="Nom du gear", role="Rôle à ping")
    async def gear_role(self, interaction: discord.Interaction, gear: str, role: discord.Role):
        await interaction.response.defer(ephemeral=True)
        try:
            if os.path.exists("data/gear_roles.json"):
                with open("data/gear_roles.json", "r", encoding="utf-8") as f:
                    gear_roles = json.load(f)
            else:
                gear_roles = {}
            guild_id = str(interaction.guild_id)
            if guild_id not in gear_roles:
                gear_roles[guild_id] = {}
            gear_key = gear.lower().strip()
            gear_info = None
            try:
                with open("data/gear.json", "r", encoding="utf-8") as f:
                    all_gears = json.load(f)
                for item in all_gears:
                    if (item.get("name", "").lower() == gear.lower() or item.get("identifier", "").lower() == gear.lower()):
                        gear_info = item
                        gear_key = item.get("identifier", gear.lower())
                        break
            except FileNotFoundError: pass
            gear_roles[guild_id][gear_key] = role.id
            os.makedirs("data", exist_ok=True)
            with open("data/gear_roles.json", "w", encoding="utf-8") as f:
                json.dump(gear_roles, f, ensure_ascii=False, indent=4)
            if gear_info:
                tier = gear_info.get("additional", {}).get("Tier", "Unknown")
                effects = gear_info.get("additional", {}).get("Effects", "Unknown")
                price = gear_info.get("price", 0)
                robux_price = gear_info.get("additional", {}).get("Robux Price", "N/A")
                embed = discord.Embed(title="✅ Association créée", description=f"Le gear **{gear_info['name']}** est maintenant associé au rôle {role.mention}", color=0x4CAF50)
                embed.add_field(name="📊 Informations", value=f"**Tier:** {tier}\n**Effets:** {effects}\n**Prix:** {price:,} Sheckles\n**Robux:** {robux_price}", inline=True)
                embed.set_thumbnail(url=gear_info.get("image", ""))
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(f"✅ Le gear **{gear}** est maintenant associé au rôle {role.mention}.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Une erreur est survenue : {str(e)}", ephemeral=True)

    @gear_role.autocomplete("gear")
    async def gear_autocomplete(self, interaction: discord.Interaction, current: str):
        try:
            with open("data/gear.json", "r", encoding="utf-8") as f:
                all_gears = json.load(f)
        except FileNotFoundError: return [app_commands.Choice(name="❌ Fichier gear.json introuvable", value="error")]
        current_lower = current.lower()
        suggestions = []
        for gear in all_gears:
            gear_name = gear.get("name", "Unknown")
            gear_identifier = gear.get("identifier", "")
            if current_lower in gear_name.lower() or current_lower in gear_identifier.lower():
                tier = gear.get("additional", {}).get("Tier", "")
                price = gear.get("price", 0)
                tier_emoji = {"Common": "🟢", "Uncommon": "🔵", "Rare": "🟣", "Epic": "🟠", "Legendary": "🟡", "Mythical": "🔴", "Divine": "✨"}.get(tier, "⚙️")
                display_name = f"{tier_emoji} {gear_name}"
                if tier: display_name += f" ({tier})"
                if price > 0: display_name += f" - {price:,}"
                value = gear_identifier if gear_identifier else gear_name.lower()
                suggestions.append(app_commands.Choice(name=display_name[:100], value=value))
        return suggestions[:25]

    @app_commands.command(name="remove_gear_role", description="Supprime l'association d'un gear avec un rôle")
    @app_commands.describe(gear="Nom du gear à supprimer")
    async def remove_gear_role(self, interaction: discord.Interaction, gear: str):
        await interaction.response.defer(ephemeral=True)
        try:
            if not os.path.exists("data/gear_roles.json"):
                await interaction.followup.send("❌ Aucun gear configuré.", ephemeral=True)
                return
            with open("data/gear_roles.json", "r", encoding="utf-8") as f:
                gear_roles = json.load(f)
            guild_id = str(interaction.guild_id)
            gear_key = gear.lower().strip()
            if guild_id not in gear_roles or gear_key not in gear_roles[guild_id]:
                await interaction.followup.send(f"❌ Le gear **{gear}** n'est pas configuré.", ephemeral=True)
                return
            del gear_roles[guild_id][gear_key]
            if not gear_roles[guild_id]: del gear_roles[guild_id]
            os.makedirs("data", exist_ok=True)
            with open("data/gear_roles.json", "w", encoding="utf-8") as f:
                json.dump(gear_roles, f, ensure_ascii=False, indent=4)
            await interaction.followup.send(f"✅ Le gear **{gear}** a été supprimé.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur : {str(e)}", ephemeral=True)

    @remove_gear_role.autocomplete("gear")
    async def remove_gear_autocomplete(self, interaction: discord.Interaction, current: str):
        try:
            with open("data/gear_roles.json", "r", encoding="utf-8") as f:
                gear_roles = json.load(f)
            guild_id = str(interaction.guild_id)
            if guild_id not in gear_roles: return []
            configured_gears = gear_roles[guild_id].keys()
            gear_infos = {}
            try:
                with open("data/gear.json", "r", encoding="utf-8") as f:
                    all_gears = json.load(f)
                    for gear in all_gears:
                        identifier = gear.get("identifier", gear.get("name", "").lower())
                        gear_infos[identifier] = gear
            except FileNotFoundError: pass
            suggestions = []
            current_lower = current.lower()
            for gear_key in configured_gears:
                gear_info = gear_infos.get(gear_key, {})
                gear_name = gear_info.get("name", gear_key.title())
                if current_lower in gear_name.lower() or current_lower in gear_key:
                    tier = gear_info.get("additional", {}).get("Tier", "")
                    tier_emoji = {"Common": "🟢", "Uncommon": "🔵", "Rare": "🟣", "Epic": "🟠", "Legendary": "🟡", "Mythical": "🔴", "Divine": "✨"}.get(tier, "⚙️")
                    display_name = f"{tier_emoji} {gear_name}"
                    if tier: display_name += f" ({tier})"
                    suggestions.append(app_commands.Choice(name=display_name, value=gear_key))
            return suggestions[:25]
        except Exception as e:
            return [app_commands.Choice(name=f"❌ Erreur: {str(e)}", value="error")]

    @app_commands.command(name="list_gear_roles", description="Affiche tous les gears configurés avec leurs rôles et informations")
    async def list_gear_roles(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            if not os.path.exists("data/gear_roles.json"):
                await interaction.followup.send("❌ Aucun gear configuré.", ephemeral=True)
                return
            with open("data/gear_roles.json", "r", encoding="utf-8") as f:
                gear_roles = json.load(f)
            guild_id = str(interaction.guild_id)
            if guild_id not in gear_roles or not gear_roles[guild_id]:
                await interaction.followup.send("❌ Aucun gear configuré pour ce serveur.", ephemeral=True)
                return
            gear_infos = {}
            try:
                with open("data/gear.json", "r", encoding="utf-8") as f:
                    all_gears = json.load(f)
                    for gear in all_gears:
                        identifier = gear.get("identifier", gear.get("name", "").lower())
                        gear_infos[identifier] = gear
            except FileNotFoundError: pass
            embed = discord.Embed(title="⚙️ Gears configurés", description="Liste des gears avec leurs rôles associés", color=0x4CAF50)
            gears_by_tier = {}
            for gear_key, role_id in gear_roles[guild_id].items():
                role = interaction.guild.get_role(role_id)
                role_mention = role.mention if role else f"❌ Rôle supprimé (ID: {role_id})"
                gear_info = gear_infos.get(gear_key, {})
                gear_name = gear_info.get("name", gear_key.title())
                tier = gear_info.get("additional", {}).get("Tier", "Unknown")
                price = gear_info.get("price", 0)
                if tier not in gears_by_tier: gears_by_tier[tier] = []
                gear_display = f"⚙️ **{gear_name}**"
                if price > 0: gear_display += f" ({price:,})"
                gear_display += f"\n└ {role_mention}"
                gears_by_tier[tier].append(gear_display)
            tier_order = ["Divine", "Mythical", "Legendary", "Epic", "Rare", "Uncommon", "Common", "Unknown"]
            for tier in tier_order:
                if tier in gears_by_tier:
                    tier_emoji = {"Common": "🟢", "Uncommon": "🔵", "Rare": "🟣", "Epic": "🟠", "Legendary": "🟡", "Mythical": "🔴", "Divine": "✨", "Unknown": "❓"}.get(tier, "❓")
                    gears_text = "\n\n".join(gears_by_tier[tier])
                    embed.add_field(name=f"{tier_emoji} {tier} ({len(gears_by_tier[tier])})", value=gears_text, inline=False)
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur : {str(e)}", ephemeral=True)

    @app_commands.command(name="egg_role", description="Associe un œuf à un rôle à ping lors de l'affichage du market")
    @app_commands.describe(egg="Nom de l'œuf", role="Rôle à ping")
    async def egg_role(self, interaction: discord.Interaction, egg: str, role: discord.Role):
        await interaction.response.defer(ephemeral=True)
        try:
            if os.path.exists("data/egg_roles.json"):
                with open("data/egg_roles.json", "r", encoding="utf-8") as f:
                    egg_roles = json.load(f)
            else:
                egg_roles = {}
            guild_id = str(interaction.guild_id)
            if guild_id not in egg_roles:
                egg_roles[guild_id] = {}
            egg_key = egg.lower().strip()
            egg_info = None
            try:
                with open("data/eggs.json", "r", encoding="utf-8") as f:
                    all_eggs = json.load(f)
                for e in all_eggs:
                    if (e.get("name", "").lower() == egg.lower() or e.get("identifier", "").lower() == egg.lower()):
                        egg_info = e
                        egg_key = e.get("identifier", egg.lower())
                        break
            except FileNotFoundError: pass
            egg_roles[guild_id][egg_key] = role.id
            os.makedirs("data", exist_ok=True)
            with open("data/egg_roles.json", "w", encoding="utf-8") as f:
                json.dump(egg_roles, f, ensure_ascii=False, indent=4)
            if egg_info:
                rarity = egg_info.get("rarity", "Unknown")
                price = egg_info.get("base_value", "Inconnu")
                embed = discord.Embed(title="✅ Association créée", description=f"L'œuf **{egg_info['name']}** est maintenant associé au rôle {role.mention}", color=0x4CAF50)
                embed.add_field(name="📊 Informations", value=f"**Rareté:** {rarity}\n**Valeur:** {price}", inline=True)
                embed.set_thumbnail(url=egg_info.get("image", ""))
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(f"✅ L'œuf **{egg}** est maintenant associé au rôle {role.mention}.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Une erreur est survenue : {str(e)}", ephemeral=True)

    @egg_role.autocomplete("egg")
    async def egg_autocomplete(self, interaction: discord.Interaction, current: str):
        try:
            with open("data/eggs.json", "r", encoding="utf-8") as f:
                all_eggs = json.load(f)
        except FileNotFoundError:
            return [app_commands.Choice(name="❌ Fichier eggs.json introuvable", value="error")]
        current_lower = current.lower()
        suggestions = []
        for egg in all_eggs:
            name = egg.get("name", "Unknown")
            identifier = egg.get("identifier", "")
            rarity = egg.get("rarity", "")
            price = egg.get("base_value", 0)
            if current_lower in name.lower() or current_lower in identifier.lower():
                emoji = {"Common": "🟢", "Uncommon": "🔵", "Rare": "🟣", "Epic": "🟠", "Legendary": "🟡", "Mythical": "🔴", "Divine": "✨"}.get(rarity, "🥚")
                display = f"{emoji} {name}"
                if rarity: display += f" ({rarity})"
                if price: display += f" - {price}"
                value = identifier if identifier else name.lower()
                suggestions.append(app_commands.Choice(name=display[:100], value=value))
        return suggestions[:25]

    @app_commands.command(name="list_egg_roles", description="Affiche tous les œufs configurés avec leurs rôles")
    async def list_egg_roles(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            if not os.path.exists("data/egg_roles.json"):
                await interaction.followup.send("❌ Aucun œuf configuré.", ephemeral=True)
                return
            with open("data/egg_roles.json", "r", encoding="utf-8") as f:
                egg_roles = json.load(f)
            guild_id = str(interaction.guild_id)
            if guild_id not in egg_roles or not egg_roles[guild_id]:
                await interaction.followup.send("❌ Aucun œuf configuré pour ce serveur.", ephemeral=True)
                return
            with open("data/eggs.json", "r", encoding="utf-8") as f:
                all_eggs = json.load(f)
                eggs_by_id = {egg.get("identifier", egg["name"].lower()): egg for egg in all_eggs}
            embed = discord.Embed(title="🥚 Œufs configurés", description="Liste des œufs avec leurs rôles associés", color=0x4CAF50)
            for egg_key, role_id in egg_roles[guild_id].items():
                egg = eggs_by_id.get(egg_key, {})
                name = egg.get("name", egg_key.title())
                rarity = egg.get("rarity", "Unknown")
                price = egg.get("base_value", "Inconnu")
                role = interaction.guild.get_role(role_id)
                role_mention = role.mention if role else f"❌ (ID: {role_id})"
                emoji = {"Common": "🟢", "Uncommon": "🔵", "Rare": "🟣", "Epic": "🟠", "Legendary": "🟡", "Mythical": "🔴", "Divine": "✨"}.get(rarity, "🥚")
                embed.add_field(name=f"{emoji} {name}", value=f"Rôle: {role_mention}\nValeur: {price}", inline=False)
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur : {str(e)}", ephemeral=True)

    @app_commands.command(name="remove_egg_role", description="Supprime l'association d'un œuf avec un rôle")
    @app_commands.describe(egg="Nom de l'œuf à supprimer")
    async def remove_egg_role(self, interaction: discord.Interaction, egg: str):
        await interaction.response.defer(ephemeral=True)
        try:
            if not os.path.exists("data/egg_roles.json"):
                await interaction.followup.send("❌ Aucun œuf configuré.", ephemeral=True)
                return
            with open("data/egg_roles.json", "r", encoding="utf-8") as f:
                egg_roles = json.load(f)
            guild_id = str(interaction.guild_id)
            egg_key = egg.lower().strip()
            if guild_id not in egg_roles or egg_key not in egg_roles[guild_id]:
                await interaction.followup.send(f"❌ L'œuf **{egg}** n'est pas configuré.", ephemeral=True)
                return
            del egg_roles[guild_id][egg_key]
            if not egg_roles[guild_id]:
                del egg_roles[guild_id]
            os.makedirs("data", exist_ok=True)
            with open("data/egg_roles.json", "w", encoding="utf-8") as f:
                json.dump(egg_roles, f, ensure_ascii=False, indent=4)
            await interaction.followup.send(f"✅ L'œuf **{egg}** a été supprimé.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur : {str(e)}", ephemeral=True)

    @remove_egg_role.autocomplete("egg")
    async def remove_egg_autocomplete(self, interaction: discord.Interaction, current: str):
        try:
            with open("data/egg_roles.json", "r", encoding="utf-8") as f:
                egg_roles = json.load(f)
            guild_id = str(interaction.guild_id)
            if guild_id not in egg_roles: return []
            configured_eggs = egg_roles[guild_id].keys()
            try:
                with open("data/eggs.json", "r", encoding="utf-8") as f:
                    all_eggs = json.load(f)
                    egg_info = {egg.get("identifier", egg["name"].lower()): egg for egg in all_eggs}
            except: egg_info = {}
            suggestions = []
            current_lower = current.lower()
            for egg_key in configured_eggs:
                egg = egg_info.get(egg_key, {})
                name = egg.get("name", egg_key.title())
                if current_lower in name.lower() or current_lower in egg_key:
                    rarity = egg.get("rarity", "")
                    emoji = {"Common": "🟢", "Uncommon": "🔵", "Rare": "🟣", "Epic": "🟠", "Legendary": "🟡", "Mythical": "🔴", "Divine": "✨"}.get(rarity, "🥚")
                    suggestions.append(app_commands.Choice(name=f"{emoji} {name}", value=egg_key))
            return suggestions[:25]
        except Exception as e:
            return [app_commands.Choice(name=f"❌ Erreur : {str(e)}", value="error")]

    @app_commands.command(name="test_ping", description="Test les pings de rôles")
    async def test_ping(self, interaction: discord.Interaction, role_id: str):
        await interaction.response.send_message(f"<@&{role_id}>", allowed_mentions=discord.AllowedMentions(roles=True))

async def setup(bot):
    await bot.add_cog(GrowAGardenRoles(bot))
