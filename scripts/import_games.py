#!/usr/bin/env python3
import sqlite3
import os
import re

def get_format_priority(filename):
    ext = filename.lower().split('.')[-1]
    priorities = {
        'crt': 3,  # cartridges highest priority
        'd64': 2,  # disk images second
        'g64': 2,
        'nib': 2,
        'tap': 1,  # tapes lowest priority
        't64': 1
    }
    return priorities.get(ext, 0)

def is_multi_part(path, name):
    # Check if this is part of a multi-disk/part game
    return bool(re.search(r'(Side|Part|Disk)\s*[0-9]+', path + name, re.IGNORECASE))

def get_multi_part_info(path, name):
    # Extract part number if present
    match = re.search(r'(Side|Part|Disk)\s*([0-9]+)', path + name, re.IGNORECASE)
    if match:
        return int(match.group(2))
    return 0

def clean_name(name):
    # First, get base name without extension
    name = os.path.splitext(name)[0]
    
    # Remove side/part/disk numbers first
    name = re.sub(r'\s*[\(\[]?(Side|Part|Disk)\s*[0-9]+[\)\]]?.*$', '', name, flags=re.IGNORECASE)
    
    # Remove region and language markers
    name = re.sub(r'\s*[\(\[](USA|Europe|World|Japan|Eur?|Jp|En|PAL|NTSC)[^\)\]]*[\]\)]', '', name, flags=re.IGNORECASE)
    
    # Remove version info
    name = re.sub(r'\s*[\(\[]v[\d\.]+[\]\)]', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*[\(\[]Version\s+[a-z0-9\.]+[\]\)]', '', name, flags=re.IGNORECASE)
    
    # Remove common suffixes in parentheses
    name = re.sub(r'\s*[\(\[](Budget|Alt|Alternative|Unl|Aftermarket|Program|Tape\s*Port\s*Dongle)[\]\)]', '', name, flags=re.IGNORECASE)
    
    # Remove collection markers
    name = re.sub(r'\s*[\(\[](Compilation|Collection)[\]\)]', '', name, flags=re.IGNORECASE)
    
    # Convert roman numerals (but not if they're part of a larger word)
    name = re.sub(r'\bII\b', '2', name)
    name = re.sub(r'\bIII\b', '3', name)
    name = re.sub(r'\bIV\b', '4', name)
    name = re.sub(r'\bVI\b', '6', name)
    name = re.sub(r'\bVII\b', '7', name)
    name = re.sub(r'\bVIII\b', '8', name)
    
    # Remove any remaining parentheses and their contents
    name = re.sub(r'\s*\([^)]*\)', '', name)
    name = re.sub(r'\s*\[[^\]]*\]', '', name)
    
    # Clean up spaces and special characters
    name = name.strip()
    name = re.sub(r'\s+', ' ', name)
    
    return name

def should_skip_file(path, filename):
    """Determine if a file should be skipped during import."""
    # Patterns to skip
    skip_patterns = [
        'BIOS', 'Action Replay', 'EPROM-System',
        'Quickload', '64 Doctor', '64MON',
        'Construction Kit', 'Monitor', 'Compiler',
        'Editor', 'Utility', 'Demo Disk',
        'Program', 'System', 'Cartridge Plus'
    ]
    
    # Skip entries in Originals folder
    if '/Originals/' in path or '\\Originals\\' in path:
        return True
    
    # Skip system utilities and non-game content
    if any(pattern in path or pattern in filename for pattern in skip_patterns):
        return True
    
    # Skip certain file types
    format_ext = os.path.splitext(filename)[1][1:].lower()
    
    # Valid C64 ROM formats
    valid_formats = ['crt', 'd64', 'g64', 'nib', 'tap', 't64']
    
    # Skip if not a recognized C64 ROM format
    if format_ext not in valid_formats:
        return True
    
    return False

def process_file(file_path, collection_name):
    """Process a single file and return its game data."""
    original_name = os.path.basename(file_path)
    
    format_ext = os.path.splitext(original_name)[1][1:].lower()
    clean_title = clean_name(original_name)
    
    # Skip empty clean titles
    if not clean_title:
        return None
    
    format_priority = get_format_priority(original_name)
    is_multi = is_multi_part(file_path, original_name)
    part_num = get_multi_part_info(file_path, original_name) if is_multi else 0
    
    return {
        'source_path': file_path,
        'original_name': original_name,
        'clean_name': clean_title,
        'format': format_ext,
        'collection': collection_name,
        'format_priority': format_priority,
        'is_multi_part': 1 if is_multi else 0,
        'part_number': part_num
    }

def create_database_schema(conn):
    """Create the new normalized database schema"""
    c = conn.cursor()
    
    # Create games table (master list of games)
    c.execute('''CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY,
        clean_name TEXT NOT NULL UNIQUE,
        is_multi_part INTEGER NOT NULL DEFAULT 0,
        best_format TEXT,
        best_format_priority INTEGER DEFAULT 0
    )''')
    
    # Create game_files table (individual ROM files)
    c.execute('''CREATE TABLE IF NOT EXISTS game_files (
        id INTEGER PRIMARY KEY,
        game_id INTEGER NOT NULL,
        source_path TEXT NOT NULL,
        original_name TEXT NOT NULL,
        format TEXT NOT NULL,
        collection TEXT NOT NULL,
        format_priority INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (game_id) REFERENCES games(id)
    )''')
    
    # Create game_parts table (parts of multi-part games)
    c.execute('''CREATE TABLE IF NOT EXISTS game_parts (
        id INTEGER PRIMARY KEY,
        game_id INTEGER NOT NULL,
        file_id INTEGER NOT NULL,
        part_number INTEGER NOT NULL,
        FOREIGN KEY (game_id) REFERENCES games(id),
        FOREIGN KEY (file_id) REFERENCES game_files(id)
    )''')
    
    # Create indexes
    c.execute('CREATE INDEX IF NOT EXISTS idx_games_clean_name ON games (clean_name)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_game_files_game_id ON game_files (game_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_game_files_format ON game_files (format)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_game_files_collection ON game_files (collection)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_game_parts_game_id ON game_parts (game_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_game_parts_file_id ON game_parts (file_id)')
    
    conn.commit()

def import_games():
    print("Starting import from filesystem...")
    
    # Connect to the database (or create it if it doesn't exist)
    conn = sqlite3.connect('c64_games.db')
    c = conn.cursor()
    
    # Drop existing tables if they exist to clear all data
    print("Clearing existing database tables...")
    c.execute('DROP TABLE IF EXISTS game_parts')
    c.execute('DROP TABLE IF EXISTS game_files')
    c.execute('DROP TABLE IF EXISTS games')
    
    # Create new schema
    create_database_schema(conn)
    
    game_data_list = []  # List to store all processed game data
    
    # Get all collections (top-level directories in src/)
    collections_path = "src"
    if not os.path.exists(collections_path):
        print(f"Error: Source directory '{collections_path}' not found!")
        return
    
    collections = [d for d in os.listdir(collections_path) 
                  if os.path.isdir(os.path.join(collections_path, d))]
    
    total_files = 0
    processed_files = 0
    skipped_files = 0
    error_files = 0
    
    # Process each collection
    for collection in collections:
        print(f"Processing collection: {collection}")
        collection_path = os.path.join(collections_path, collection)
        
        # Walk through all files in the collection
        for root, dirs, files in os.walk(collection_path):
            total_files += len(files)
            for file in files:
                file_path = os.path.join(root, file)
                
                # Normalize path for consistency
                file_path = file_path.replace('\\', '/')
                
                if should_skip_file(file_path, file):
                    skipped_files += 1
                    continue
                
                try:
                    game_data = process_file(file_path, collection)
                    if game_data:
                        game_data_list.append(game_data)
                        processed_files += 1
                    else:
                        skipped_files += 1
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
                    error_files += 1
    
    print(f"\nProcessed {processed_files} files, now importing to database...")
    
    # First, collect unique game names and determine which are multi-part
    unique_games = {}
    for game in game_data_list:
        clean_name = game['clean_name']
        if clean_name not in unique_games:
            unique_games[clean_name] = game['is_multi_part']
        elif game['is_multi_part'] == 1:
            unique_games[clean_name] = 1
    
    # Insert the unique games into the games table
    game_ids = {}  # Map of clean_name to game_id
    batch_data = []
    for clean_name, is_multi in unique_games.items():
        batch_data.append((clean_name, is_multi))
        if len(batch_data) >= 1000:
            c.executemany('INSERT INTO games (clean_name, is_multi_part) VALUES (?, ?)', batch_data)
            conn.commit()
            batch_data = []
    
    if batch_data:
        c.executemany('INSERT INTO games (clean_name, is_multi_part) VALUES (?, ?)', batch_data)
        conn.commit()
    
    # Get all game IDs from the database
    c.execute('SELECT id, clean_name FROM games')
    for game_id, clean_name in c.fetchall():
        game_ids[clean_name] = game_id
    
    # Insert game files and build a list of multi-part games
    batch_files = []
    file_ids = {}  # To track file IDs for multi-part games
    file_counter = 0
    
    for game in game_data_list:
        game_id = game_ids[game['clean_name']]
        batch_files.append((
            game_id,
            game['source_path'],
            game['original_name'],
            game['format'],
            game['collection'],
            game['format_priority']
        ))
        
        # Track which items are multi-part for later insertion
        if game['is_multi_part'] == 1:
            file_counter += 1
            file_ids[game['source_path']] = (file_counter, game_id, game['part_number'])
        
        if len(batch_files) >= 1000:
            c.executemany('''
                INSERT INTO game_files 
                (game_id, source_path, original_name, format, collection, format_priority)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', batch_files)
            conn.commit()
            batch_files = []
    
    if batch_files:
        c.executemany('''
            INSERT INTO game_files 
            (game_id, source_path, original_name, format, collection, format_priority)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', batch_files)
        conn.commit()
    
    # Get the real file IDs from the database
    if file_ids:
        # Build a query to get all file IDs at once
        paths = list(file_ids.keys())
        placeholders = ','.join(['?' for _ in paths])
        c.execute(f'SELECT id, source_path FROM game_files WHERE source_path IN ({placeholders})', paths)
        file_id_map = {row[1]: row[0] for row in c.fetchall()}
        
        # Insert multi-part game records
        batch_parts = []
        for source_path, (_, game_id, part_number) in file_ids.items():
            file_id = file_id_map[source_path]
            batch_parts.append((game_id, file_id, part_number))
        
        c.executemany('INSERT INTO game_parts (game_id, file_id, part_number) VALUES (?, ?, ?)', batch_parts)
        conn.commit()
    
    # Update the best format for each game
    print("Calculating best format for each game...")
    c.execute('''
    WITH BestFormats AS (
        SELECT 
            game_id,
            format,
            format_priority,
            ROW_NUMBER() OVER (
                PARTITION BY game_id 
                ORDER BY format_priority DESC, collection ASC
            ) as rn
        FROM game_files
    )
    UPDATE games 
    SET 
        best_format = (SELECT format FROM BestFormats WHERE BestFormats.game_id = games.id AND rn = 1),
        best_format_priority = (SELECT format_priority FROM BestFormats WHERE BestFormats.game_id = games.id AND rn = 1)
    ''')
    conn.commit()
    
    # Print summary
    print("\nImport Summary:")
    print(f"Total files found: {total_files}")
    print(f"Files processed:   {processed_files}")
    print(f"Files skipped:     {skipped_files}")
    print(f"Files with errors: {error_files}")
    
    # Get counts from database for validation
    c.execute('SELECT COUNT(*) FROM games')
    games_count = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM game_files')
    files_count = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM game_parts')
    parts_count = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM games WHERE is_multi_part = 1')
    multi_games_count = c.fetchone()[0]
    
    print(f"Unique games:      {games_count}")
    print(f"Total game files:  {files_count}")
    print(f"Multi-part games:  {multi_games_count}")
    print(f"Game parts:        {parts_count}")
    
    conn.close()
    print("\nImport complete!")

if __name__ == '__main__':
    import time
    start_time = time.time()
    import_games()
    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds")
