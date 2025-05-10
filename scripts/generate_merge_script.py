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
            SELECT gf.source_path, g.clean_name, gf.format
            FROM games g
            JOIN game_files gf ON g.id = gf.game_id
            WHERE g.is_multi_part = 0
            AND gf.format_priority = g.best_format_priority
            AND gf.format = g.best_format
            ORDER BY g.clean_name
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
            SELECT gf.source_path, g.clean_name, gf.format, gp.part_number
            FROM games g
            JOIN game_files gf ON g.id = gf.game_id
            JOIN game_parts gp ON gf.id = gp.file_id
            WHERE g.is_multi_part = 1
            AND gf.format_priority = g.best_format_priority
            AND gf.format = g.best_format
            ORDER BY g.clean_name, gp.part_number
        ''')
        
        # For multipart games, create directories and copy files into them
        current_game = None
        for source_path, clean_name, format_ext, part_num in c.fetchall():
            # Create game directory if this is a new game
            if clean_name != current_game:
                current_game = clean_name
                game_dir = os.path.join(MERGED_DIR, clean_name)
                game_dir = game_dir.replace('\\', '/')
                f.write(f'echo "Creating directory for {clean_name}"\n')
                f.write(f'mkdir -p "{game_dir}"\n\n')
            
            if part_num > 0:
                target_name = f"{clean_name} (Disk {part_num}).{format_ext}"
            else:
                target_name = f"{clean_name}.{format_ext}"
            target_path = os.path.join(MERGED_DIR, clean_name, target_name)
            
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
