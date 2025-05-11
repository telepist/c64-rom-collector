"""
Utilities for sanitizing file system paths.
"""
import re
import os
import posixpath

def sanitize_directory_name(name: str, preserve_spaces: bool = True) -> str:
    """
    Sanitizes a directory name by removing/replacing problematic characters.
    
    Args:
        name (str): The directory name to sanitize
        preserve_spaces (bool): Whether to preserve spaces or convert them to underscores
        
    Returns:
        str: A sanitized directory name safe for all file systems
    """
    if not name:
        return "unnamed"

    # Remove all parentheses (and their contents)
    name = re.sub(r'\s*\([^)]*\)', '', name)

    # Remove wildcard characters first
    name = re.sub(r'[?*]', '', name)

    # Collapse multiple spaces to a single space and trim
    name = re.sub(r'\s+', ' ', name).strip()

    # Remove dots surrounded by spaces or at start/end
    name = re.sub(r'(^|\s)\.+(\s|$)', ' ', name).strip()
    
    # Replace problematic characters
    if preserve_spaces:
        name = re.sub(r'[<>:"|\\]', '_', name)
    else:
        name = re.sub(r'[<>:"|\\\s]', '_', name)
    
    # Collapse multiple underscores to a single underscore
    name = re.sub(r'_{2,}', '_', name)

    # Trim dots and underscores (but not spaces)
    while name.startswith(('.', '_')):
        name = name[1:]
    while name.endswith(('.', '_')):
        name = name[:-1]

    # If name is empty or only dots/spaces/underscores, use "unnamed"
    name = name.strip()
    if not name or all(c in '. _' for c in name):
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
    # Convert to forward slashes
    path = path.replace('\\', '/')

    # Handle root paths
    if path == '/':
        return '/'

    # Split path into root and non-root parts
    root = ''
    rest = path

    # Handle network share paths first (must be before Unix root check)
    if path.startswith('//'):
        parts = path[2:].split('/', 1)
        if len(parts) == 1:
            return '//' + parts[0]
        server, rest = parts
        return '//' + server + '/' + sanitize_full_path(rest)

    # Handle Unix-style root paths
    elif path.startswith('/'):
        root = '/'
        rest = path[1:]

    # Handle Windows drive letters
    elif re.match(r'^[A-Za-z]:', path):
        root = path[0:3]  # Includes drive letter and :/
        rest = path[3:]

    # Process the components
    components = []
    for comp in rest.split('/'):
        if not comp or comp == '.':
            continue
        if comp == '..':
            if components and components[-1] != '..':
                components.pop()
            else:
                components.append('..')
            continue
                
        # Always preserve spaces in all path components
        components.append(sanitize_directory_name(comp, True))

    # Put it all back together
    result = root + '/'.join(components)
    
    return result
