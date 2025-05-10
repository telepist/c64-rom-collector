"""Tests for file repository-based operations."""
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from c64collector.filesys import FileRepository, LocalFileRepository
from c64collector.utils.file_ops import (
    clean_directory,
    ensure_directory_exists,
    get_all_collections,
    normalize_path_for_script
)

class TestRepositoryBasedOps(unittest.TestCase):
    """Test suite for repository-based file operations."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_path = Path(self.temp_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
        
    def test_clean_directory(self):
        """Test cleaning a directory with repository."""
        # Create test files
        test_file = self.test_path / "test.txt"
        test_file.write_text("test")
        test_subdir = self.test_path / "subdir"
        test_subdir.mkdir()
        (test_subdir / "subfile.txt").write_text("test")
        
        # Clean directory
        self.assertTrue(clean_directory(str(self.test_path)))
        
        # Verify directory is empty
        self.assertTrue(self.test_path.exists())
        self.assertEqual(len(list(self.test_path.iterdir())), 0)
        
    def test_ensure_directory_exists(self):
        """Test directory creation with repository."""
        test_dir = self.test_path / "nested" / "dir"
        
        # Create directory
        self.assertTrue(ensure_directory_exists(str(test_dir)))
        
        # Verify directory exists
        self.assertTrue(test_dir.exists())
        self.assertTrue(test_dir.is_dir())
        
    def test_get_all_collections(self):
        """Test getting collections with repository."""
        # Create test collections
        collections = ["Collection1", "Collection2"]
        for coll in collections:
            (self.test_path / coll).mkdir()
            
        # Add a file (should be ignored)
        (self.test_path / "not_a_dir.txt").write_text("")
        
        # Get collections
        found = get_all_collections(str(self.test_path))
        self.assertEqual(sorted(found), sorted(collections))
        
    def test_normalize_path_for_script(self):
        """Test path normalization."""
        # Basic normalization
        self.assertEqual(
            normalize_path_for_script(r"path\to\file"),
            "path/to/file"
        )
        
        # With prefix
        self.assertEqual(
            normalize_path_for_script("to/file", ensure_prefix="path"),
            "path/to/file"
        )
        
        # With existing prefix
        self.assertEqual(
            normalize_path_for_script("path/to/file", ensure_prefix="path"),
            "path/to/file"
        )
