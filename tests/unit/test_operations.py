"""Tests for file operations utility functions."""
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from c64collector.files.operations import (
    should_skip_file,
    get_all_collections,
    clean_directory,
    ensure_directory_exists
)


class TestFileOps(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create mock collection directories
        os.makedirs(os.path.join(self.temp_dir, "Collection1"))
        os.makedirs(os.path.join(self.temp_dir, "Collection2"))
        os.makedirs(os.path.join(self.temp_dir, "Originals"))
        
        # Create some test files
        self.test_files = [
            os.path.join(self.temp_dir, "Collection1", "test1.txt"),
            os.path.join(self.temp_dir, "Collection1", "test2.txt"),
            os.path.join(self.temp_dir, "Collection1", "subdir")
        ]
        
        for file_path in self.test_files[:-1]:
            with open(file_path, 'w') as f:
                f.write("test content")
        
        os.makedirs(self.test_files[-1])
        
    def tearDown(self):
        """Clean up test environment."""
        try:
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Warning: Failed to clean up temp directory: {e}")

    def test_should_skip_file(self):
        """Test file skipping functionality."""
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
        """Test getting collections."""
        collections = get_all_collections(self.temp_dir)
        self.assertEqual(len(collections), 3)  # Including Originals
        self.assertIn("Collection1", collections)
        self.assertIn("Collection2", collections)
        
        # Test with non-existent directory
        non_existent_dir = os.path.join(self.temp_dir, "non_existent")
        collections = get_all_collections(non_existent_dir)
        self.assertEqual(collections, [])
        
    def test_clean_directory(self):
        """Test directory cleaning functionality."""
        test_dir = os.path.join(self.temp_dir, "Collection1")
        
        # Verify initial state
        self.assertTrue(os.path.exists(test_dir))
        self.assertTrue(os.path.exists(self.test_files[0]))
        
        # Test cleaning
        result = clean_directory(test_dir)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_dir))  # Directory should still exist
        self.assertEqual(os.listdir(test_dir), [])  # But should be empty
        
        # Test cleaning non-existent directory
        non_existent = os.path.join(self.temp_dir, "non_existent")
        result = clean_directory(non_existent)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(non_existent))
        
        # Test cleaning with permission error
        if os.name == 'posix':  # Skip on Windows
            read_only_dir = os.path.join(self.temp_dir, "readonly")
            os.makedirs(read_only_dir)
            os.chmod(read_only_dir, 0o444)  # Read-only
            result = clean_directory(read_only_dir)
            self.assertFalse(result)  # Should fail gracefully
            
    def test_ensure_directory_exists(self):
        """Test directory creation functionality."""
        # Test creating new directory
        new_dir = os.path.join(self.temp_dir, "new_directory")
        self.assertFalse(os.path.exists(new_dir))
        result = ensure_directory_exists(new_dir)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(new_dir))
        
        # Test with existing directory
        result = ensure_directory_exists(new_dir)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(new_dir))
        
        # Test with deeply nested path
        deep_path = os.path.join(self.temp_dir, "deep", "nested", "path")
        result = ensure_directory_exists(deep_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(deep_path))
          # Test with invalid characters in path (Windows)
        if os.name == 'nt':
            invalid_path = os.path.join(self.temp_dir, "test<>:\"/\\|?*")
            result = ensure_directory_exists(invalid_path)
            self.assertFalse(result)  # Should fail gracefully


if __name__ == '__main__':
    unittest.main()
