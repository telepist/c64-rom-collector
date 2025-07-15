"""
Core functionality for processing game files.
"""
import os
from utils.name_cleaner import clean_name, extract_region, get_region_priority
from utils.format_handler import get_format_priority, is_multi_part, get_multi_part_info
from files import should_skip_file


def process_file(file_path, collection_name):
    """
    Process a single file and return its game data.
    
    Args:
        file_path (str): Path to the file
        collection_name (str): Name of the collection
        
    Returns:
        dict: Game data dictionary, or None if file should be skipped
    """
    original_name = os.path.basename(file_path)
    format_ext = os.path.splitext(original_name)[1][1:].lower()
    clean_title = clean_name(original_name)
    
    # Skip empty clean titles
    if not clean_title:
        return None
    
    # Extract region information
    region = extract_region(original_name)
    region_priority = get_region_priority(region)
    
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
        'region': region,
        'region_priority': region_priority,
        'is_multi_part': 1 if is_multi else 0,
        'part_number': part_num
    }


def scan_directory(base_dir, collection_name):
    """
    Scan a directory for game files.
    
    Args:
        base_dir (str): The base directory to scan
        collection_name (str): The name of the collection
        
    Returns:
        tuple: (processed_files, skipped_files, error_files)
    """
    game_data_list = []
    skipped_files = 0
    error_files = 0
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            file_path = os.path.join(root, file)
            
            # Normalize path for consistency
            file_path = file_path.replace('\\', '/')
            
            if should_skip_file(file_path, file):
                skipped_files += 1
                continue
            
            try:
                game_data = process_file(file_path, collection_name)
                if game_data:
                    game_data_list.append(game_data)
                else:
                    skipped_files += 1
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                error_files += 1
    
    return game_data_list, skipped_files, error_files
