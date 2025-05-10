"""
Core file operations for the ROM collector.
"""
import os
import shutil
from typing import List

def should_skip_file(path: str, filename: str) -> bool:
    """
    Determine if a file should be skipped during import.
    
    Args:
        path: The file path
        filename: The filename
        
    Returns:
        True if file should be skipped, False otherwise
    """
    # Patterns to skip
    skip_patterns = [
        'BIOS', 'Action Replay', 'EPROM-System',
        'Quickload', '64 Doctor', '64MON',
        'Construction Kit', 'Monitor', 'Compiler',
        'Editor', 'Utility', 'Demo Disk',
        'Program', 'System', 'Cartridge Plus'
    ]
    
    # Skip entries in Originals folder
    if '/Originals/' in path or '\\Originals\\' in path:
        return True
    
    # Skip system utilities and non-game content
    if any(pattern in path or pattern in filename for pattern in skip_patterns):
        return True
    
    # Skip certain file types
    format_ext = os.path.splitext(filename)[1][1:].lower()
    
    # Valid C64 ROM formats
    valid_formats = ['crt', 'd64', 'g64', 'nib', 'tap', 't64']
    
    # Skip if not a recognized C64 ROM format
    if format_ext not in valid_formats:
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
    normalized_path = path.replace('\\', '/')
    
    if ensure_prefix and not normalized_path.startswith(ensure_prefix):
        if not ensure_prefix.endswith('/'):
            ensure_prefix += '/'
        normalized_path = ensure_prefix + normalized_path
    
    return normalized_path
