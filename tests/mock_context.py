import sys
import os
from unittest.mock import MagicMock, AsyncMock

# Add project root to sys.path so we can import commands and functions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def get_mock_interaction(user_id=123456789):
    """Creates a mock discord.Interaction object."""
    mock_interaction = MagicMock()
    mock_interaction.response.defer = AsyncMock()
    mock_interaction.response.send_message = AsyncMock()
    mock_interaction.followup.send = AsyncMock()
    mock_interaction.user.id = user_id
    mock_interaction.user.mention = f"<@{user_id}>"
    mock_interaction.guild.name = "Test Guild"
    mock_interaction.channel.id = 987654321
    return mock_interaction

def get_mock_bot():
    """Creates a mock discord.ext.commands.Bot object."""
    mock_bot = MagicMock()
    return mock_bot
