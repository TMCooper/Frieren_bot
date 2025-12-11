import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
DEV_ID = os.getenv('DEV_ID')

# Ensure imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from commands.System import System
from tests.mock_context import get_mock_interaction, get_mock_bot

import traceback

def log_error(e):
    with open("test_system_traceback.log", "a") as f:
        f.write(traceback.format_exc() + "\n")

class TestSystem(unittest.TestCase):
    def setUp(self):
        try:
            self.bot = get_mock_bot()
            self.cog = System(self.bot)
        except Exception as e:
            log_error(e)
            raise

    def test_ping(self):
        """Test ping command."""
        try:
            interaction = get_mock_interaction()
            # Mock latency
            self.bot.latency = 0.123 
            
            asyncio.run(self.cog.ping.callback(self.cog, interaction))
            
            interaction.response.send_message.assert_called()
            args, _ = interaction.response.send_message.call_args
            self.assertIn("123ms", args[0])
        except Exception as e:
            log_error(e)
            raise

    @patch('function.Holo.Holo.shutdown')
    def test_shutdown_authorized(self, mock_shutdown):
        """Test shutdown command with authorized user."""
        try:
            # Use simple IDs if env var not set or complex
            dev_id = int(DEV_ID) if DEV_ID else 123
            interaction = get_mock_interaction(user_id=dev_id)
            
            # We need to patch os.getenv in the module if we depend on it, 
            # but Holo.py loads it. 
            # For this test, we assume Holo.shutdown checks ID against env.
            # So we just mock Holo.shutdown to return True
            mock_shutdown.return_value = True
            
            asyncio.run(self.cog.shutdown.callback(self.cog, interaction))
            
            mock_shutdown.assert_called()
        except Exception as e:
            log_error(e)
            raise

    def test_shutdown_unauthorized(self):
        """Test shutdown command with unauthorized user."""
        try:
            # Something that definitely isn't the dev ID
            interaction = get_mock_interaction(user_id=0)
            
            # Since logic is delegating to Holo.shutdown which we can't easily run fully without killing process,
            # we really rely on patching Holo.shutdown for system tests, 
            # or checking the logic in the command (which just calls Holo).
            # The command itself is: await Holo.shutdown(self.bot, interaction.user.id, interaction)
            # So testing the cog mainly means testing it calls Holo.
            
            # Since shutdown is an async function in System cog, we should call it
            # But here we didn't patch Holo.shutdown, so calling it might actually try to kill process if logic allows?
            # Holo.shutdown checks ID. 0 != DEV_ID. So it should print "Unauthorized..." and return string.
            
            asyncio.run(self.cog.shutdown.callback(self.cog, interaction))
            pass 
        except Exception as e:
            log_error(e)
            raise

    @patch('function.Mita.Mita.debug_game')
    def test_games_file(self, mock_debug_game):
        """Test games_file command."""
        try:
            interaction = get_mock_interaction()
            mock_debug_game.return_value = True
            
            asyncio.run(self.cog.games_file.callback(self.cog, interaction))
            
            interaction.response.defer.assert_called()
            mock_debug_game.assert_called_with(interaction.user.id)
            interaction.followup.send.assert_called_with("Le fichier des jeux est accessible.")
        except Exception as e:
            log_error(e)
            raise

    @patch('function.Holo.Holo.reboot')
    def test_reboot(self, mock_reboot):
        try:
            interaction = get_mock_interaction()
            mock_reboot.return_value = "Redémarrage..."
            
            asyncio.run(self.cog.reboot.callback(self.cog, interaction))
            
            mock_reboot.assert_called()
        except Exception as e:
            log_error(e)
            raise

    @patch('function.Holo.Holo.update')
    def test_update_bot(self, mock_update):
        try:
            interaction = get_mock_interaction()
            mock_update.return_value = "Update..."
            
            asyncio.run(self.cog.update_bot.callback(self.cog, interaction))
            
            mock_update.assert_called()
        except Exception as e:
            log_error(e)
            raise

    def test_status(self):
        try:
            interaction = get_mock_interaction()
            asyncio.run(self.cog.status.callback(self.cog, interaction))
            interaction.response.defer.assert_called()
            interaction.followup.send.assert_called()
        except Exception as e:
            log_error(e)
            raise

    def test_info(self):
        try:
            interaction = get_mock_interaction()
            asyncio.run(self.cog.info.callback(self.cog, interaction))
            interaction.response.defer.assert_called()
            interaction.followup.send.assert_called()
        except Exception as e:
            log_error(e)
            raise

    def test_dashboard(self):
        try:
            interaction = get_mock_interaction()
            asyncio.run(self.cog.dashboard.callback(self.cog, interaction))
            interaction.response.defer.assert_called()
            interaction.followup.send.assert_called()
        except Exception as e:
            log_error(e)
            raise

    def test_list_roles(self):
        try:
            interaction = get_mock_interaction()
            role = MagicMock()
            role.name = "Role1"
            role.id = 1
            role.mentionable = True
            interaction.guild.roles = [role]
            
            asyncio.run(self.cog.list_roles.callback(self.cog, interaction))
            
            interaction.response.defer.assert_called()
            interaction.followup.send.assert_called()
        except Exception as e:
            log_error(e)
            raise

    @patch('function.Yui.Yui.simpleRequest')
    def test_ping_url(self, mock_request):
        try:
            interaction = get_mock_interaction()
            mock_request.return_value = "Pong"
            
            asyncio.run(self.cog.ping_url.callback(self.cog, interaction, url="http://test.com"))
            
            interaction.response.defer.assert_called()
            interaction.followup.send.assert_called_with("Pong")
        except Exception as e:
            log_error(e)
            raise

    @patch('function.Holo.Holo.changeStatus')
    def test_changestatus(self, mock_change):
        try:
            interaction = get_mock_interaction()
            choice = MagicMock()
            choice.value = "online"
            choice.name = "Online"
            
            asyncio.run(self.cog.changeStatus.callback(self.cog, interaction, status=choice))
            
            mock_change.assert_called()
            interaction.followup.send.assert_called()
        except Exception as e:
            log_error(e)
            raise

    @patch('function.Holo.Holo.changeActivity')
    def test_changeactivity(self, mock_change):
        try:
            interaction = get_mock_interaction()
            choice = MagicMock()
            choice.value = "playing"
            
            asyncio.run(self.cog.changeActivity.callback(self.cog, interaction, activite=choice, nom="Game"))
            
            mock_change.assert_called()
        except Exception as e:
            log_error(e)
            raise

if __name__ == '__main__':
    unittest.main()
