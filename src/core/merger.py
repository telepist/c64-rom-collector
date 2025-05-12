"""
Module for generating merge script.
"""
import os
from pathlib import Path
from typing import Dict, List, Tuple

from config import DATABASE_PATH, MERGE_SCRIPT_PATH, TARGET_DIR
from db.database import DatabaseManager
from db.game_repository import GameRepository
from files import (
    clean_directory,
    normalize_path_for_script,
    sanitize_directory_name,
    sanitize_full_path
)


def clean_target_directory(target_dir=str(TARGET_DIR)):
    """Clean target directory."""
    try:
        return clean_directory(target_dir)
    except Exception as e:
        print(f"Error cleaning target directory: {e}")
        return False


def _write_copy_command_sh(script_file, source_path: str, target_path: str, target_name: str):
    """Write a copy command for shell script."""
    script_file.write(f'cp "{source_path}" "{target_path}"\n')


def _write_copy_command_cmd(script_file, source_path: str, target_path: str, target_name: str):
    """Write a copy command for Windows batch script."""
    # Convert forward slashes to backslashes for Windows
    source_path = source_path.replace('/', '\\')
    target_path = target_path.replace('/', '\\')
    script_file.write(f'copy "{source_path}" "{target_path}"\n')


def _write_mkdir_command_sh(script_file, directory: str):
    """Write a mkdir command for shell script."""
    script_file.write(f'mkdir -p "{directory}"\n')


def _write_mkdir_command_cmd(script_file, directory: str):
    """Write a mkdir command for Windows batch script."""
    # Convert forward slashes to backslashes for Windows
    directory = directory.replace('/', '\\')
    script_file.write(f'if not exist "{directory}" mkdir "{directory}"\n')


def _write_m3u_file_sh(script_file, m3u_path: str, disk_files: List[Tuple[str, str]]):
    """Write M3U file creation for shell script."""
    script_file.write(f'\n# Create playlist\n')
    script_file.write(f'cat > "{m3u_path}" << EOL\n')
    for rel_path, label in disk_files:
        script_file.write(f'{rel_path}|{label}\n')
    script_file.write('EOL\n')


def _write_m3u_file_cmd(script_file, m3u_path: str, disk_files: List[Tuple[str, str]]):
    """Write M3U file creation for Windows batch script."""
    m3u_path = m3u_path.replace('/', '\\')
    script_file.write(f'\nREM Create playlist\n')
    # Use temporary file to avoid redirection issues with special characters
    script_file.write('@echo off\n')
    for rel_path, label in disk_files:
        rel_path = rel_path.replace('/', '\\')
        # Escape special characters and use echo with >> for append
        script_file.write(f'echo {rel_path}^|{label}>>"{m3u_path}"\n')


def generate_merge_script(db_path=DATABASE_PATH, output_path=MERGE_SCRIPT_PATH, target_dir=TARGET_DIR):
    """
    Generate a script to copy the best version of each game to the target directory.
    Generates both shell script and batch script versions.
    
    Args:
        db_path (str): Path to the database
        output_path (str): Base path for the generated scripts
        target_dir (str): Target directory for the merged collection
        
    Returns:
        int: Number of files to be merged
    """
    db = DatabaseManager(db_path)
    db.connect()
    repository = GameRepository(db)
    
    file_count = 0
    m3u_files: Dict[str, List[Tuple[str, str]]] = {}

    # Define script paths
    sh_path = str(Path(output_path))
    cmd_path = str(Path(output_path).with_suffix('.cmd'))
    
    # Handle both shell and batch script generation
    with open(sh_path, 'w', encoding='utf-8') as sh_file, \
         open(cmd_path, 'w', encoding='utf-8') as cmd_file:
        
        # Write headers
        sh_file.write('#!/bin/bash\n\n')
        cmd_file.write('@echo off\nREM Generated merge script for Windows\n\n')
        
        # Create output directory
        normalized_target = normalize_path_for_script(target_dir)
        _write_mkdir_command_sh(sh_file, normalized_target)
        _write_mkdir_command_cmd(cmd_file, normalized_target)
        
        # Use GameRepository to fetch the best versions of games
        best_versions = repository.get_best_versions()
        current_game = None
        
        # Process each game version
        for clean_name, format_ext, source_path, part_number, total_parts in best_versions:
            file_count += 1
            source_path = normalize_path_for_script(source_path)
            sanitized_name = sanitize_directory_name(clean_name)
            
            # For multi-part games, create a subdirectory
            if total_parts > 1:
                target_subdir = os.path.join(target_dir, sanitized_name)
                norm_subdir = normalize_path_for_script(target_subdir)
                
                if current_game != clean_name:
                    # Add comments for multi-part game
                    sh_file.write(f'\n# Multi-part game: {clean_name}\n')
                    cmd_file.write(f'\nREM Multi-part game: {clean_name}\n')
                    current_game = clean_name
                    # Create subdirectory
                    _write_mkdir_command_sh(sh_file, norm_subdir)
                    _write_mkdir_command_cmd(cmd_file, norm_subdir)
                
                # For multi-part games, preserve original disk notation
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
            
            # Write copy commands
            _write_copy_command_sh(sh_file, source_path, target_path, target_file)
            _write_copy_command_cmd(cmd_file, source_path, target_path, target_file)
        
        # Write .m3u files for multi-disk games
        for game_name, disk_files in m3u_files.items():
            m3u_path = normalize_path_for_script(os.path.join(target_dir, f"{sanitize_directory_name(game_name)}.m3u"))
            _write_m3u_file_sh(sh_file, m3u_path, disk_files)
            _write_m3u_file_cmd(cmd_file, m3u_path, disk_files)
    
    repository.db_manager.close()
    print(f"Generated {sh_path} and {cmd_path}")
    print(f"Scripts will copy {file_count} files to the {target_dir} directory.")
    return file_count
