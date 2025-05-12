"""
Integration tests for the importer module.
"""
import unittest
import os
import tempfile
import shutil
import sqlite3
from core.importer import import_games


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
        
        # Check unique games
        c.execute("SELECT COUNT(*) FROM games")
        self.assertEqual(c.fetchone()[0], 4)  # 4 unique games
        
        # Check game versions
        c.execute("SELECT COUNT(*) FROM game_versions")
        self.assertEqual(c.fetchone()[0], 5)  # 5 versions (Game1 has 2 versions)
        
        # Check game parts
        c.execute("SELECT COUNT(*) FROM game_parts")
        self.assertEqual(c.fetchone()[0], 6)  # 6 total files
        
        # Check clean names
        c.execute("SELECT clean_name FROM games ORDER BY clean_name")
        clean_names = [row[0] for row in c.fetchall()]
        self.assertEqual(clean_names, ["Game1", "Game2", "Game3", "Game4"])
        
        # Check multi-part game
        c.execute("""
            SELECT g.clean_name, COUNT(p.id)
            FROM games g
            JOIN game_versions v ON g.id = v.game_id
            JOIN game_parts p ON v.id = p.version_id
            WHERE g.clean_name = 'Game3'
            GROUP BY g.id
        """)
        multi_part = c.fetchone()
        self.assertEqual(multi_part[1], 2)  # Game3 has 2 parts
        
        # Check Game1 appears in both collections
        c.execute("""
            SELECT COUNT(DISTINCT v.collection)
            FROM games g
            JOIN game_versions v ON g.id = v.game_id
            WHERE g.clean_name = 'Game1'
        """)
        self.assertEqual(c.fetchone()[0], 2)  # Game1 is in 2 collections
        
        conn.close()


if __name__ == '__main__':
    unittest.main()
