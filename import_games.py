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

def import_games():
    print("Starting import from filesystem...")
    conn = sqlite3.connect('c64_games.db')
    c = conn.cursor()
    
    # Create tables if they don't exist
    c.execute('''CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY,
        source_path TEXT NOT NULL,
        original_name TEXT NOT NULL,
        clean_name TEXT NOT NULL,
        format TEXT NOT NULL,
        collection TEXT NOT NULL,
        format_priority INTEGER NOT NULL DEFAULT 0,
        is_multi_part INTEGER NOT NULL DEFAULT 0,
        part_number INTEGER NOT NULL DEFAULT 0
    )''')
    
    # Clear existing data
    c.execute('DELETE FROM games')
    
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
        batch_data = []
        
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
                        batch_data.append((
                            game_data['source_path'],
                            game_data['original_name'],
                            game_data['clean_name'],
                            game_data['format'],
                            game_data['collection'],
                            game_data['format_priority'],
                            game_data['is_multi_part'],
                            game_data['part_number']
                        ))
                        processed_files += 1
                    else:
                        skipped_files += 1
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
                    error_files += 1
            
            # Batch insert every 1000 files for efficiency
            if len(batch_data) >= 1000:
                c.executemany('''
                    INSERT INTO games 
                    (source_path, original_name, clean_name, format, 
                     collection, format_priority, is_multi_part, part_number)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', batch_data)
                conn.commit()
                batch_data = []
        
        # Insert any remaining files in this collection
        if batch_data:
            c.executemany('''
                INSERT INTO games 
                (source_path, original_name, clean_name, format, 
                 collection, format_priority, is_multi_part, part_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', batch_data)
    
    # Final commit
    conn.commit()
    
    # Create indexes for better query performance
    print("\nCreating indexes...")
    c.execute('CREATE INDEX IF NOT EXISTS idx_clean_name ON games (clean_name)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_format ON games (format)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_collection ON games (collection)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_multi_part ON games (is_multi_part)')
    conn.commit()
    
    # Print summary
    print("\nImport Summary:")
    print(f"Total files found: {total_files}")
    print(f"Files processed:   {processed_files}")
    print(f"Files skipped:     {skipped_files}")
    print(f"Files with errors: {error_files}")
    
    # Get counts from database for validation
    c.execute('SELECT COUNT(*) FROM games')
    db_count = c.fetchone()[0]
    print(f"Database entries:  {db_count}")
    
    c.execute('SELECT COUNT(DISTINCT clean_name) FROM games')
    unique_games = c.fetchone()[0]
    print(f"Unique game names: {unique_games}")
    
    c.execute('SELECT COUNT(*) FROM games WHERE is_multi_part = 1')
    multi_part_count = c.fetchone()[0]
    print(f"Multi-part files:  {multi_part_count}")
    
    conn.close()
    print("\nImport complete!")

if __name__ == '__main__':
    import time
    start_time = time.time()
    import_games()
    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds")
