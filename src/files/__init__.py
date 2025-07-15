"""
File operations module for ROM collection management.
"""

from .operations import (
    should_skip_file,
    get_all_collections,
    clean_directory,
    ensure_directory_exists,
    normalize_path_for_script,
    read_file,
    write_file,
    copy_file,
    is_file,
    is_dir
)

from .path_sanitizer import (
    sanitize_directory_name,
    sanitize_full_path
)

__all__ = [
    'should_skip_file',
    'get_all_collections', 
    'clean_directory',
    'ensure_directory_exists',
    'normalize_path_for_script',
    'sanitize_directory_name',
    'sanitize_full_path',
    'read_file',
    'write_file',
    'copy_file',
    'is_file',
    'is_dir'
]
