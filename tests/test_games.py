import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import asyncio
import traceback
from dotenv import load_dotenv

load_dotenv()
DEV_ID = int(os.getenv('DEV_ID') or 0)

# Ensure imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from commands.Games import Games
from tests.mock_context import get_mock_interaction, get_mock_bot

def log_error(e):
    with open("test_games_traceback.log", "a") as f:
        f.write(traceback.format_exc() + "\n")

class TestGames(unittest.TestCase):
    def setUp(self):
        try:
            self.bot = get_mock_bot()
            self.cog = Games(self.bot)
        except Exception as e:
            log_error(e)
            raise

    @patch('function.Maid.Maid.valorant_tracker_rank')
    def test_valorant_rank(self, mock_val_rank):
        try:
            interaction = get_mock_interaction()
            mock_val_rank.return_value = "Diamond 1"
            
            asyncio.run(self.cog.valorant_rank.callback(self.cog, interaction, pseudo="Player", tag="EUW"))
            
            interaction.response.defer.assert_called()
            interaction.followup.send.assert_called_with("Le rank de Player#EUW est : Diamond 1")
        except Exception as e:
            log_error(e)
            raise

    @patch('function.Maid.Maid.scrap')
    def test_code(self, mock_scrap):
        try:
            interaction = get_mock_interaction()
            mock_scrap.return_value = "CODE123"
            
            choice = MagicMock()
            choice.value = "genshin"
            
            asyncio.run(self.cog.code.callback(self.cog, interaction, jeux_entrer=choice))
            
            interaction.response.defer.assert_called()
            interaction.followup.send.assert_called()
            args, _ = interaction.followup.send.call_args
            self.assertIn("CODE123", args[0])
        except Exception as e:
            log_error(e)
            raise

    @patch('function.Frieren.Frieren.speedrun_main')
    def test_speedrun(self, mock_speedrun):
        try:
            interaction = get_mock_interaction()
            # Mock return data structure
            mock_speedrun.return_value = {
                'Image URL': 'http://image.com',
                'Top Results': [
                    {'Rank': '1', 'Player': 'Speedster', 'Time': '1h 20m', 'Country': 'US', 'Date': '2025-01-01'}
                ]
            }
            
            asyncio.run(self.cog.speedrun.callback(self.cog, interaction, jeu="Celeste"))
            
            interaction.response.defer.assert_called()
            interaction.followup.send.assert_called()
            # Check embed
            _, kwargs = interaction.followup.send.call_args
            self.assertIn('embed', kwargs)
            self.assertIn("Celeste", kwargs['embed'].description)
        except Exception as e:
            log_error(e)
            raise

    @patch('function.Frieren.Frieren.speedrun_refresh')
    def test_refresh_speedrun_authorized(self, mock_refresh):
        try:
            # Authorized user
            interaction = get_mock_interaction(user_id=DEV_ID)
            mock_refresh.return_value = "Actualisation terminée"
            
            asyncio.run(self.cog.refresh_speedrun.callback(self.cog, interaction))
            
            interaction.response.defer.assert_called()
            interaction.followup.send.assert_called()
            # Check success embed or message
            _, kwargs = interaction.followup.send.call_args
            # The code sends an embed
            self.assertIn('embed', kwargs)
            self.assertIn("terminée", kwargs['embed'].description)

        except Exception as e:
            log_error(e)
            raise

    def test_refresh_speedrun_unauthorized(self):
        try:
            # Unauthorized user
            interaction = get_mock_interaction(user_id=DEV_ID + 1)
            
            asyncio.run(self.cog.refresh_speedrun.callback(self.cog, interaction))
            
            interaction.response.defer.assert_called()
            interaction.followup.send.assert_called_with("Vous n'êtes pas autorisé à utiliser cette commande.")
        except Exception as e:
            log_error(e)
            raise

if __name__ == '__main__':
    unittest.main()
