import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
import asyncio
import traceback
import json

# Ensure imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from commands.Anime import Anime
from tests.mock_context import get_mock_interaction, get_mock_bot

def log_error(e):
    with open("test_anime_traceback.log", "a") as f:
        f.write(traceback.format_exc() + "\n")

class TestAnime(unittest.TestCase):
    def setUp(self):
        try:
            self.bot = get_mock_bot()
            self.cog = Anime(self.bot)
        except Exception as e:
            log_error(e)
            raise

    @patch('function.Maid.Maid.voiranime_scrap_catalogue')
    def test_anime_refresh(self, mock_scrap):
        try:
            interaction = get_mock_interaction()
            mock_scrap.return_value = "Catalogue mis à jour"
            
            asyncio.run(self.cog.anime_refresh.callback(self.cog, interaction))
            
            # Since mock returns a string, command body doesn't send anything if msg is not None based on the snippet.
            # Wait, looking at Anime.py: 
            # msg = await Maid...
            # if msg == None: send message. 
            # Else? It does NOTHING?
            # Looking at source code:
            # if msg == None: ...
            # No else block. So it does nothing if successful? That seems weird but ok.
            # Let's verify valid mock interaction doesn't fail.
            pass
        except Exception as e:
            log_error(e)
            raise

    def test_anime_search_found(self):
        try:
            interaction = get_mock_interaction()
            mock_data = [
                {"anime_name": "Naruto", "image_url": "http://img.com/naruto.jpg", "link": "http://link.com"}
            ]
            json_data = json.dumps(mock_data)
            
            with patch("builtins.open", mock_open(read_data=json_data)):
                asyncio.run(self.cog.anime_search.callback(self.cog, interaction, nom="Naruto"))
            
            interaction.followup.send.assert_called()
            _, kwargs = interaction.followup.send.call_args
            self.assertIn("embed", kwargs)
            self.assertIn("Naruto", kwargs['embed'].title)
        except Exception as e:
            log_error(e)
            raise
    
    def test_anime_search_not_found(self):
        try:
            interaction = get_mock_interaction()
            mock_data = []
            json_data = json.dumps(mock_data)
            
            with patch("builtins.open", mock_open(read_data=json_data)):
                asyncio.run(self.cog.anime_search.callback(self.cog, interaction, nom="Unknown"))
            
            interaction.followup.send.assert_called()
            args, _ = interaction.followup.send.call_args
            self.assertIn("Aucun anime trouvé", args[0])
        except Exception as e:
            log_error(e)
            raise

    @patch('function.Holo.Holo.purge_anime_file')
    def test_purge_anime_file(self, mock_purge):
        try:
            interaction = get_mock_interaction()
            
            asyncio.run(self.cog.purge_anime_file.callback(self.cog, interaction))
            
            interaction.response.defer.assert_called()
            mock_purge.assert_called_with(interaction.user.id, interaction)
        except Exception as e:
            log_error(e)
            raise

if __name__ == '__main__':
    unittest.main()
