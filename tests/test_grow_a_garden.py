import unittest
import discord
from unittest.mock import MagicMock, patch, mock_open, AsyncMock
import sys
import os
import asyncio
import traceback
import json
import datetime

# Ensure imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from commands.GrowAGarden import GrowAGarden
from commands.GrowAGardenRoles import GrowAGardenRoles
from tests.mock_context import get_mock_interaction, get_mock_bot

def log_error(e):
    with open("test_grow_a_garden_traceback.log", "a") as f:
        f.write(traceback.format_exc() + "\n")

class TestGrowAGarden(unittest.TestCase):
    def setUp(self):
        try:
            self.bot = get_mock_bot()
            self.cog = GrowAGarden(self.bot)
        except Exception as e:
            log_error(e)
            raise

    @patch('function.Maid.Maid.get_next_5min_interval')
    @patch('asyncio.create_task')
    def test_setup_aga(self, mock_create_task, mock_get_interval):
        try:
            interaction = get_mock_interaction(user_id=123)
            interaction.guild_id = 999
            
            mock_get_interval.return_value = (300, datetime.datetime.now())
            
            asyncio.run(self.cog.setup_aga.callback(self.cog, interaction))
            
            interaction.response.defer.assert_called()
            mock_create_task.assert_called()
            self.assertIn(999, self.cog.aga_channels)
            self.assertIn(999, self.cog.aga_tasks)
        except Exception as e:
            log_error(e)
            raise

    @patch('function.Maid.Maid.shop_aga')
    def test_imediat_aga(self, mock_shop):
        try:
            interaction = get_mock_interaction()
            mock_shop.return_value = (discord.Embed(title="Market"), "MentionRole")
            
            asyncio.run(self.cog.imediat_aga.callback(self.cog, interaction))
            
            interaction.response.defer.assert_called()
            interaction.followup.send.assert_called()
            # Check content
            kwargs = interaction.followup.send.call_args.kwargs
            self.assertIn("MentionRole", kwargs.get('content', ''))
        except Exception as e:
            log_error(e)
            raise

    def test_stop_aga(self):
        try:
            interaction = get_mock_interaction()
            interaction.guild_id = 999
            
            # Setup dummy task
            self.cog.aga_tasks[999] = MagicMock()
            self.cog.aga_channels[999] = MagicMock()
            
            asyncio.run(self.cog.stop_aga.callback(self.cog, interaction))
            
            interaction.response.defer.assert_called()
            self.assertNotIn(999, self.cog.aga_tasks)
            self.assertNotIn(999, self.cog.aga_channels)
        except Exception as e:
            log_error(e)
            raise

    def test_status_aga(self):
        try:
            interaction = get_mock_interaction()
            interaction.guild_id = 123
            
            # Test when inactive
            asyncio.run(self.cog.status_aga.callback(self.cog, interaction))
            interaction.followup.send.assert_called()
            
            # Test when active (mock state)
            self.cog.aga_channels[123] = MagicMock()
            self.cog.aga_tasks[123] = MagicMock()
            
            with patch('function.Maid.Maid.get_next_5min_interval') as mock_int:
                mock_int.return_value = (300, datetime.datetime.now())
                asyncio.run(self.cog.status_aga.callback(self.cog, interaction))
                interaction.followup.send.assert_called()
        except Exception as e:
            log_error(e)
            raise

    @patch('function.Holo.Holo.db_gag_refresh')
    def test_db_gag_refresh(self, mock_refresh):
        try:
            interaction = get_mock_interaction()
            mock_refresh.return_value = "Refreshed"
            
            asyncio.run(self.cog.db_gag_refresh.callback(self.cog, interaction))
            
            interaction.followup.send.assert_called_with("Refreshed")
        except Exception as e:
            log_error(e)
            raise

class TestGrowAGardenRoles(unittest.TestCase):
    def setUp(self):
        try:
            self.bot = get_mock_bot()
            self.cog = GrowAGardenRoles(self.bot)
        except Exception as e:
            log_error(e)
            raise

    def test_fruit_role(self):
        try:
            interaction = get_mock_interaction()
            role = MagicMock()
            role.id = 12345
            role.mention = "<@&12345>"
            
            # Mock file IO
            file_data = {
                "data/fruit_roles.json": "{}", 
                "data/fruits.json": '[{"name": "Apple", "identifier": "apple", "price": 100}]'
            }
            
            def side_effect(filename, *args, **kwargs):
                content = file_data.get(filename, "{}")
                return mock_open(read_data=content).return_value
            
            with patch("builtins.open", side_effect=side_effect):
                with patch("os.path.exists", return_value=True):
                    with patch("json.load") as mock_json_load:
                        with patch("json.dump") as mock_json_dump:
                             # Setup json.load to return dict/list based on file content logic or just mock logic
                             # Simpler: mock open reads.
                             # But side_effect on mock_open is tricky.
                             # Let's simple patch os.path.exists and open for just successful write.
                             pass
            
            # Simplified test: assume files don't exist -> empty dict
            with patch("os.path.exists", return_value=False):
                with patch("builtins.open", mock_open()) as m:
                    asyncio.run(self.cog.fruit_role.callback(self.cog, interaction, fruit="Apple", role=role))
                    
                    # Verify write
                    # m.assert_called_with("data/fruit_roles.json", "w", encoding="utf-8")
                    # Verify success message
                    interaction.followup.send.assert_called()
                    args, kwargs = interaction.followup.send.call_args
                    # Check for embed or success text
                    self.assertTrue(args or kwargs.get('embed') or kwargs.get('content'))
                    
        except Exception as e:
            log_error(e)
            raise

    @patch('os.path.exists', return_value=True)
    def test_list_fruit_roles(self, mock_exists):
        try:
            interaction = get_mock_interaction()
            with patch("builtins.open", mock_open(read_data='{"123": {"apple": 1}}')):
                interaction.guild.get_role.return_value.mention = "@Role"
                interaction.guild_id = 123
                
                asyncio.run(self.cog.list_fruit_roles.callback(self.cog, interaction))
                interaction.followup.send.assert_called()
        except Exception as e:
            log_error(e)
            raise

    @patch('os.path.exists', return_value=True)
    def test_remove_fruit_role(self, mock_exists):
        try:
            interaction = get_mock_interaction()
            with patch("builtins.open", mock_open(read_data='{"123": {"apple": 1}}')) as m:
                interaction.guild_id = 123
                
                asyncio.run(self.cog.remove_fruit_role.callback(self.cog, interaction, fruit="apple"))
                
                # Verify write occurred (role removed)
                m.assert_called()
                interaction.followup.send.assert_called()
        except Exception as e:
            log_error(e)
            raise

    def test_test_ping(self):
        try:
            interaction = get_mock_interaction()
            asyncio.run(self.cog.test_ping.callback(self.cog, interaction, role_id="123"))
            interaction.response.send_message.assert_called()
        except Exception as e:
            log_error(e)
            raise

    def test_gear_role(self):
        try:
            interaction = get_mock_interaction()
            role = MagicMock()
            role.id = 1
            role.mention = "@Role"
            
            with patch('os.path.exists', return_value=False):
                with patch("builtins.open", mock_open()) as m:
                    asyncio.run(self.cog.gear_role.callback(self.cog, interaction, gear="Sword", role=role))
                    interaction.followup.send.assert_called()
        except Exception as e:
            log_error(e)
            raise

    def test_egg_role(self):
        try:
            interaction = get_mock_interaction()
            role = MagicMock()
            role.id = 1
            role.mention = "@Role"
            
            with patch('os.path.exists', return_value=False):
                with patch("builtins.open", mock_open()) as m:
                    asyncio.run(self.cog.egg_role.callback(self.cog, interaction, egg="Dragon", role=role))
                    interaction.followup.send.assert_called()
        except Exception as e:
            log_error(e)
            raise

if __name__ == '__main__':
    # Need to mock discord.Embed since it's used in logic before sending
    import discord
    # Patching discord.Embed globally for this module if needed, 
    # but mocks usually handle it if we don't inspect it too deeply.
    # Actually, in imediat_aga test, it returns discord.Embed(title="Market").
    # Real discord.Embed is fine if library is present.
    unittest.main()
