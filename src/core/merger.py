"""
Module for generating merge script.
"""
import os
from ..config import DATABASE_PATH, MERGE_SCRIPT_PATH, TARGET_DIR
from ..db.database import DatabaseManager
from src.db.game_repository import GameRepository
from src.files import (
    clean_directory,
    normalize_path_for_script,
    sanitize_directory_name,
    sanitize_full_path
)


def clean_target_directory(target_dir=str(TARGET_DIR)):
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
        source_path: Source file path
        target_path: Target file path
        target_name: Name of the target file (for display)
    """
    # For display, replace backslashes with forward slashes and clean up double quotes
    display_name = target_name.replace('\\', '/').replace('"', '')
    script_file.write(f'echo "Copying {display_name}"\n')
    script_file.write(f'cp "{source_path}" "{target_path}" || echo "Failed to copy {display_name}"\n\n')


def generate_merge_script(db_path=DATABASE_PATH, output_path=MERGE_SCRIPT_PATH, target_dir=TARGET_DIR):
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
    m3u_files = {}
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('#!/bin/bash\n\n')
        # Use normalized path for the target directory
        normalized_target = normalize_path_for_script(target_dir)
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
                    current_game = clean_name                # For multi-part games, preserve original disk notation
                target_file = os.path.join(sanitized_name, f"{sanitized_name} (Disk {part_number}).{format_ext}")
                rel_path = target_file.replace('\\', '/')

                # Add to m3u playlist with label
                if clean_name not in m3u_files:
                    m3u_files[clean_name] = []
                m3u_files[clean_name].append((rel_path, f"Disk {part_number}"))
            else:
                # Single file game
                target_file = f"{sanitized_name}.{format_ext}"
            
            target_path = normalize_path_for_script(os.path.join(target_dir, target_file))
            _write_copy_command(f, source_path, target_path, target_file)
        
        # Write .m3u files for multi-disk games
        for game_name, disk_files in m3u_files.items():
            m3u_path = os.path.join(target_dir, f"{sanitize_directory_name(game_name)}.m3u")
            f.write(f'\n# Create {game_name} playlist\n')
            f.write(f'cat > "{normalize_path_for_script(m3u_path)}" << EOL\n')
            # Write disk paths with labels
            for rel_path, label in disk_files:
                f.write(f'{rel_path}|{label}\n')
            f.write('EOL\n')
    
    repository.db_manager.close()
    print(f"Generated {output_path}")
    print(f"Script will copy {file_count} files to the {target_dir} directory.")
    return file_count
