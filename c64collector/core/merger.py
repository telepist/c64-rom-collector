"""
Module for generating merge script.
"""
import os
from ..db.database import DatabaseManager
from ..utils.file_ops import clean_directory, ensure_directory_exists, normalize_path_for_script


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
    script_file.write(f'echo "Copying {target_name}"\n')
    script_file.write(f'cp "{source_path}" "{target_path}" || echo "Failed to copy {target_name}"\n\n')


def _prepare_path_for_script(path, is_source=False):
    """
    Prepare a path for use in a shell script.
    
    Args:
        path (str): The path to normalize
        is_source (bool): Whether this is a source path
        
    Returns:
        str: The normalized path
    """
    if is_source:
        return normalize_path_for_script(path, ensure_prefix="src")
    else:
        return normalize_path_for_script(path)


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
    
    file_count = 0
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('#!/bin/bash\n\n')
        # Use normalized path for the target directory
        normalized_target = _prepare_path_for_script(target_dir)
        f.write(f'# Create output directory\nmkdir -p "{normalized_target}"\n\n')
        
        # First, handle single-part games
        db.execute('''
            WITH RankedGames AS (
                SELECT *,
                    ROW_NUMBER() OVER (
                        PARTITION BY clean_name 
                        ORDER BY format_priority DESC, 
                                 collection ASC
                    ) as rn
                FROM games
                WHERE is_multi_part = 0
            )
            SELECT source_path, clean_name, format
            FROM RankedGames 
            WHERE rn = 1
            ORDER BY clean_name
        ''')
        
        # Process single-part games
        for source_path, clean_name, format_ext in db.fetchall():
            file_count += 1
            target_name = f"{clean_name}.{format_ext}"
            target_path = os.path.join(target_dir, target_name)
            
            # Use utility functions to normalize paths
            source_path = _prepare_path_for_script(source_path, is_source=True)
            target_path = _prepare_path_for_script(target_path)
            
            _write_copy_command(f, source_path, target_path, target_name)
        
        # Then handle multi-part games
        db.execute('''
            WITH RankedGames AS (
                SELECT g.*,
                    ROW_NUMBER() OVER (
                        PARTITION BY clean_name 
                        ORDER BY format_priority DESC,
                                 collection ASC
                    ) as rn
                FROM games g
                WHERE g.is_multi_part = 1
            )
            SELECT g.source_path, g.clean_name, g.format, g.part_number
            FROM games g
            JOIN (
                SELECT clean_name, format, collection
                FROM RankedGames 
                WHERE rn = 1
            ) r ON g.clean_name = r.clean_name 
                AND g.format = r.format 
                AND g.collection = r.collection
            WHERE g.is_multi_part = 1
            ORDER BY g.clean_name, g.part_number
        ''')
        
        # Process multi-part games
        for source_path, clean_name, format_ext, part_num in db.fetchall():
            file_count += 1
            
            if part_num > 0:
                target_name = f"{clean_name} (Disk {part_num}).{format_ext}"
            else:
                target_name = f"{clean_name}.{format_ext}"
            target_path = os.path.join(target_dir, target_name)
            
            # Use utility functions to normalize paths
            source_path = _prepare_path_for_script(source_path, is_source=True)
            target_path = _prepare_path_for_script(target_path)
            
            _write_copy_command(f, source_path, target_path, target_name)
    
    db.close()
    print(f"Generated {output_path}")
    print(f"Script will copy {file_count} files to the {target_dir} directory.")
    
    return file_count
