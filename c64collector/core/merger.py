"""
Module for generating merge script.
"""
import os
from ..db.database import DatabaseManager


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
        f.write(f'# Create output directory\nmkdir -p "{target_dir}"\n\n')
        
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
        
        for source_path, clean_name, format_ext in db.fetchall():
            file_count += 1
            target_name = f"{clean_name}.{format_ext}"
            target_path = os.path.join(target_dir, target_name)
            
            # Ensure source path includes src/ prefix
            if not source_path.startswith("src/") and not source_path.startswith("src\\"):
                source_path = os.path.join("src", source_path)
            
            # Handle Windows paths
            source_path = source_path.replace('\\', '/')
            target_path = target_path.replace('\\', '/')
            
            f.write(f'echo "Copying {target_name}"\n')
            f.write(f'cp "{source_path}" "{target_path}" || echo "Failed to copy {target_name}"\n\n')
        
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
            
            # Ensure source path includes src/ prefix
            if not source_path.startswith("src/") and not source_path.startswith("src\\"):
                source_path = os.path.join("src", source_path)
            
            # Handle Windows paths
            source_path = source_path.replace('\\', '/')
            target_path = target_path.replace('\\', '/')
            
            f.write(f'echo "Copying {target_name}"\n')
            f.write(f'cp "{source_path}" "{target_path}" || echo "Failed to copy {target_name}"\n\n')
    
    db.close()
    print(f"Generated {output_path}")
    print(f"Script will copy {file_count} files to the {target_dir} directory.")
    
    return file_count
