"""Tests for file operations utility functions."""
import os
from pathlib import Path
import pytest
from tempfile import TemporaryDirectory

from c64collector.files import (
    should_skip_file,
    get_all_collections,
    clean_directory,
    ensure_directory_exists,
    normalize_path_for_script
)

class TestFileOps:
    
    def setUp(self):
        # Create a temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()
        
        # Create mock collection directories
        os.makedirs(os.path.join(self.temp_dir, "Collection1"))
        os.makedirs(os.path.join(self.temp_dir, "Collection2"))
        os.makedirs(os.path.join(self.temp_dir, "Originals"))  # Should be skipped
        
    def tearDown(self):
        # Remove the temporary directory after tests
        shutil.rmtree(self.temp_dir)
        
    def test_should_skip_file(self):
        # Test files that should be skipped
        self.assertTrue(should_skip_file("/path/to/BIOS.crt", "BIOS.crt"))
        self.assertTrue(should_skip_file("/path/to/Action Replay.d64", "Action Replay.d64"))
        self.assertTrue(should_skip_file("/path/to/Construction Kit.tap", "Construction Kit.tap"))
        self.assertTrue(should_skip_file("/path/to/Utility.nib", "Utility.nib"))
        self.assertTrue(should_skip_file("/path/to/Originals/Game.crt", "Game.crt"))
        self.assertTrue(should_skip_file("/path/to/game.bin", "game.bin"))  # Invalid extension
        
        # Test files that should not be skipped
        self.assertFalse(should_skip_file("/path/to/Game.crt", "Game.crt"))
        self.assertFalse(should_skip_file("/path/to/SuperGame.d64", "SuperGame.d64"))
        self.assertFalse(should_skip_file("/path/to/Adventure.tap", "Adventure.tap"))
        self.assertFalse(should_skip_file("/path/to/Racer.nib", "Racer.nib"))
        
    def test_get_all_collections(self):
        # Test getting collections
        collections = get_all_collections(self.temp_dir)
        self.assertEqual(len(collections), 3)  # Including Originals
        self.assertIn("Collection1", collections)
        self.assertIn("Collection2", collections)
        
        # Test with non-existent directory
        non_existent_dir = os.path.join(self.temp_dir, "non_existent")
        collections = get_all_collections(non_existent_dir)
        self.assertEqual(collections, [])


if __name__ == '__main__':
    unittest.main()
