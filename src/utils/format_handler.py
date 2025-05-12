"""
Functions for format prioritization and multi-part game detection.
"""
import re
from config import FORMAT_PRIORITIES, SKIP_PATTERNS, MULTI_PART_PATTERNS


def get_format_priority(filename):
    """
    Determine the priority of a file format.
    
    Args:
        filename (str): The filename to check
          Returns:
        int: The priority level (higher is better)
          3: Cartridge (.crt) - Most reliable, original hardware format
          2: Disk images (.d64, .g64, .nib) - Complete disk images with protection
          1: Program files (.prg), Tape images (.tap, .t64) - Lowest priority
          0: Unknown formats"""    
    ext = filename.lower().split('.')[-1]
    return FORMAT_PRIORITIES.get(ext, 0)


def is_multi_part(path, name):
    """
    Check if a file is part of a multi-disk/multi-part game.
    
    Args:
        path (str): The file path
        name (str): The filename
        
    Returns:
        bool: True if this is a multi-part game, False otherwise
    """
    full_path = path + name
      # Skip certain patterns that might give false positives
    if any(p in full_path for p in SKIP_PATTERNS):
        return False
    
    # Check for various multi-part patterns
    patterns = MULTI_PART_PATTERNS
    
    return any(bool(re.search(pattern, full_path, re.IGNORECASE)) for pattern in patterns)


def get_multi_part_info(path, name):
    """
    Extract part number if present in filename or path.
    
    Args:
        path (str): The file path
        name (str): The filename
        
    Returns:
        int: The part number, or 0 if not found
    """
    full_path = path + name
    
    # Skip certain patterns
    if any(p in full_path for p in [
        "Tape Port Dongle",
        "Savedisk",
        "Special Edition",
        "(v2)",
        "Re-release"
    ]):
        return 0
        
    # First try normal numeric patterns
    match = re.search(r'(Side|Part|Disk)\s*([0-9]+)', full_path, re.IGNORECASE)
    if match:
        return int(match.group(2))
    
    # Check for Side A/B format
    match = re.search(r'Side\s*([A-B])', full_path, re.IGNORECASE)
    if match:
        # Convert A -> 1, B -> 2
        return ord(match.group(1).upper()) - ord('A') + 1
      # Handle sequential level numbering
    matches = list(re.finditer(r'Levels?\s*([0-9]+)(?:\s*(?:and|&|\+|-)\s*([0-9]+))?', full_path, re.IGNORECASE))
    if matches:
        # Count how many level pairs came before this one
        current_match = matches[0]
        first_num = int(current_match.group(1))
        # Return the sequence number (1 for levels 1-2, 2 for levels 3-4, etc)
        return (first_num + 1) // 2
    
    return 0
