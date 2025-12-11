import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import asyncio

# Ensure imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from commands.General import General
from tests.mock_context import get_mock_interaction, get_mock_bot

import traceback

def log_error(e):
    with open("test_traceback.log", "a") as f:
        f.write(traceback.format_exc() + "\n")

class TestGeneral(unittest.TestCase):
    def setUp(self):
        try:
            self.bot = get_mock_bot()
            self.cog = General(self.bot)
        except Exception as e:
            log_error(e)
            raise

    def test_hello_no_member(self):
        """Test hello command without a member mention."""
        try:
            interaction = get_mock_interaction()
            # Run async function
            asyncio.run(self.cog.hello.callback(self.cog, interaction, None))
            interaction.response.send_message.assert_called_with("Veuillez mentionner un membre valide.", ephemeral=True)
        except Exception as e:
            log_error(e)
            raise

    def test_hello_with_member(self):
        """Test hello command with a member."""
        try:
            interaction = get_mock_interaction()
            member = MagicMock()
            member.mention = "<@0000>"
            
            asyncio.run(self.cog.hello.callback(self.cog, interaction, member))
            
            interaction.response.send_message.assert_called_with("Hello <@0000> :kiss:")
        except Exception as e:
            log_error(e)
            raise

    def test_hello_world(self):
        """Test hello_world command."""
        try:
            interaction = get_mock_interaction()
            asyncio.run(self.cog.hello_world.callback(self.cog, interaction))
            interaction.response.send_message.assert_called_with("Hello World")
        except Exception as e:
            log_error(e)
            raise

    def test_my_id(self):
        """Test my_id command."""
        try:
            interaction = get_mock_interaction(user_id=12345)
            asyncio.run(self.cog.my_id.callback(self.cog, interaction))
            interaction.response.defer.assert_called_once()
            interaction.followup.send.assert_called_with("Votre ID : 12345")
        except Exception as e:
            log_error(e)
            raise

    @patch('function.Holo.Holo.Translate')
    def test_translate(self, mock_translate):
        """Test translate command."""
        try:
            interaction = get_mock_interaction()
            
            # Mocking values
            phrase = "Bonjour"
            langue_choice = MagicMock()
            langue_choice.name = "Anglais"
            langue_choice.value = "en"
            
            # Mocking Holo.Translate return
            mock_translate.return_value = ("Hello", "həˈlō")
            
            asyncio.run(self.cog.translate.callback(self.cog, interaction, phrase, langues=langue_choice))
            
            interaction.response.defer.assert_called_once()
            mock_translate.assert_called_with(phrase, "en")
            interaction.followup.send.assert_called()
            # Verify the content of the sent message contains the translation
            args, _ = interaction.followup.send.call_args
            self.assertIn("Hello", args[0])
        except Exception as e:
            log_error(e)
            raise

if __name__ == '__main__':
    unittest.main()
