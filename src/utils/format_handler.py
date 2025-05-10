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
          4: Cartridge (.crt) - Most reliable, original hardware format
          3: Disk images (.d64, .g64, .nib) - Complete disk images with protection
          2: Program files (.prg) - Raw program data, may miss custom loaders
          1: Tape images (.tap, .t64) - Lowest priority
    """
    ext = filename.lower().split('.')[-1]
    priorities = {
        'crt': 4,  # cartridges highest priority
        'd64': 3,  # disk images second (complete with protection)
        'g64': 3,
        'nib': 3,
        'prg': 2,  # program files third (may miss custom loaders)
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
    full_path = path + name
    
    # Skip certain patterns that might give false positives
    if any(p in full_path for p in [
        "Tape Port Dongle",
        "Savedisk",
        "Special Edition",
        "(v2)",
        "Re-release"
    ]):
        return False
    
    # Check for various multi-part patterns
    patterns = [
        r'(Side|Part|Disk)\s*[0-9]+',  # Side 1, Part 2, Disk 3
        r'Side\s*[A-B]',               # Side A, Side B
        r'Part\s*[0-9]+\s*-',          # Part 1 - Name
        r'Levels?\s*[0-9][\s\-]*(?:and|&|\+)[\s\-]*[0-9]',  # Levels 1 and 2, Level 1-2
        r'Disk\s*[0-9]+/',             # In directory name
        r'Side\s*[A-B]/',              # In directory name
        r'Part\s*[0-9]+/'              # In directory name
    ]
    
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
