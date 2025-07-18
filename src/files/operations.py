"""
Core file operations for the ROM collector.
"""
import os
import shutil
from pathlib import Path
from typing import List, Union, Iterator
from config import FORMAT_PRIORITIES, SKIP_PATTERNS

def should_skip_file(path: Union[str, Path], filename: str) -> bool:
    """
    Determine if a file should be skipped during import.
    
    Args:
        path: The file path
        filename: The filename
        
    Returns:
        True if file should be skipped, False otherwise
    """
    # Convert to Path for safe operations
    path_obj = Path(path)
    
    # Skip entries in Originals folder
    if 'Originals' in path_obj.parts:
        return True
    
    # Skip system utilities and non-game content using configured patterns
    if any(pattern in path or pattern in filename for pattern in SKIP_PATTERNS):
        return True
      # Skip certain file types
    format_ext = os.path.splitext(filename)[1][1:].lower()
    
    # Valid C64 ROM formats    # Skip if not a recognized C64 ROM format
    if format_ext not in FORMAT_PRIORITIES.keys():
        return True
    
    return False


def get_all_collections(base_dir: str) -> List[str]:
    """
    Get all collections (top-level directories) in the source directory.
    
    Args:
        base_dir: The base directory containing collections
        
    Returns:
        A list of collection directories
    """
    if not os.path.exists(base_dir):
        return []
        
    return [d for d in os.listdir(base_dir) 
            if os.path.isdir(os.path.join(base_dir, d))]


def clean_directory(directory_path: str) -> bool:
    """
    Remove all files from a directory but keep the directory itself.
    
    Args:
        directory_path: Path to the directory to clean
    
    Returns:
        True if cleaning was successful, False otherwise
    """
    try:
        # Check if directory exists
        if os.path.exists(directory_path):
            # Test write access by trying to add a subdirectory
            test_dir = os.path.join(directory_path, '.test')
            try:
                os.makedirs(test_dir, exist_ok=True)
                os.rmdir(test_dir)
            except (IOError, OSError, PermissionError):
                return False
                
            # Remove all content but keep directory
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                if os.path.isfile(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            return True
        else:
            # Create directory if it doesn't exist
            os.makedirs(directory_path, exist_ok=True)
            return True
    except Exception as e:
        print(f"Error cleaning directory '{directory_path}': {e}")
        return False


def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
    
    Returns:
        True if directory exists or was created successfully, False otherwise
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory '{directory_path}': {e}")
        return False


def normalize_path_for_script(path: str, ensure_prefix: str = None) -> str:
    """
    Normalize a path for use in a shell script (replace backslashes with forward slashes).
    
    Args:
        path: The path to normalize
        ensure_prefix: A prefix to ensure is at the start of the path
        
    Returns:
        The normalized path
    """
    if path is None:
        raise TypeError("Path cannot be None")
    
    normalized_path = path.replace('\\', '/')
    
    if ensure_prefix and not normalized_path.startswith(ensure_prefix):
        if not ensure_prefix.endswith('/'):
            ensure_prefix += '/'
        normalized_path = ensure_prefix + normalized_path
    
    return normalized_path


def read_file(path: Union[str, Path]) -> bytes:
    """
    Read file from filesystem.
    
    Args:
        path: Path to the file to read
        
    Returns:
        The file contents as bytes
        
    Raises:
        FileNotFoundError: If the file does not exist
    """
    return Path(path).read_bytes()


def write_file(path: Union[str, Path], data: bytes) -> None:
    """
    Write file to filesystem.
    
    Args:
        path: Path where to write the file
        data: Content to write to the file
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def copy_file(src: Union[str, Path], dst: Union[str, Path]) -> None:
    """
    Copy a file from source to destination.
    
    Args:
        src: Source file path
        dst: Destination file path
    """
    src, dst = Path(src), Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def is_file(path: Union[str, Path]) -> bool:
    """
    Check if path points to a regular file.
    
    Args:
        path: Path to check
        
    Returns:
        True if path is a regular file
    """
    return Path(path).is_file()


def is_dir(path: Union[str, Path]) -> bool:
    """
    Check if path points to a directory.
    
    Args:
        path: Path to check
        
    Returns:
        True if path is a directory
    """
    return Path(path).is_dir()
