#!/usr/bin/env python3
import sqlite3

def check_counts():
    conn = sqlite3.connect('c64_games.db')
    c = conn.cursor()
    
    # Count single part games
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
        SELECT COUNT(*) FROM RankedGames WHERE rn = 1
    ''')
    single_games = c.fetchone()[0]
    
    # Count multi part games
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
        SELECT COUNT(*) FROM games g
        JOIN (
            SELECT clean_name, format, collection
            FROM RankedGames 
            WHERE rn = 1
        ) r ON g.clean_name = r.clean_name 
            AND g.format = r.format 
            AND g.collection = r.collection
        WHERE g.is_multi_part = 1
    ''')
    multi_parts = c.fetchone()[0]
    
    print(f"Expected single-part games: {single_games}")
    print(f"Expected multi-part files: {multi_parts}")
    print(f"Total expected files: {single_games + multi_parts}")
    
    conn.close()

if __name__ == '__main__':
    check_counts()
