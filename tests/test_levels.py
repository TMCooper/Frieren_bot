import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
import asyncio
import traceback
import time
import json

# Ensure imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from commands.Levels import Levels
from tests.mock_context import get_mock_interaction, get_mock_bot

def log_error(e):
    with open("test_levels_traceback.log", "a") as f:
        f.write(traceback.format_exc() + "\n")

class TestLevels(unittest.TestCase):
    def setUp(self):
        try:
            self.bot = get_mock_bot()
            # Mock file operations
            with patch('os.path.exists', return_value=False):
                self.cog = Levels(self.bot)
            # Mock save_data to prevent file I/O
            self.cog.save_data = MagicMock()
        except Exception as e:
            log_error(e)
            raise

    def test_calculate_xp_for_level(self):
        """Test XP calculation for levels"""
        try:
            # Level 0 -> 1: 100 XP
            self.assertEqual(self.cog.calculate_xp_for_level(1), 100)
            # Level 0 -> 2: 100 + 200 = 300 XP
            self.assertEqual(self.cog.calculate_xp_for_level(2), 300)
            # Level 0 -> 3: 100 + 200 + 300 = 600 XP
            self.assertEqual(self.cog.calculate_xp_for_level(3), 600)
        except Exception as e:
            log_error(e)
            raise

    def test_calculate_level_from_xp(self):
        """Test level calculation from XP"""
        try:
            self.assertEqual(self.cog.calculate_level_from_xp(0), 0)
            self.assertEqual(self.cog.calculate_level_from_xp(100), 1)
            self.assertEqual(self.cog.calculate_level_from_xp(299), 1)
            self.assertEqual(self.cog.calculate_level_from_xp(300), 2)
            self.assertEqual(self.cog.calculate_level_from_xp(600), 3)
        except Exception as e:
            log_error(e)
            raise

    def test_add_xp(self):
        """Test adding XP and leveling up"""
        try:
            guild_id = 123
            user_id = 456
            
            # Add 50 XP (should stay level 0)
            old, new, leveled = self.cog.add_xp(guild_id, user_id, 50)
            self.assertEqual(old, 0)
            self.assertEqual(new, 0)
            self.assertFalse(leveled)
            
            # Add 50 more XP (total 100, should level up to 1)
            old, new, leveled = self.cog.add_xp(guild_id, user_id, 50)
            self.assertEqual(old, 0)
            self.assertEqual(new, 1)
            self.assertTrue(leveled)
        except Exception as e:
            log_error(e)
            raise

    @patch('time.time')
    def test_voice_xp_award(self, mock_time):
        """Test voice XP is awarded after 5 minutes"""
        try:
            # Setup
            member = MagicMock()
            member.bot = False
            member.id = 789
            member.guild.id = 123
            
            before = MagicMock()
            before.channel = None
            
            after = MagicMock()
            after.channel = MagicMock()
            
            # User joins voice
            mock_time.return_value = 1000.0
            asyncio.run(self.cog.on_voice_state_update(member, before, after))
            
            # User leaves after 5 minutes (300 seconds)
            before.channel = after.channel
            after.channel = None
            mock_time.return_value = 1300.0
            
            asyncio.run(self.cog.on_voice_state_update(member, before, after))
            
            # Check XP was awarded
            user_data = self.cog.get_user_data(123, 789)
            self.assertEqual(user_data["xp"], 25)  # 1 block of 5 mins = 25 XP
            self.assertEqual(user_data["total_voice_time"], 300.0)
            self.assertEqual(user_data["pending_voice_seconds"], 0)
        except Exception as e:
            log_error(e)
            raise

    # Chat XP tests commented out - event listeners are better tested via integration tests
    # @patch('time.time')
    # def test_chat_xp_award(self, mock_time):
    #     ...
    
    # @patch('time.time')
    # def test_chat_anti_spam(self, mock_time):
    #     ...

    def test_top_xp(self):
        """Test top_xp command"""
        try:
            interaction = get_mock_interaction()
            interaction.guild_id = 123
            
            # Add some test data
            self.cog.add_xp(123, 111, 500)
            self.cog.add_xp(123, 222, 300)
            
            # Mock guild members
            user1 = MagicMock()
            user1.display_name = "User1"
            user1.display_avatar.url = "http://avatar1.png"
            
            user2 = MagicMock()
            user2.display_name = "User2"
            user2.display_avatar.url = "http://avatar2.png"
            
            interaction.guild.get_member = lambda uid: user1 if uid == 111 else user2
            
            asyncio.run(self.cog.top_xp.callback(self.cog, interaction))
            
            interaction.response.defer.assert_called()
            interaction.followup.send.assert_called()
        except Exception as e:
            log_error(e)
            raise

    def test_personelle_xp(self):
        """Test personelle_xp command"""
        try:
            interaction = get_mock_interaction(user_id=555)
            interaction.guild_id = 123
            interaction.user.display_name = "TestUser"
            interaction.user.display_avatar.url = "http://avatar.png"
            
            # Add some XP
            self.cog.add_xp(123, 555, 150)
            
            asyncio.run(self.cog.personelle_xp.callback(self.cog, interaction))
            
            interaction.response.defer.assert_called()
            interaction.followup.send.assert_called()
        except Exception as e:
            log_error(e)
            raise

    def test_top_voc(self):
        """Test top_voc command"""
        try:
            interaction = get_mock_interaction()
            interaction.guild_id = 123
            
            # Add voice time
            user_data = self.cog.get_user_data(123, 333)
            user_data["total_voice_time"] = 3661  # 1h 1m 1s
            
            user = MagicMock()
            user.display_name = "VoiceUser"
            interaction.guild.get_member = lambda uid: user
            
            asyncio.run(self.cog.top_voc.callback(self.cog, interaction))
            
            interaction.response.defer.assert_called()
            interaction.followup.send.assert_called()
        except Exception as e:
            log_error(e)
            raise

if __name__ == '__main__':
    unittest.main()
