"""
File system repository interface.
Provides a clean, storage-agnostic API for file operations.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator, List, Union, BinaryIO

class FileRepository(ABC):
    """Abstract base class for file system operations."""

    @abstractmethod
    def read_file(self, path: Union[str, Path]) -> bytes:
        """Read the contents of a file.
        
        Args:
            path: Path to the file to read
            
        Returns:
            The file contents as bytes
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            PermissionError: If the file can't be accessed
        """
        pass

    @abstractmethod
    def write_file(self, path: Union[str, Path], data: bytes) -> None:
        """Write data to a file.
        
        Args:
            path: Path where to write the file
            data: The data to write
            
        Raises:
            PermissionError: If the file can't be written
            OSError: If there's an error writing the file
        """
        pass

    @abstractmethod
    def list_files(self, directory: Union[str, Path], pattern: str = "*") -> Iterator[Path]:
        """List files in a directory matching a pattern.
        
        Args:
            directory: Directory to list files from
            pattern: Glob pattern to match files against
            
        Returns:
            Iterator of paths to matching files
            
        Raises:
            FileNotFoundError: If the directory doesn't exist
            PermissionError: If the directory can't be accessed
        """
        pass

    @abstractmethod
    def exists(self, path: Union[str, Path]) -> bool:
        """Check if a file or directory exists.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path exists, False otherwise
        """
        pass

    @abstractmethod
    def copy_file(self, src: Union[str, Path], dst: Union[str, Path]) -> None:
        """Copy a file from source to destination.
        
        Args:
            src: Source file path
            dst: Destination file path
            
        Raises:
            FileNotFoundError: If source doesn't exist
            PermissionError: If files can't be accessed
            OSError: If there's an error during copy
        """
        pass

    @abstractmethod
    def move_file(self, src: Union[str, Path], dst: Union[str, Path]) -> None:
        """Move a file from source to destination.
        
        Args:
            src: Source file path
            dst: Destination file path
            
        Raises:
            FileNotFoundError: If source doesn't exist
            PermissionError: If files can't be accessed
            OSError: If there's an error during move
        """
        pass

    @abstractmethod
    def get_file_size(self, path: Union[str, Path]) -> int:
        """Get the size of a file in bytes.
        
        Args:
            path: Path to the file
            
        Returns:
            Size of the file in bytes
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            PermissionError: If the file can't be accessed
        """
        pass

    @abstractmethod
    def remove_file(self, path: Union[str, Path]) -> None:
        """Remove a file.
        
        Args:
            path: Path to the file to remove
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            PermissionError: If the file can't be removed
            OSError: If there's an error removing the file
        """
        pass

    @abstractmethod
    def remove_directory(self, path: Union[str, Path], recursive: bool = False) -> None:
        """Remove a directory.
        
        Args:
            path: Path to the directory to remove
            recursive: If True, remove directory and all contents
            
        Raises:
            FileNotFoundError: If the directory doesn't exist
            PermissionError: If the directory can't be removed
            OSError: If there's an error removing the directory
        """
        pass

    @abstractmethod
    def is_file(self, path: Union[str, Path]) -> bool:
        """Check if a path is a file.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path is a file, False otherwise
        """
        pass

    @abstractmethod
    def is_dir(self, path: Union[str, Path]) -> bool:
        """Check if a path is a directory.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path is a directory, False otherwise
        """
        pass
