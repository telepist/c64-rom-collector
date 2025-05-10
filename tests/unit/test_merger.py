"""
Unit tests for the merger module.
"""
import unittest
import os
import tempfile
import sqlite3
from c64collector.core.merger import generate_merge_script


class TestMerger(unittest.TestCase):
    
    def setUp(self):
        # Create temporary database and output file
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        self.temp_script_fd, self.temp_script_path = tempfile.mkstemp(suffix=".sh")
        self.target_dir = "test_target"
        
        # Close the file descriptors
        os.close(self.temp_db_fd)
        os.close(self.temp_script_fd)
        
        # Set up test database
        self._setup_test_database()
        
    def tearDown(self):
        # Remove temporary files
        os.unlink(self.temp_db_path)
        os.unlink(self.temp_script_path)
        
    def _setup_test_database(self):
        """Set up a test database with sample data."""
        conn = sqlite3.connect(self.temp_db_path)
        cursor = conn.cursor()
        
        # Create schema
        cursor.execute('''CREATE TABLE games (
            id INTEGER PRIMARY KEY,
            clean_name TEXT NOT NULL
        )''')
        cursor.execute('''CREATE TABLE game_versions (
            id INTEGER PRIMARY KEY,
            game_id INTEGER NOT NULL,
            collection TEXT NOT NULL,
            format TEXT NOT NULL,
            format_priority INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (game_id) REFERENCES games(id)
        )''')
        cursor.execute('''CREATE TABLE game_parts (
            id INTEGER PRIMARY KEY,
            version_id INTEGER NOT NULL,
            part_number INTEGER NOT NULL DEFAULT 0,
            source_path TEXT NOT NULL,
            original_name TEXT NOT NULL,
            FOREIGN KEY (version_id) REFERENCES game_versions(id)
        )''')
        
        # Insert single part game in Collection1 (highest priority)
        cursor.execute('INSERT INTO games (clean_name) VALUES (?)', ('Game1',))
        game1_id = cursor.lastrowid
        cursor.execute('''INSERT INTO game_versions (game_id, collection, format, format_priority) 
                         VALUES (?, ?, ?, ?)''', (game1_id, 'Collection1', 'crt', 3))
        version1_id = cursor.lastrowid
        cursor.execute('''INSERT INTO game_parts (version_id, part_number, source_path, original_name) 
                         VALUES (?, ?, ?, ?)''', 
                         (version1_id, 0, 'src/Collection1/Game1.crt', 'Game1.crt'))
        
        # Insert same game in Collection2 (lower priority)
        cursor.execute('''INSERT INTO game_versions (game_id, collection, format, format_priority) 
                         VALUES (?, ?, ?, ?)''', (game1_id, 'Collection2', 'crt', 3))
        version2_id = cursor.lastrowid
        cursor.execute('''INSERT INTO game_parts (version_id, part_number, source_path, original_name) 
                         VALUES (?, ?, ?, ?)''', 
                         (version2_id, 0, 'src/Collection2/Game1 (USA).crt', 'Game1 (USA).crt'))
        
        # Insert single part game 2
        cursor.execute('INSERT INTO games (clean_name) VALUES (?)', ('Game2',))
        game2_id = cursor.lastrowid
        cursor.execute('''INSERT INTO game_versions (game_id, collection, format, format_priority) 
                         VALUES (?, ?, ?, ?)''', (game2_id, 'Collection1', 'd64', 2))
        version3_id = cursor.lastrowid
        cursor.execute('''INSERT INTO game_parts (version_id, part_number, source_path, original_name) 
                         VALUES (?, ?, ?, ?)''', 
                         (version3_id, 0, 'src/Collection1/Game2 (Europe).d64', 'Game2 (Europe).d64'))
        
        # Insert multi part game 3
        cursor.execute('INSERT INTO games (clean_name) VALUES (?)', ('Game3',))
        game3_id = cursor.lastrowid
        cursor.execute('''INSERT INTO game_versions (game_id, collection, format, format_priority) 
                         VALUES (?, ?, ?, ?)''', (game3_id, 'Collection1', 'tap', 1))
        version4_id = cursor.lastrowid
        cursor.execute('''INSERT INTO game_parts (version_id, part_number, source_path, original_name) 
                         VALUES (?, ?, ?, ?)''', 
                         (version4_id, 1, 'src/Collection1/Game3 (Disk 1).tap', 'Game3 (Disk 1).tap'))
        cursor.execute('''INSERT INTO game_parts (version_id, part_number, source_path, original_name) 
                         VALUES (?, ?, ?, ?)''', 
                         (version4_id, 2, 'src/Collection1/Game3 (Disk 2).tap', 'Game3 (Disk 2).tap'))
        
        conn.commit()
        conn.close()
        
    def test_generate_merge_script(self):
        """Test generating the merge script."""
        # Run the function
        file_count = generate_merge_script(self.temp_db_path, self.temp_script_path, self.target_dir)
        
        # Check result
        self.assertEqual(file_count, 4)  # 4 files total (2 single, 2 multi)
        
        # Check script content
        with open(self.temp_script_path, 'r') as f:
            content = f.read()
        
        # Verify script contains correct commands
        self.assertIn('mkdir -p "test_target"', content)
        self.assertIn('cp "src/Collection1/Game1.crt" "test_target/Game1.crt"', content)
        self.assertIn('cp "src/Collection1/Game2 (Europe).d64" "test_target/Game2.d64"', content)
        self.assertIn('mkdir -p "test_target/Game3"', content)
        self.assertIn('cp "src/Collection1/Game3 (Disk 1).tap" "test_target/Game3/Game3 (Part 1).tap"', content)
        self.assertIn('cp "src/Collection1/Game3 (Disk 2).tap" "test_target/Game3/Game3 (Part 2).tap"', content)
        
        # Make sure it's not using Collection2's version of Game1
        self.assertNotIn('cp "src/Collection2/Game1 (USA).crt" "test_target/Game1.crt"', content)


if __name__ == '__main__':
    unittest.main()
