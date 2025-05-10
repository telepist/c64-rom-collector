"""
Integration tests for the importer module.
"""
import unittest
import os
import tempfile
import shutil
import sqlite3
from c64collector.core.importer import import_games


class TestImporter(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for src and temp db
        self.temp_dir = tempfile.mkdtemp()
        self.src_dir = os.path.join(self.temp_dir, "src")
        self.db_path = os.path.join(self.temp_dir, "test.db")
        
        # Create collection directories
        os.makedirs(os.path.join(self.src_dir, "Collection1"))
        os.makedirs(os.path.join(self.src_dir, "Collection2"))
        
        # Create test files
        self._create_test_files()
        
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
        
    def _create_test_files(self):
        """Create test game files."""
        # Collection 1
        open(os.path.join(self.src_dir, "Collection1", "Game1.crt"), "w").close()
        open(os.path.join(self.src_dir, "Collection1", "Game2 (Europe).d64"), "w").close()
        open(os.path.join(self.src_dir, "Collection1", "Game3 (Disk 1).tap"), "w").close()
        open(os.path.join(self.src_dir, "Collection1", "Game3 (Disk 2).tap"), "w").close()
        open(os.path.join(self.src_dir, "Collection1", "BIOS.crt"), "w").close()  # Should be skipped
        
        # Collection 2
        open(os.path.join(self.src_dir, "Collection2", "Game1 (USA).crt"), "w").close()
        open(os.path.join(self.src_dir, "Collection2", "Game4.nib"), "w").close()
        open(os.path.join(self.src_dir, "Collection2", "Game5.txt"), "w").close()  # Should be skipped
        
    def test_import_games(self):
        """Test the import_games function."""
        # Run the importer
        stats = import_games(self.src_dir, self.db_path)
        
        # Check statistics
        self.assertEqual(stats['processed_files'], 6)  # 6 valid game files
        self.assertEqual(stats['skipped_files'], 2)    # 2 skipped files
        self.assertEqual(stats['unique_games'], 4)     # 4 unique games
        self.assertEqual(stats['multi_games'], 1)      # 1 multi-part game
        
        # Check database contents
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Check games table
        c.execute("SELECT COUNT(*) FROM games")
        self.assertEqual(c.fetchone()[0], 6)  # 6 total records (3 singles + 2 multi parts + 1 duplicate)
        
        # Check clean names
        c.execute("SELECT DISTINCT clean_name FROM games")
        clean_names = [row[0] for row in c.fetchall()]
        self.assertEqual(sorted(clean_names), ["Game1", "Game2", "Game3", "Game4"])
        
        # Check multi-part game
        c.execute("SELECT clean_name, part_number FROM games WHERE is_multi_part = 1")
        multi_parts = c.fetchall()
        self.assertEqual(len(multi_parts), 2)  # 2 parts of Game3
        
        # Check formats
        c.execute("SELECT clean_name, format FROM games WHERE clean_name = 'Game1'")
        game1_formats = c.fetchall()
        self.assertEqual(len(game1_formats), 2)  # Game1 appears in both collections
        
        conn.close()


if __name__ == '__main__':
    unittest.main()
