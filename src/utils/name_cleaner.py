"""
Utility functions for cleaning and normalizing game names.
"""
import os
import re

def extract_region(name):
    """
    Extract region information from a game name.
    
    Args:
        name (str): The original game name
        
    Returns:
        str: The region code (USA, Europe, World, Japan, etc.) or empty string if not found
    """
    # Skip region extraction for multi-part games to avoid false positives
    if re.search(r'(Side|Part|Disk)\s*[0-9]+', name, re.IGNORECASE):
        return ""
    
    # Look for common region patterns
    region_match = re.search(r'\(([^)]*(?:USA|Europe|World|Japan|Eur|Jp|En|PAL|NTSC)[^)]*)\)', name, flags=re.IGNORECASE)
    if region_match:
        region_text = region_match.group(1).strip()
        # Normalize common region names
        region_text = re.sub(r'\bEur\b', 'Europe', region_text, flags=re.IGNORECASE)
        region_text = re.sub(r'\bJp\b', 'Japan', region_text, flags=re.IGNORECASE)
        region_text = re.sub(r'\bEn\b', 'English', region_text, flags=re.IGNORECASE)
        return region_text
    return ""


def get_region_priority(region):
    """
    Get the priority value for a region.
    
    Args:
        region (str): The region string
        
    Returns:
        int: The priority value (higher is better)
    """
    # Define region priorities here to avoid circular imports
    REGION_PRIORITIES = {
        'Europe': 6,     # Europe releases (highest priority)
        'PAL': 5,        # PAL-specific releases
        'World': 4,      # World releases
        'USA': 3,        # USA releases
        'Japan': 2,      # Japan releases
        'NTSC': 1,       # NTSC-specific releases
        '': 0            # No region specified (lowest priority)
    }
    
    # Check exact matches first
    if region in REGION_PRIORITIES:
        return REGION_PRIORITIES[region]
    
    # Check for partial matches (e.g., "USA, Europe" should match "USA")
    for priority_region in sorted(REGION_PRIORITIES.keys(), key=lambda x: REGION_PRIORITIES[x], reverse=True):
        if priority_region and priority_region in region:
            return REGION_PRIORITIES[priority_region]
    
    return REGION_PRIORITIES.get('', 0)

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
