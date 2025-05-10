"""
Unit tests for the database operations.
"""
import unittest
import sqlite3
import os
import tempfile
from c64collector.db.database import DatabaseManager


class TestDatabaseManager(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary database for testing
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        self.db = DatabaseManager(self.temp_db_path)
        self.db.connect()
        
    def tearDown(self):
        # Close and remove the temporary database
        self.db.close()
        os.close(self.temp_db_fd)
        os.unlink(self.temp_db_path)
        
    def test_create_schema(self):
        # Test creating the database schema
        self.db.create_schema()
        
        # Verify tables were created
        self.db.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in self.db.fetchall()]
        self.assertIn("games", tables)
        
        # Verify indexes were created
        self.db.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in self.db.fetchall()]
        self.assertIn("idx_games_clean_name", indexes)
        self.assertIn("idx_games_format", indexes)
        
    def test_reset_schema(self):
        # Create some test data
        self.db.create_schema()
        self.db.execute("INSERT INTO games (source_path, original_name, clean_name, format, collection, format_priority) VALUES (?, ?, ?, ?, ?, ?)",
                      ("path/to/game.crt", "Game.crt", "Game", "crt", "Collection1", 3))
        self.db.commit()
        
        # Verify data was inserted
        self.db.execute("SELECT COUNT(*) FROM games")
        self.assertEqual(self.db.fetchone()[0], 1)
        
        # Reset schema
        self.db.reset_schema()
        
        # Verify table is empty
        self.db.execute("SELECT COUNT(*) FROM games")
        self.assertEqual(self.db.fetchone()[0], 0)
        
    def test_insert_game(self):
        # Create schema
        self.db.create_schema()
        
        # Insert a game
        game_data = {
            'source_path': 'path/to/game.crt',
            'original_name': 'Game.crt',
            'clean_name': 'Game',
            'format': 'crt',
            'collection': 'Collection1',
            'format_priority': 3,
            'is_multi_part': 0,
            'part_number': 0
        }
        row_id = self.db.insert_game(game_data)
        
        # Verify the game was inserted
        self.assertTrue(row_id > 0)
        self.db.execute("SELECT clean_name, format FROM games WHERE id = ?", (row_id,))
        result = self.db.fetchone()
        self.assertEqual(result[0], 'Game')
        self.assertEqual(result[1], 'crt')


if __name__ == '__main__':
    unittest.main()
