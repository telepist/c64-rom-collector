"""
Utilities for sanitizing file system paths.
"""
import re
import os
import posixpath

def sanitize_directory_name(name: str) -> str:
    """
    Sanitizes a directory name by removing/replacing problematic characters.
    
    Args:
        name (str): The directory name to sanitize
        
    Returns:
        str: A sanitized directory name safe for all file systems
    """
    # Extract region/version info from parentheses before removing them
    region = None
    region_match = re.search(r'\s*\((USA|Europe|Japan|World)\)', name)
    if region_match:
        region = region_match.group(1)
        name = name.replace(region_match.group(0), '')
    
    # Remove other parentheses (and their contents)
    name = re.sub(r'\s*\([^)]*\)', '', name)

    # Collapse multiple spaces to a single space
    name = re.sub(r'\s+', ' ', name)

    # Replace problematic characters with underscores
    name = re.sub(r'[<>:"|?*\\/\s]', '_', name)
    
    # Collapse multiple underscores to a single underscore
    name = re.sub(r'_{2,}', '_', name)

    # Trim dots, underscores, and spaces
    name = name.strip('. _')

    # Add back region info if present
    if region:
        name = f"{name}_{region}"

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
    # Convert to forward slashes
    path = path.replace('\\', '/')

    # Handle special cases first
    if path.startswith('//'):
        # Network share paths
        parts = path[2:].split('/', 1)
        if len(parts) == 1:
            return '//' + parts[0]
        server, rest = parts
        return '//' + server + '/' + sanitize_full_path(rest)
    
    # Preserve Windows drive letters
    drive = ''
    if re.match(r'^[A-Za-z]:', path):
        drive = path[0] + ':/'
        path = path[3:]  # Skip drive letter and :/

    # Split path into components
    components = path.split('/')
    
    # Keep track of components for proper .. resolution
    result_components = []
    
    # Process each component
    for i in range(len(components)):
        component = components[i]
        
        # Skip empty components and current directory
        if not component or component == '.':
            continue
            
        # Handle parent directory
        if component == '..':
            # Pop the last component unless we're at root
            if result_components and result_components[-1] != '..':
                result_components.pop()
            else:
                result_components.append('..')
            continue
            
        # Handle file extensions
        if '.' in component:
            name, ext = os.path.splitext(component)
            result_components.append(sanitize_directory_name(name) + ext)
        else:
            result_components.append(sanitize_directory_name(component))
            
    # If path starts with /, preserve it
    if path.startswith('/'):
        result_components.insert(0, '')
            
    # Combine drive (if any) with sanitized path
    return drive + '/'.join(result_components)
