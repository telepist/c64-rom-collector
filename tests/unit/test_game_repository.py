"""Unit tests for game repository functionality."""
import unittest
import os
import tempfile
from db.database import DatabaseManager
from db.game_repository import GameRepository


class TestGameRepository(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        self.db_manager = DatabaseManager(self.temp_db_path)
        self.db_manager.connect()
        self.db_manager.create_schema()
        self.repository = GameRepository(self.db_manager)
        
        # Sample game data for testing
        self.game_data = {
            'source_path': 'path/to/game.crt',
            'original_name': 'Game.crt',
            'clean_name': 'Game',
            'format': 'crt',
            'collection': 'Collection1',
            'format_priority': 3,
            'part_number': 0
        }
        
    def tearDown(self):
        """Clean up test environment."""
        self.db_manager.close()
        os.close(self.temp_db_fd)
        os.unlink(self.temp_db_path)
        
    def test_add_game(self):
        """Test adding a new game."""
        game_id, version_id, part_id = self.repository.add_game(self.game_data)
        
        # Verify game was added
        self.assertIsNotNone(game_id)
        self.assertIsNotNone(version_id)
        self.assertIsNotNone(part_id)
        
        # Verify game details
        game = self.repository.get_game_by_name('Game')
        self.assertIsNotNone(game)
        self.assertEqual(game[1], 'Game')  # clean_name is the second column
        
    def test_insert_game_duplicate(self):
        """Test inserting the same game twice."""
        # Insert first time
        game_id1, version_id1, part_id1 = self.repository.insert_game(self.game_data)
        
        # Insert same game again with a different collection
        self.game_data['collection'] = 'Collection2'
        game_id2, version_id2, part_id2 = self.repository.insert_game(self.game_data)
        
        # Should use same game ID but different version ID
        self.assertEqual(game_id1, game_id2)
        self.assertNotEqual(version_id1, version_id2)
        self.assertNotEqual(part_id1, part_id2)
        
    def test_get_game_by_name(self):
        """Test retrieving a game by its clean name."""
        # Insert a game
        self.repository.insert_game(self.game_data)
        
        # Get the game
        game = self.repository.get_game_by_name('Game')
        self.assertIsNotNone(game)
        self.assertEqual(game[1], 'Game')  # clean_name is the second column
        
        # Test non-existent game
        game = self.repository.get_game_by_name('NonExistentGame')
        self.assertIsNone(game)
        
    def test_fetch_all_games(self):
        """Test fetching all games from the database."""
        # Insert multiple games
        games_data = [
            self.game_data,
            {**self.game_data, 'clean_name': 'Game2', 'original_name': 'Game2.crt'},
            {**self.game_data, 'clean_name': 'Game3', 'original_name': 'Game3.crt'}
        ]
        
        for data in games_data:
            self.repository.insert_game(data)
            
        # Fetch all games
        all_games = self.repository.fetch_all_games()
        
        # Verify number of games
        self.assertEqual(len(all_games), 3)
        
        # Verify game names
        game_names = sorted(game[1] for game in all_games)  # clean_name is the second column
        self.assertEqual(game_names, ['Game', 'Game2', 'Game3'])
        
    def test_reset_database(self):
        """Test resetting the database."""
        # Insert a game
        self.repository.insert_game(self.game_data)
        
        # Verify game exists
        self.assertIsNotNone(self.repository.get_game_by_name('Game'))
        
        # Reset database
        self.repository.reset_database()
        
        # Verify game no longer exists
        self.assertIsNone(self.repository.get_game_by_name('Game'))
        
    def test_get_best_versions(self):
        """Test retrieving the best version of each game."""
        # Insert a game with multiple versions
        game_data1 = self.game_data
        game_data2 = {**self.game_data, 'format': 'd64', 'format_priority': 2}
        game_data3 = {**self.game_data, 'clean_name': 'Game2', 'format': 'tap', 'format_priority': 1}
        
        self.repository.insert_game(game_data1)  # CRT version
        self.repository.insert_game(game_data2)  # D64 version
        self.repository.insert_game(game_data3)  # Another game
        
        # Get best versions
        best_versions = self.repository.get_best_versions()
        
        # Should have one entry per game (2 games total)
        game_formats = {(game[0], game[1]) for game in best_versions}  # (clean_name, format)
        self.assertEqual(game_formats, {('Game', 'crt'), ('Game2', 'tap')})


if __name__ == '__main__':
    unittest.main()
