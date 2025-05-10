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
            source_path TEXT NOT NULL,
            original_name TEXT NOT NULL,
            clean_name TEXT NOT NULL,
            format TEXT NOT NULL,
            collection TEXT NOT NULL,
            format_priority INTEGER NOT NULL DEFAULT 0,
            is_multi_part INTEGER NOT NULL DEFAULT 0,
            part_number INTEGER NOT NULL DEFAULT 0
        )''')
        
        # Insert single part games
        cursor.execute('''INSERT INTO games 
            (source_path, original_name, clean_name, format, collection, format_priority, is_multi_part, part_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            ("src/Collection1/Game1.crt", "Game1.crt", "Game1", "crt", "Collection1", 3, 0, 0))
            
        cursor.execute('''INSERT INTO games 
            (source_path, original_name, clean_name, format, collection, format_priority, is_multi_part, part_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            ("src/Collection2/Game1 (USA).crt", "Game1 (USA).crt", "Game1", "crt", "Collection2", 3, 0, 0))
            
        cursor.execute('''INSERT INTO games 
            (source_path, original_name, clean_name, format, collection, format_priority, is_multi_part, part_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            ("src/Collection1/Game2 (Europe).d64", "Game2 (Europe).d64", "Game2", "d64", "Collection1", 2, 0, 0))
            
        # Insert multi-part game
        cursor.execute('''INSERT INTO games 
            (source_path, original_name, clean_name, format, collection, format_priority, is_multi_part, part_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            ("src/Collection1/Game3 (Disk 1).tap", "Game3 (Disk 1).tap", "Game3", "tap", "Collection1", 1, 1, 1))
            
        cursor.execute('''INSERT INTO games 
            (source_path, original_name, clean_name, format, collection, format_priority, is_multi_part, part_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            ("src/Collection1/Game3 (Disk 2).tap", "Game3 (Disk 2).tap", "Game3", "tap", "Collection1", 1, 1, 2))
        
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
        self.assertIn('cp "src/Collection1/Game3 (Disk 1).tap" "test_target/Game3 (Disk 1).tap"', content)
        self.assertIn('cp "src/Collection1/Game3 (Disk 2).tap" "test_target/Game3 (Disk 2).tap"', content)
        
        # Make sure it's not using Collection2's version of Game1
        self.assertNotIn('cp "src/Collection2/Game1 (USA).crt" "test_target/Game1.crt"', content)


if __name__ == '__main__':
    unittest.main()
