"""
File system operations and filtering functions for the ROM collector.
"""
import os
import re

def should_skip_file(path, filename):
    """
    Determine if a file should be skipped during import.
    
    Args:
        path (str): The file path
        filename (str): The filename
        
    Returns:
        bool: True if file should be skipped, False otherwise
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


def get_all_collections(base_dir):
    """
    Get all collections (top-level directories) in the source directory.
    
    Args:
        base_dir (str): The base directory containing collections
        
    Returns:
        list: A list of collection directories
    """
    if not os.path.exists(base_dir):
        return []
        
    return [d for d in os.listdir(base_dir) 
            if os.path.isdir(os.path.join(base_dir, d))]
