"""
Utilities for sanitizing file system paths.
"""
import re
import os

def sanitize_directory_name(name: str) -> str:
    """
    Sanitizes a directory name by removing/replacing problematic characters.
    
    Args:
        name (str): The directory name to sanitize
        
    Returns:
        str: A sanitized directory name safe for all file systems
    """
    # Collapse multiple spaces to a single space
    name = re.sub(r'\s+', ' ', name)

    # Replace problematic characters with underscores
    name = re.sub(r'[<>:"|?*\\/]', '_', name)
    
    # Collapse multiple underscores to a single underscore
    name = re.sub(r'_{2,}', '_', name)

    # Trim dots, underscores, and spaces
    name = name.strip('. _')

    # Ensure name isn't empty and doesn't consist only of dots
    if not name or all(c == '.' for c in name):
        name = "unnamed"
        
    return name

def sanitize_full_path(path: str) -> str:
    """
    Sanitizes a full path by sanitizing each component.
    
    Args:
        path (str): The full path to sanitize
        
    Returns:
        str: A sanitized path safe for all file systems
    """
    # Split path into components
    components = path.split('/')
    
    # Sanitize each component except the first one (which might be empty for absolute paths)
    for i in range(1, len(components)):
        components[i] = sanitize_directory_name(components[i])
        
    # Rejoin path
    return '/'.join(components)
