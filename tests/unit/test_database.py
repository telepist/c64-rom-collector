"""
Unit tests for the database operations.
"""
import unittest
import sqlite3
import os
import tempfile
from src.db.database import DatabaseManager
from src.db.game_repository import GameRepository


class TestDatabaseManager(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary database for testing
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        self.db = DatabaseManager(self.temp_db_path)
        self.db.connect()
        self.repository = GameRepository(self.db)
        
    def tearDown(self):
        # Close and remove the temporary database
        self.db.close()
        os.close(self.temp_db_fd)
        os.unlink(self.temp_db_path)
        
    def test_create_schema(self):
        # Test creating the database schema
        self.repository.db_manager.create_schema()
        
        # Verify tables were created
        self.repository.db_manager.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in self.repository.db_manager.fetchall()]
        self.assertIn("games", tables)
        self.assertIn("game_versions", tables)
        self.assertIn("game_parts", tables)
        
        # Verify indexes were created
        self.repository.db_manager.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in self.repository.db_manager.fetchall()]
        self.assertIn("idx_games_clean_name", indexes)
        self.assertIn("idx_versions_format", indexes)
        self.assertIn("idx_versions_game_id", indexes)
        self.assertIn("idx_versions_collection", indexes)
        self.assertIn("idx_versions_format_priority", indexes)
        self.assertIn("idx_parts_version_id", indexes)
        self.assertIn("idx_parts_part_number", indexes)
        
    def test_reset_schema(self):
        # Create some test data
        self.repository.db_manager.create_schema()
        
        # Insert a game with one part
        self.repository.db_manager.execute("INSERT INTO games (clean_name) VALUES (?)", ("Game",))
        game_id = self.repository.db_manager.cursor.lastrowid
        
        self.repository.db_manager.execute("""
            INSERT INTO game_versions (
                game_id, collection, format, format_priority
            ) VALUES (?, ?, ?, ?)""",
            (game_id, "Collection1", "crt", 3))
        version_id = self.repository.db_manager.cursor.lastrowid
        
        self.repository.db_manager.execute("""
            INSERT INTO game_parts (
                version_id, part_number, source_path, original_name
            ) VALUES (?, ?, ?, ?)""",
            (version_id, 0, "path/to/game.crt", "Game.crt"))
        self.repository.db_manager.commit()
        
        # Verify data was inserted
        self.repository.db_manager.execute("SELECT COUNT(*) FROM games")
        self.assertEqual(self.repository.db_manager.fetchone()[0], 1)
        self.repository.db_manager.execute("SELECT COUNT(*) FROM game_versions")
        self.assertEqual(self.repository.db_manager.fetchone()[0], 1)
        self.repository.db_manager.execute("SELECT COUNT(*) FROM game_parts")
        self.assertEqual(self.repository.db_manager.fetchone()[0], 1)
        
        # Reset schema
        self.repository.db_manager.reset_schema()
        
        # Verify tables are empty
        self.repository.db_manager.execute("SELECT COUNT(*) FROM games")
        self.assertEqual(self.repository.db_manager.fetchone()[0], 0)
        self.repository.db_manager.execute("SELECT COUNT(*) FROM game_versions")
        self.assertEqual(self.repository.db_manager.fetchone()[0], 0)
        self.repository.db_manager.execute("SELECT COUNT(*) FROM game_parts")
        self.assertEqual(self.repository.db_manager.fetchone()[0], 0)
        
    def test_insert_game(self):
        # Create schema
        self.repository.db_manager.create_schema()
        
        # Insert a game
        game_data = {
            'source_path': 'path/to/game.crt',
            'original_name': 'Game.crt',
            'clean_name': 'Game',
            'format': 'crt',
            'collection': 'Collection1',
            'format_priority': 3,
            'part_number': 0
        }
        game_id, version_id, part_id = self.repository.insert_game(game_data)
        
        # Verify the game was inserted
        self.assertTrue(game_id > 0)
        self.assertTrue(version_id > 0)
        self.assertTrue(part_id > 0)
        
        # Check game record
        self.repository.db_manager.execute("SELECT clean_name FROM games WHERE id = ?", (game_id,))
        result = self.repository.db_manager.fetchone()
        self.assertEqual(result[0], 'Game')
        
        # Check version record
        self.repository.db_manager.execute("""
            SELECT format, collection, format_priority
            FROM game_versions WHERE id = ?""", (version_id,))
        result = self.repository.db_manager.fetchone()
        self.assertEqual(result[0], 'crt')
        self.assertEqual(result[1], 'Collection1')
        self.assertEqual(result[2], 3)
        
        # Check part record
        self.repository.db_manager.execute("""
            SELECT source_path, original_name, part_number
            FROM game_parts WHERE id = ?""", (part_id,))
        result = self.repository.db_manager.fetchone()
        self.assertEqual(result[0], 'path/to/game.crt')
        self.assertEqual(result[1], 'Game.crt')
        self.assertEqual(result[2], 0)
        
    def test_insert_multi_part_game(self):
        """Test inserting a multi-part game"""
        self.repository.db_manager.create_schema()
        
        # Insert first part
        game_data1 = {
            'source_path': 'path/to/game_disk1.d64',
            'original_name': 'Game (Disk 1).d64',
            'clean_name': 'Game',
            'format': 'd64',
            'collection': 'Collection1',
            'format_priority': 2,
            'part_number': 1
        }
        game_id1, version_id1, part_id1 = self.repository.insert_game(game_data1)
        
        # Insert second part (should use same game and version)
        game_data2 = dict(game_data1)
        game_data2.update({
            'source_path': 'path/to/game_disk2.d64',
            'original_name': 'Game (Disk 2).d64',
            'part_number': 2
        })
        game_id2, version_id2, part_id2 = self.repository.insert_game(game_data2)
        
        # Verify both parts use the same game and version
        self.assertEqual(game_id1, game_id2)
        self.assertEqual(version_id1, version_id2)
        self.assertNotEqual(part_id1, part_id2)
        
        # Check we have one game, one version, but two parts
        self.repository.db_manager.execute("SELECT COUNT(*) FROM games")
        self.assertEqual(self.repository.db_manager.fetchone()[0], 1)
        self.repository.db_manager.execute("SELECT COUNT(*) FROM game_versions")
        self.assertEqual(self.repository.db_manager.fetchone()[0], 1)
        self.repository.db_manager.execute("SELECT COUNT(*) FROM game_parts")
        self.assertEqual(self.repository.db_manager.fetchone()[0], 2)
        
        # Check part numbers are correct
        self.repository.db_manager.execute("""
            SELECT part_number, original_name FROM game_parts 
            WHERE version_id = ? ORDER BY part_number""", (version_id1,))
        parts = self.repository.db_manager.fetchall()
        self.assertEqual(len(parts), 2)
        self.assertEqual(parts[0][0], 1)
        self.assertEqual(parts[1][0], 2)
        
    def test_insert_duplicate_version(self):
        """Test inserting the same game version twice"""
        self.repository.db_manager.create_schema()
        
        # First insert
        game_data1 = {
            'source_path': 'path1/game.crt',
            'original_name': 'Game.crt',
            'clean_name': 'Game',
            'format': 'crt',
            'collection': 'Collection1',
            'format_priority': 3,
            'part_number': 0
        }
        game_id1, version_id1, part_id1 = self.repository.insert_game(game_data1)
        
        # Second insert (same game, same collection and format)
        game_data2 = dict(game_data1)
        game_data2['source_path'] = 'path2/game.crt'
        game_id2, version_id2, part_id2 = self.repository.insert_game(game_data2)
        
        # Should use same game and version
        self.assertEqual(game_id1, game_id2)
        self.assertEqual(version_id1, version_id2)
        self.assertNotEqual(part_id1, part_id2)
        
        # Check we have one game, one version, but two parts
        self.repository.db_manager.execute("SELECT COUNT(*) FROM games")
        self.assertEqual(self.repository.db_manager.fetchone()[0], 1)
        self.repository.db_manager.execute("SELECT COUNT(*) FROM game_versions")
        self.assertEqual(self.repository.db_manager.fetchone()[0], 1)
        self.repository.db_manager.execute("SELECT COUNT(*) FROM game_parts")
        self.assertEqual(self.repository.db_manager.fetchone()[0], 2)
        
    def test_get_best_versions(self):
        """Test getting the best version of each game."""
        self.repository.db_manager.create_schema()
        
        # Insert a single part game with multiple versions
        game_data1 = {
            'source_path': 'path/to/game.crt',
            'original_name': 'Game.crt',
            'clean_name': 'Game',
            'format': 'crt',
            'collection': 'Collection1',
            'format_priority': 3,
            'part_number': 0
        }
        self.repository.insert_game(game_data1)
        
        # Insert same game but lower priority format
        game_data2 = dict(game_data1)
        game_data2.update({
            'source_path': 'path/to/game.tap',
            'original_name': 'Game.tap',
            'format': 'tap',
            'format_priority': 1
        })
        self.repository.insert_game(game_data2)
        
        # Insert a multi-part game
        game_data3 = {
            'source_path': 'path/to/game2_disk1.d64',
            'original_name': 'Game2 (Disk 1).d64',
            'clean_name': 'Game2',
            'format': 'd64',
            'collection': 'Collection1',
            'format_priority': 2,
            'part_number': 1
        }
        self.repository.insert_game(game_data3)
        
        game_data4 = dict(game_data3)
        game_data4.update({
            'source_path': 'path/to/game2_disk2.d64',
            'original_name': 'Game2 (Disk 2).d64',
            'part_number': 2
        })
        self.repository.insert_game(game_data4)
        
        # Get best versions
        best_versions = self.repository.get_best_versions()
        
        # Convert results to list for easier assertion
        results = list(best_versions)
        self.assertEqual(len(results), 3)  # Game + Game2 (2 parts)
        
        # First result should be Game.crt (highest priority)
        self.assertEqual(results[0][0], 'Game')  # clean_name
        self.assertEqual(results[0][1], 'crt')   # format
        
        # Second and third results should be Game2 disk parts
        self.assertEqual(results[1][0], 'Game2')  # clean_name
        self.assertEqual(results[1][1], 'd64')    # format
        self.assertEqual(results[1][3], 1)        # part_number
        
        self.assertEqual(results[2][0], 'Game2')  # clean_name
        self.assertEqual(results[2][1], 'd64')    # format
        self.assertEqual(results[2][3], 2)        # part_number


if __name__ == '__main__':
    unittest.main()
