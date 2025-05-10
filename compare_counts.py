#!/usr/bin/env python3
import sqlite3
import os

def compare_counts():
    conn = sqlite3.connect('c64_games.db')
    c = conn.cursor()
      # Count what's in target directory
    target_files = set(os.listdir("target"))
    print(f"Files in target directory: {len(target_files)}")
    
    # Get expected files from database
    expected_files = set()
    
    # Single part games
    c.execute('''
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
        SELECT clean_name, format
        FROM RankedGames 
        WHERE rn = 1
    ''')
    for clean_name, format_ext in c.fetchall():
        expected_files.add(f"{clean_name}.{format_ext}")
    
    # Multi part games
    c.execute('''
        WITH RankedGames AS (
            SELECT g.*,
                ROW_NUMBER() OVER (
                    PARTITION BY clean_name 
                    ORDER BY format_priority DESC,
                             collection ASC
                ) as rn
            FROM games g
            WHERE is_multi_part = 1
        )
        SELECT g.clean_name, g.format, g.part_number
        FROM games g
        JOIN (
            SELECT clean_name, format, collection
            FROM RankedGames 
            WHERE rn = 1
        ) r ON g.clean_name = r.clean_name 
            AND g.format = r.format 
            AND g.collection = r.collection
        WHERE g.is_multi_part = 1
    ''')
    for clean_name, format_ext, part_num in c.fetchall():
        if part_num > 0:
            expected_files.add(f"{clean_name} (Disk {part_num}).{format_ext}")
        else:
            expected_files.add(f"{clean_name}.{format_ext}")
    
    print(f"Files expected from database: {len(expected_files)}")
      # Find differences
    in_collection_not_expected = target_files - expected_files
    expected_not_in_collection = expected_files - target_files
    
    print(f"\nFiles in collection but not expected: {len(in_collection_not_expected)}")
    for f in list(in_collection_not_expected)[:20]:  # Show first 20
        print(f"  {f}")
    
    print(f"\nFiles expected but not in collection: {len(expected_not_in_collection)}")
    for f in list(expected_not_in_collection)[:20]:  # Show first 20
        print(f"  {f}")
    
    conn.close()

if __name__ == '__main__':
    compare_counts()
