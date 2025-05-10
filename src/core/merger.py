"""
Module for generating merge script.
"""
import os
from ..db.database import DatabaseManager
from ..db.game_repository import GameRepository
from ..files import clean_directory, ensure_directory_exists, normalize_path_for_script
from ..utils.path_sanitizer import sanitize_directory_name, sanitize_full_path


def clean_target_directory(target_dir="target"):
    """
    Remove all files from the target directory.
    
    Args:
        target_dir (str): Path to the target directory
    
    Returns:
        bool: True if cleaning was successful, False otherwise
    """
    result = clean_directory(target_dir)
    if result:
        print(f"Target directory '{target_dir}' has been cleaned.")
    else:
        print(f"Failed to clean target directory '{target_dir}'.")
    return result


def _write_copy_command(script_file, source_path, target_path, target_name):
    """
    Write a shell script command to copy a file.
    
    Args:
        script_file: File object to write to
        source_path (str): Source file path
        target_path (str): Target file path
    target_name (str): Name of the target file (for display)
    """
    # For display, replace backslashes with forward slashes and clean up double quotes
    display_name = target_name.replace('\\', '/').replace('"', '')
    script_file.write(f'echo "Copying {display_name}"\n')
    script_file.write(f'cp "{source_path}" "{target_path}" || echo "Failed to copy {display_name}"\n\n')


def _prepare_path_for_script(path, is_source=False):
    """
    Prepare a path for use in a shell script.
    
    Args:
        path (str): The path to normalize
        is_source (bool): Whether this is a source path
        
    Returns:
        str: The normalized path
    """
    # First normalize slashes for script
    path = normalize_path_for_script(path)
    
    # Only sanitize target paths, not source paths
    if not is_source:
        path = sanitize_full_path(path)
        
    return path


def generate_merge_script(db_path="c64_games.db", output_path="merge_collection.sh", target_dir="target"):
    """
    Generate a script to copy the best version of each game to the target directory.
    
    Args:
        db_path (str): Path to the database
        output_path (str): Path to save the generated script
        target_dir (str): Target directory for the merged collection
        
    Returns:
        int: Number of files to be merged
    """
    db = DatabaseManager(db_path)
    db.connect()
    repository = GameRepository(db)
    
    file_count = 0
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('#!/bin/bash\n\n')
        # Use normalized path for the target directory
        normalized_target = _prepare_path_for_script(target_dir)
        f.write(f'# Create output directory\nmkdir -p "{normalized_target}"\n\n')
        
        # Use GameRepository to fetch the best versions of games
        best_versions = repository.get_best_versions()
        current_game = None
        
        for clean_name, format_ext, source_path, part_number, total_parts in best_versions:
            file_count += 1
            # Only normalize source path for script but don't sanitize it
            source_path = normalize_path_for_script(source_path)
            
            # Sanitize the clean_name for directory and file names
            sanitized_name = sanitize_directory_name(clean_name)
            
            # For multi-part games, create a subdirectory
            if total_parts > 1:
                target_subdir = os.path.join(target_dir, sanitized_name)
                f.write(f'mkdir -p "{normalize_path_for_script(target_subdir)}"\n')
                if current_game != clean_name:
                    # Add a comment for the start of a multi-part game
                    f.write(f'\n# Multi-part game: {clean_name}\n')
                    current_game = clean_name
                # Create sanitized multi-part filename
                part_filename = f"{sanitized_name} (Part {part_number})"
                target_file = os.path.join(sanitized_name, f"{sanitize_directory_name(part_filename)}.{format_ext}")
            else:
                # Single file game
                target_file = f"{sanitized_name}.{format_ext}"
            
            target_path = normalize_path_for_script(os.path.join(target_dir, target_file))
            _write_copy_command(f, source_path, target_path, target_file)
    
    repository.db_manager.close()
    print(f"Generated {output_path}")
    print(f"Script will copy {file_count} files to the {target_dir} directory.")
    return file_count
