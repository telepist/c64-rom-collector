"""
Module for verifying the collection.
"""
import os
from ..db.game_repository import GameRepository
from ..db.database import DatabaseManager


def check_missing_files(db_path="c64_games.db", target_dir="target"):
    """
    Check for missing files in the target directory.
    
    Args:
        db_path (str): Path to the database
        target_dir (str): Target directory to check
        
    Returns:
        dict: Statistics and list of missing files
    """
    db = DatabaseManager(db_path)
    db.connect()
    repository = GameRepository(db)
    
    results = {
        'missing_singles': [],
        'missing_multis': [],
        'total_expected': 0,
        'total_actual': 0,
        'total_missing': 0
    }
    
    # Get expected files from single part games
    repository.db_manager.execute('''
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
        SELECT clean_name, format, collection, source_path
        FROM RankedGames 
        WHERE rn = 1
        ORDER BY clean_name
    ''')
    single_files = repository.db_manager.fetchall()
    
    # Get expected files from multi part games
    repository.db_manager.execute('''
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
        SELECT g.clean_name, g.format, g.collection, g.source_path, g.part_number
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
    multi_files = repository.db_manager.fetchall()
    
    # Check single part games
    for clean_name, format_ext, collection, source_path in single_files:
        results['total_expected'] += 1
        expected_name = f"{clean_name}.{format_ext}"
        if not os.path.exists(os.path.join(target_dir, expected_name)):
            results['missing_singles'].append({
                "name": expected_name,
                "source": source_path
            })
    
    # Check multi part games
    for clean_name, format_ext, collection, source_path, part_num in multi_files:
        results['total_expected'] += 1
        if part_num > 0:
            expected_name = f"{clean_name} (Disk {part_num}).{format_ext}"
        else:
            expected_name = f"{clean_name}.{format_ext}"
        if not os.path.exists(os.path.join(target_dir, expected_name)):
            results['missing_multis'].append({
                "name": expected_name,
                "source": source_path
            })
    
    # Get actual files count
    results['total_actual'] = len([f for f in os.listdir(target_dir) 
                                if os.path.isfile(os.path.join(target_dir, f))])
    
    results['total_missing'] = len(results['missing_singles']) + len(results['missing_multis'])
    
    repository.db_manager.close()
    return results
