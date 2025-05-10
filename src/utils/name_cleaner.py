"""
Utility functions for cleaning and normalizing game names.
"""
import os
import re

def clean_name(name):
    """
    Cleans and normalizes a game name by removing region markers, version info,
    and other unnecessary information.
    
    Args:
        name (str): The original game name
        
    Returns:
        str: The cleaned game name
    """
    # First, get base name without extension
    name = os.path.splitext(name)[0]
    
    # Remove side/part/disk numbers first
    name = re.sub(r'\s*[\(\[]?(Side|Part|Disk)\s*[0-9]+[\)\]]?.*$', '', name, flags=re.IGNORECASE)
    
    # Remove region and language markers
    name = re.sub(r'\s*[\(\[](USA|Europe|World|Japan|Eur?|Jp|En|PAL|NTSC)[^\)\]]*[\]\)]', '', name, flags=re.IGNORECASE)
    
    # Remove version info
    name = re.sub(r'\s*[\(\[]v[\d\.]+[\)\]]', '', name, flags=re.IGNORECASE)
    name = re.sub(r'v[\d\.]+\b', '', name)  # Also remove version without parentheses
    name = re.sub(r'\s*[\(\[]Version\s+[a-z0-9\.]+[\)\]]', '', name, flags=re.IGNORECASE)
    
    # Remove common suffixes in parentheses
    name = re.sub(r'\s*[\(\[](Budget|Alt|Alternative|Unl|Aftermarket|Program|Tape\s*Port\s*Dongle)[\]\)]', '', name, flags=re.IGNORECASE)
    
    # Remove collection markers
    name = re.sub(r'\s*[\(\[](Compilation|Collection)[\]\)]', '', name, flags=re.IGNORECASE)
    
    # Convert roman numerals (but not if they're part of a larger word)
    name = re.sub(r'\bII\b', '2', name)
    name = re.sub(r'\bIII\b', '3', name)
    name = re.sub(r'\bIV\b', '4', name)
    name = re.sub(r'\bVI\b', '6', name)
    name = re.sub(r'\bVII\b', '7', name)
    name = re.sub(r'\bVIII\b', '8', name)
    
    # Remove any remaining parentheses and their contents
    name = re.sub(r'\s*\([^)]*\)', '', name)
    name = re.sub(r'\s*\[[^\]]*\]', '', name)
    
    # Clean up spaces and special characters
    name = name.strip()
    name = re.sub(r'\s+', ' ', name)
    
    return name
