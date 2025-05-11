"""
Configuration module for the C64 ROM collector.

This module centralizes all configuration values used across the application.
All paths are handled in a platform-independent way using pathlib.Path.
"""
from pathlib import Path

# Directory paths
BUILD_DIR = Path("build")
ROMS_DIR = Path("roms")
TARGET_DIR = Path("target")

# File paths
DATABASE_PATH = BUILD_DIR / "c64_games.db"
MERGE_SCRIPT_PATH = BUILD_DIR / "merge_collection.sh"

# Database configuration
BATCH_SIZE = 1000  # Number of records to insert in one batch

# Format priorities (higher number = higher priority)
FORMAT_PRIORITIES = {
    'crt': 3,  # Cartridge files (highest priority)
    'd64': 2,  # Disk images
    'g64': 2,
    'nib': 2,
    'tap': 1,  # Tape images (lowest priority)
    't64': 1,
    'prg': 1
}

# Skip patterns for file processing
SKIP_PATTERNS = [
    'BIOS',
    'Action Replay',
    'EPROM-System',
    'Quickload',
    '64 Doctor',
    '64MON',
    'Construction Kit',
    'Monitor',
    'Compiler',
    'Editor',
    'Utility',
    'Demo Disk',
    'Program',
    'System',
    'Cartridge Plus'
]

# Multi-part patterns
MULTI_PART_PATTERNS = [
    r'(Side|Part|Disk)\s*[0-9]+',  # Side 1, Part 2, Disk 3
    r'Side\s*[A-B]',               # Side A, Side B
    r'Part\s*[0-9]+\s*-',          # Part 1 - Name
    r'Levels?\s*[0-9][\s\-]*(?:and|&|\+)[\s\-]*[0-9]',  # Levels 1 and 2, Level 1-2
    r'Disk\s*[0-9]+/',             # In directory name
    r'Side\s*[A-B]/',              # In directory name
    r'Part\s*[0-9]+/'              # In directory name
]