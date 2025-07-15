"""Tests for path-based file operations."""
import os
import shutil
import tempfile
import unittest
from pathlib import Path
import platform
from unittest.mock import patch

from files.operations import (
    should_skip_file,
    get_all_collections,
    clean_directory,
    ensure_directory_exists,
    read_file,
    write_file,
    copy_file,
    is_file,
    is_dir,
    normalize_path_for_script
)


class TestPathOperations(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        # Use Path for all path operations
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create collections with platform-safe paths
        self.collections = {
            "Collection1": self.temp_dir / "Collection1",
            "Collection2": self.temp_dir / "Collection2",
            "Originals": self.temp_dir / "Originals"
        }
        
        for path in self.collections.values():
            path.mkdir(exist_ok=True)
            
        # Create test files
        self.test_files = {
            "regular": self.collections["Collection1"] / "test.txt",
            "spaces": self.collections["Collection1"] / "test with spaces.txt",
            "special": self.collections["Collection1"] / "test_special#1.txt"
        }
        
        for file_path in self.test_files.values():
            file_path.write_text("test content")
            
        # Create a subdirectory
        self.test_subdir = self.collections["Collection1"] / "subdir"
        self.test_subdir.mkdir()

    def tearDown(self):
        """Clean up test environment."""
        try:
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Warning: Failed to clean up temp directory: {e}")

    def test_read_write_file(self):
        """Test reading and writing files."""
        test_path = self.temp_dir / "test_rw.txt"
        test_content = b"Test content"
        
        # Test write_file
        write_file(test_path, test_content)
        self.assertTrue(test_path.exists())
        
        # Test read_file
        content = read_file(test_path)
        self.assertEqual(content, test_content)
        
        # Test with non-existent file
        with self.assertRaises(FileNotFoundError):
            read_file(self.temp_dir / "nonexistent.txt")

    def test_copy_file(self):
        """Test copying files."""
        source = self.test_files["regular"]
        copy_dest = self.temp_dir / "copied.txt"
        
        # Test copy_file
        copy_file(source, copy_dest)
        self.assertTrue(copy_dest.exists())
        self.assertTrue(source.exists())
        self.assertEqual(source.read_bytes(), copy_dest.read_bytes())



    def test_is_file_dir(self):
        """Test file and directory checking."""
        self.assertTrue(is_file(self.test_files["regular"]))
        self.assertFalse(is_file(self.test_subdir))
        self.assertTrue(is_dir(self.test_subdir))
        self.assertFalse(is_dir(self.test_files["regular"]))

    def test_normalize_path_for_script(self):
        """Test path normalization for scripts."""
        # Test Windows-style paths
        win_path = r"C:\path\to\file.txt"
        norm_path = normalize_path_for_script(win_path)
        self.assertIn("/", norm_path)
        self.assertNotIn("\\", norm_path)
        
        # Test Unix-style paths
        unix_path = "/path/to/file.txt"
        norm_path = normalize_path_for_script(unix_path)
        self.assertEqual(norm_path, unix_path)
        
        # Test with prefix
        norm_path = normalize_path_for_script("file.txt", ensure_prefix="prefix")
        self.assertEqual(norm_path, "prefix/file.txt")

    def test_platform_specific_paths(self):
        """Test handling of platform-specific paths."""
        if platform.system() == "Windows":
            # Test UNC paths
            unc_path = Path("//server/share/file.txt")
            self.assertEqual(
                normalize_path_for_script(str(unc_path)),
                "//server/share/file.txt"
            )
            
            # Test drive letters
            drive_path = Path("C:/Windows/file.txt")
            self.assertEqual(
                normalize_path_for_script(str(drive_path)),
                "C:/Windows/file.txt"
            )
        else:
            # Test absolute paths
            abs_path = Path("/usr/local/file.txt")
            self.assertEqual(
                normalize_path_for_script(str(abs_path)),
                "/usr/local/file.txt"
            )
            
            # Test home directory paths
            home_path = Path("~/file.txt")
            self.assertEqual(
                normalize_path_for_script(str(home_path)),
                "~/file.txt"
            )

    def test_path_error_handling(self):
        """Test error handling for path operations."""
        non_existent = self.temp_dir / "nonexistent"
        invalid_dest = self.temp_dir / "invalid" / "path" / "file.txt"
        
        # Test copy to invalid destination
        with self.assertRaises(FileNotFoundError):
            copy_file(non_existent, invalid_dest)
            
        # Test operations with None paths
        with self.assertRaises(TypeError):
            normalize_path_for_script(None)

    @unittest.skipIf(platform.system() != "Windows", "Windows-specific test")
    def test_windows_path_limits(self):
        """Test handling of Windows path length limits."""
        # Create a path that exceeds Windows 260 character limit
        long_name = "x" * 250
        long_path = self.temp_dir / long_name
        
        # Test creating directory with long path
        result = ensure_directory_exists(str(long_path))
        
        # On modern Windows systems, long paths may be supported
        # Just test that the function handles it gracefully (doesn't crash)
        self.assertIsInstance(result, bool)  # Should return a boolean result
        
        # If it succeeded, verify the directory actually exists
        if result:
            self.assertTrue(os.path.exists(str(long_path)))

    def test_case_sensitivity(self):
        """Test handling of case sensitivity differences."""
        original = self.test_files["regular"]
        upper_case = Path(str(original).upper())
        lower_case = Path(str(original).lower())
        
        if platform.system() == "Windows":
            # Windows should treat all cases as the same file
            self.assertTrue(is_file(upper_case))
            self.assertTrue(is_file(lower_case))
        else:
            # Unix should only find exact match
            self.assertTrue(is_file(original))
            self.assertFalse(is_file(upper_case))
            self.assertFalse(is_file(lower_case))


if __name__ == '__main__':
    unittest.main()
