"""
Unit tests for the verifier module.
"""
import unittest
import os
import tempfile
import sqlite3
import shutil
from c64collector.core.verifier import check_missing_files


class TestVerifier(unittest.TestCase):
    
    def setUp(self):
        # Create temporary directories and database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.target_dir = os.path.join(self.temp_dir, "target")
        
        # Create target directory
        os.makedirs(self.target_dir)
        
        # Set up test database and target files
        self._setup_test_database()
        self._create_target_files()
        
    def tearDown(self):
        try:
            # Force close any potential lingering connections
            try:
                conn = sqlite3.connect(self.db_path)
                conn.close()
            except:
                pass
                
            # Remove the temporary directory
            shutil.rmtree(self.temp_dir)
        except PermissionError:
            print("Warning: Unable to delete temporary files due to open database connections")
        
    def _setup_test_database(self):
        """Set up a test database with sample data."""
        conn = sqlite3.connect(self.db_path)
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
            
        cursor.execute('''INSERT INTO games 
            (source_path, original_name, clean_name, format, collection, format_priority, is_multi_part, part_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            ("src/Collection1/Game3.nib", "Game3.nib", "Game3", "nib", "Collection1", 2, 0, 0))
            
        # Insert multi-part game
        cursor.execute('''INSERT INTO games 
            (source_path, original_name, clean_name, format, collection, format_priority, is_multi_part, part_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            ("src/Collection1/Game4 (Disk 1).tap", "Game4 (Disk 1).tap", "Game4", "tap", "Collection1", 1, 1, 1))
            
        cursor.execute('''INSERT INTO games 
            (source_path, original_name, clean_name, format, collection, format_priority, is_multi_part, part_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            ("src/Collection1/Game4 (Disk 2).tap", "Game4 (Disk 2).tap", "Game4", "tap", "Collection1", 1, 1, 2))
        
        conn.commit()
        conn.close()
        
    def _create_target_files(self):
        """Create files in the target directory."""
        # Create some files (not all expected files)
        open(os.path.join(self.target_dir, "Game1.crt"), "w").close()
        open(os.path.join(self.target_dir, "Game2.d64"), "w").close()
        # Note: Game3.nib is missing
        open(os.path.join(self.target_dir, "Game4 (Disk 1).tap"), "w").close()
        # Note: Game4 (Disk 2).tap is missing
        
        # Create extra file that isn't in the database
        open(os.path.join(self.target_dir, "ExtraGame.d64"), "w").close()
        
    def test_check_missing_files(self):
        """Test checking for missing files."""
        # Run the verifier
        results = check_missing_files(self.db_path, self.target_dir)
        
        # Check results
        self.assertEqual(results['total_expected'], 5)  # 5 expected files (based on records in DB)
        self.assertEqual(results['total_actual'], 4)    # 4 actual files (including extra file)
        self.assertEqual(results['total_missing'], 2)   # 2 missing files
        
        # Check missing singles
        self.assertEqual(len(results['missing_singles']), 1)
        self.assertEqual(results['missing_singles'][0]['name'], "Game3.nib")
        
        # Check missing multi-parts
        self.assertEqual(len(results['missing_multis']), 1)
        self.assertEqual(results['missing_multis'][0]['name'], "Game4 (Disk 2).tap")


if __name__ == '__main__':
    unittest.main()
