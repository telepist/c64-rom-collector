"""
File script generation operations.
"""
import os
from typing import TextIO, Tuple, List

from .path_sanitizer import sanitize_directory_name, sanitize_full_path
from .operations import normalize_path_for_script


def prepare_path_for_script(path: str, is_source: bool = False) -> str:
    """
    Prepare a path for use in a shell script.
    
    Args:
        path: The path to normalize
        is_source: Whether this is a source path
        
    Returns:
        str: The normalized path
    """
    # First normalize slashes for script
    path = normalize_path_for_script(path)
    
    # Only sanitize target paths, not source paths
    if not is_source:
        path = sanitize_full_path(path)
        
    return path


def write_copy_command(script_file: TextIO, source_path: str, target_path: str, target_name: str):
    """
    Write a shell script command to copy a file.
    
    Args:
        script_file: File object to write to
        source_path: Source file path
        target_path: Target file path
        target_name: Name of the target file (for display)
    """
    # For display, replace backslashes with forward slashes and clean up double quotes
    display_name = target_name.replace('\\', '/').replace('"', '')
    script_file.write(f'echo "Copying {display_name}"\n')
    script_file.write(f'cp "{source_path}" "{target_path}" || echo "Failed to copy {display_name}"\n\n')


def write_m3u_playlist(script_file: TextIO, m3u_path: str, disk_files: List[Tuple[str, str]]):
    """
    Write an M3U playlist to a shell script.
    
    Args:
        script_file: File object to write to
        m3u_path: Path to save the .m3u file
        disk_files: List of tuples containing (relative_path, disk_label)
    """
    script_file.write(f'\n# Create playlist\n')
    script_file.write(f'cat > "{normalize_path_for_script(m3u_path)}" << EOL\n')
    # Write disk paths with labels
    for rel_path, label in disk_files:
        script_file.write(f'{rel_path}|{label}\n')
    script_file.write('EOL\n')
