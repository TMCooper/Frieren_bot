import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import asyncio
import traceback

# Ensure imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from commands.Fun import Fun
from tests.mock_context import get_mock_interaction, get_mock_bot

def log_error(e):
    with open("test_fun_traceback.log", "a") as f:
        f.write(traceback.format_exc() + "\n")

class TestFun(unittest.TestCase):
    def setUp(self):
        try:
            self.bot = get_mock_bot()
            self.cog = Fun(self.bot)
        except Exception as e:
            log_error(e)
            raise

    @patch('function.Eru.Eru.random_waifu')
    def test_waifu(self, mock_random_waifu):
        try:
            interaction = get_mock_interaction()
            # name, alternate_name, age, birthday, height, weight, blood_type, waifu_classification, description, like_rank, popularity_rank, image_url
            mock_random_waifu.return_value = (
                "Holo", "The Wise Wolf", "Unknown", "Unknown", "Unknown", "Unknown", "Unknown", "Deity", "Cute wolf girl", "1", "1", "http://example.com/holo.jpg"
            )
            
            asyncio.run(self.cog.waifu.callback(self.cog, interaction))
            
            interaction.response.defer.assert_called()
            interaction.followup.send.assert_called()
            # Check if embed was sent
            args, kwargs = interaction.followup.send.call_args
            self.assertIn('embed', kwargs)
            self.assertEqual(kwargs['embed'].title, "Holo")
        except Exception as e:
            log_error(e)
            raise

    @patch('function.Rias.Rias.rule34')
    def test_rule34(self, mock_rule34):
        try:
            interaction = get_mock_interaction()
            mock_rule34.return_value = "http://example.com/image.jpg"
            
            asyncio.run(self.cog.rule34.callback(self.cog, interaction, tags="holo"))
            
            interaction.response.defer.assert_called()
            interaction.followup.send.assert_called_with("http://example.com/image.jpg")
        except Exception as e:
            log_error(e)
            raise

if __name__ == '__main__':
    unittest.main()
