"""Tests for the file system repository."""
import os
from pathlib import Path
import pytest
import shutil
from tempfile import TemporaryDirectory

from c64collector.filesys import LocalFileRepository

class TestLocalFileRepository:
    """Test suite for LocalFileRepository implementation."""

    @pytest.fixture
    def repo(self):
        """Create a LocalFileRepository instance."""
        return LocalFileRepository()

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    def test_write_and_read_file(self, repo, temp_dir):
        """Test writing and reading a file."""
        test_file = temp_dir / "test.txt"
        test_data = b"test content"
        
        # Write file
        repo.write_file(test_file, test_data)
        assert test_file.exists()
        
        # Read file
        read_data = repo.read_file(test_file)
        assert read_data == test_data

    def test_list_files(self, repo, temp_dir):
        """Test listing files in a directory."""
        # Create test files
        files = ["test1.txt", "test2.txt", "other.dat"]
        for f in files:
            (temp_dir / f).write_bytes(b"")

        # List all files
        found_files = list(repo.list_files(temp_dir))
        assert len(found_files) == 3
        
        # List with pattern
        txt_files = list(repo.list_files(temp_dir, "*.txt"))
        assert len(txt_files) == 2
        assert all(f.suffix == ".txt" for f in txt_files)

    def test_exists(self, repo, temp_dir):
        """Test checking file existence."""
        test_file = temp_dir / "exists.txt"
        
        assert not repo.exists(test_file)
        test_file.write_bytes(b"")
        assert repo.exists(test_file)

    def test_copy_file(self, repo, temp_dir):
        """Test copying a file."""
        src = temp_dir / "source.txt"
        dst = temp_dir / "dest.txt"
        test_data = b"test content"
        
        src.write_bytes(test_data)
        repo.copy_file(src, dst)
        
        assert dst.exists()
        assert dst.read_bytes() == test_data
        assert src.exists()  # Original should remain

    def test_move_file(self, repo, temp_dir):
        """Test moving a file."""
        src = temp_dir / "source.txt"
        dst = temp_dir / "dest.txt"
        test_data = b"test content"
        
        src.write_bytes(test_data)
        repo.move_file(src, dst)
        
        assert dst.exists()
        assert dst.read_bytes() == test_data
        assert not src.exists()  # Original should be gone

    def test_get_file_size(self, repo, temp_dir):
        """Test getting file size."""
        test_file = temp_dir / "size.txt"
        test_data = b"test content"
        
        test_file.write_bytes(test_data)
        size = repo.get_file_size(test_file)
        assert size == len(test_data)

    def test_file_not_found(self, repo, temp_dir):
        """Test error handling for non-existent files."""
        non_existent = temp_dir / "doesnotexist.txt"
        
        with pytest.raises(FileNotFoundError):
            repo.read_file(non_existent)

    def test_nested_directories(self, repo, temp_dir):
        """Test handling nested directory creation."""
        nested_file = temp_dir / "deep" / "nested" / "test.txt"
        test_data = b"test content"
        
        repo.write_file(nested_file, test_data)
        assert nested_file.exists()
        assert repo.read_file(nested_file) == test_data
