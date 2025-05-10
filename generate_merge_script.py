#!/usr/bin/env python3
import sqlite3
import os

def generate_merge_script():
    conn = sqlite3.connect('c64_games.db')
    c = conn.cursor()
    
    # Create output directory if it doesn't exist
    MERGED_DIR = "target"
    
    with open('merge_collection.sh', 'w', encoding='utf-8') as f:
        f.write('#!/bin/bash\n\n')
        f.write(f'# Create output directory\nmkdir -p "{MERGED_DIR}"\n\n')
        
        # First, handle single-part games
        c.execute('''
            WITH RankedGames AS (
                SELECT *,
                    ROW_NUMBER() OVER (
                        PARTITION BY clean_name 
                        ORDER BY format_priority DESC, 
                                 collection ASC  -- prefer No-Intro when format is same
                    ) as rn
                FROM games
                WHERE is_multi_part = 0
                AND format_priority > 0  -- Ensure only valid ROM formats are included
            )
            SELECT source_path, clean_name, format
            FROM RankedGames
            WHERE rn = 1
            ORDER BY clean_name;
        ''')
        
        for source_path, clean_name, format_ext in c.fetchall():
            target_name = f"{clean_name}.{format_ext}"
            target_path = os.path.join(MERGED_DIR, target_name)
            
            # Ensure source path includes src/ prefix
            if not source_path.startswith("src/") and not source_path.startswith("src\\"):
                source_path = os.path.join("src", source_path)
            
            # Handle Windows paths
            source_path = source_path.replace('\\', '/')
            target_path = target_path.replace('\\', '/')
            
            f.write(f'echo "Copying {target_name}"\n')
            f.write(f'cp "{source_path}" "{target_path}" || echo "Failed to copy {target_name}"\n\n')
         # Then handle multi-part games
        c.execute('''
            WITH RankedGames AS (
                SELECT g.*,
                    ROW_NUMBER() OVER (
                        PARTITION BY clean_name 
                        ORDER BY format_priority DESC,
                                 collection ASC  -- prefer No-Intro when format is same
                    ) as rn
                FROM games g
                WHERE is_multi_part = 1
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
            ORDER BY g.clean_name, g.part_number;
        ''')
        
        for source_path, clean_name, format_ext, part_num in c.fetchall():
            if part_num > 0:
                target_name = f"{clean_name} (Disk {part_num}).{format_ext}"
            else:
                target_name = f"{clean_name}.{format_ext}"
            target_path = os.path.join(MERGED_DIR, target_name)
            
            # Ensure source path includes src/ prefix
            if not source_path.startswith("src/") and not source_path.startswith("src\\"):
                source_path = os.path.join("src", source_path)
            
            # Handle Windows paths
            source_path = source_path.replace('\\', '/')
            target_path = target_path.replace('\\', '/')
            
            f.write(f'echo "Copying {target_name}"\n')
            f.write(f'cp "{source_path}" "{target_path}" || echo "Failed to copy {target_name}"\n\n')
    
    conn.close()
    print("Generated merge_collection.sh")
    print("Run it to create the target folder with the best version of each game.")

if __name__ == '__main__':
    generate_merge_script()
