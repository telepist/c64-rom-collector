"""
Functions for format prioritization and multi-part game detection.
"""
import re


def get_format_priority(filename):
    """
    Determine the priority of a file format.
    
    Args:
        filename (str): The filename to check
        
    Returns:
        int: The priority level (higher is better)
    """
    ext = filename.lower().split('.')[-1]
    priorities = {
        'crt': 3,  # cartridges highest priority
        'd64': 2,  # disk images second
        'g64': 2,
        'nib': 2,
        'tap': 1,  # tapes lowest priority
        't64': 1
    }
    return priorities.get(ext, 0)


def is_multi_part(path, name):
    """
    Check if a file is part of a multi-disk/multi-part game.
    
    Args:
        path (str): The file path
        name (str): The filename
        
    Returns:
        bool: True if this is a multi-part game, False otherwise
    """
    return bool(re.search(r'(Side|Part|Disk)\s*[0-9]+', path + name, re.IGNORECASE))


def get_multi_part_info(path, name):
    """
    Extract part number if present in filename or path.
    
    Args:
        path (str): The file path
        name (str): The filename
        
    Returns:
        int: The part number, or 0 if not found
    """
    match = re.search(r'(Side|Part|Disk)\s*([0-9]+)', path + name, re.IGNORECASE)
    if match:
        return int(match.group(2))
    return 0
