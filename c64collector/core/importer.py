"""
Import module that processes game files and imports them into the database.
"""
import os
from ..db.database import DatabaseManager
from ..db.game_repository import GameRepository
from ..files import get_all_collections
from ..core.processor import scan_directory


def import_games(src_dir="src", db_path="c64_games.db"):
    """
    Import games from the file system into the database.
    
    Args:
        src_dir (str): The source directory containing collections
        db_path (str): The database path
        
    Returns:
        dict: Statistics about the import process
    """
    print(f"Starting import from {src_dir} into {db_path}...")
    
    # Initialize database
    db = DatabaseManager(db_path)
    db.connect()
    db.reset_schema()
    repository = GameRepository(db)
    
    all_game_data = []
    stats = {
        'total_files': 0,
        'processed_files': 0,
        'skipped_files': 0,
        'error_files': 0,
        'unique_games': 0,
        'multi_games': 0
    }
    
    # Get all collections
    collections = get_all_collections(src_dir)
    if not collections:
        print(f"Error: Source directory '{src_dir}' not found or empty!")
        db.close()
        return stats
        
    # Process each collection
    for collection in collections:
        print(f"Processing collection: {collection}")
        collection_path = os.path.join(src_dir, collection)
        
        game_data_list, skipped, errors = scan_directory(collection_path, collection)
        all_game_data.extend(game_data_list)
        
        stats['processed_files'] += len(game_data_list)
        stats['skipped_files'] += skipped
        stats['error_files'] += errors
        
    print(f"\nProcessed {stats['processed_files']} files, now importing to database...")
    
    # Batch insert into database
    batch_data = []
    for game_data in all_game_data:
        batch_data.append(game_data)
        if len(batch_data) >= 1000:
            _insert_batch(repository, batch_data)
            batch_data = []
            
    if batch_data:
        _insert_batch(repository, batch_data)
    
    # Get stats using the new schema
    # Count unique games
    repository.db_manager.execute('SELECT COUNT(*) FROM games')
    stats['unique_games'] = repository.db_manager.fetchone()[0]
    
    # Count multi-part games (games that have versions with multiple parts)
    repository.db_manager.execute('''
        SELECT COUNT(DISTINCT g.id) 
        FROM games g 
        JOIN game_versions v ON g.id = v.game_id 
        JOIN game_parts p1 ON v.id = p1.version_id 
        JOIN game_parts p2 ON v.id = p2.version_id 
        WHERE p1.part_number < p2.part_number
    ''')
    stats['multi_games'] = repository.db_manager.fetchone()[0]
    
    db.close()
    print("\nImport complete!")
    return stats


def _insert_batch(repository, batch):
    """Helper function to insert a batch of records"""
    for game_data in batch:
        repository.insert_game(game_data)
    repository.db_manager.commit()
