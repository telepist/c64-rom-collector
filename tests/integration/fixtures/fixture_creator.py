"""Utility to create comprehensive test fixtures.

This module provides functions for:
1. Creating dynamic fixtures in memory for comprehensive integration tests
2. Providing expected results for filesystem-based integration tests

The physical fixture files are stored in the roms/ directory and are used by
filesystem integration tests. The dynamic fixtures are created on-demand by
comprehensive integration tests.
"""
import os
from pathlib import Path
from .fixture_definitions import (
    REGIONAL_FIXTURES, FORMAT_PRIORITY_FIXTURES, MULTIDISK_FIXTURES,
    COLLECTION_FIXTURES, EDGE_CASE_FIXTURES, SKIP_FIXTURES
)


def create_comprehensive_fixtures(base_dir: Path):
    """Create comprehensive test fixtures for integration tests."""
    
    # Clean up existing fixtures
    if base_dir.exists():
        import shutil
        shutil.rmtree(base_dir)
    
    # Create base directory
    base_dir.mkdir(parents=True)
    
    # Create collection directories
    nointro_dir = base_dir / "NoIntro"
    tosec_dir = base_dir / "TOSEC"
    oneload64_dir = base_dir / "OneLoad64"
    
    nointro_dir.mkdir()
    tosec_dir.mkdir()
    oneload64_dir.mkdir()
    
    # Create regional variation fixtures in TOSEC
    for filename, content in REGIONAL_FIXTURES.items():
        (tosec_dir / filename).write_text(content)
    
    # Create format priority fixtures in TOSEC
    for filename, content in FORMAT_PRIORITY_FIXTURES.items():
        (tosec_dir / filename).write_text(content)
    
    # Create multi-disk fixtures in NoIntro
    for filename, content in MULTIDISK_FIXTURES.items():
        (nointro_dir / filename).write_text(content)
    
    # Create collection priority fixtures
    for collection, games in COLLECTION_FIXTURES.items():
        target_dir = None
        if collection == "nointro":
            target_dir = nointro_dir
        elif collection == "tosec":
            target_dir = tosec_dir
        elif collection == "oneload64":
            target_dir = oneload64_dir
        
        if target_dir:
            for filename, content in games.items():
                (target_dir / filename).write_text(content)
    
    # Create edge case fixtures in TOSEC
    for filename, content in EDGE_CASE_FIXTURES.items():
        (tosec_dir / filename).write_text(content)
    
    # Create skippable files in both collections
    for filename, content in SKIP_FIXTURES.items():
        (nointro_dir / filename).write_text(content)
        (tosec_dir / filename).write_text(content)
    
    return {
        'nointro': nointro_dir,
        'tosec': tosec_dir,
        'oneload64': oneload64_dir,
    }


def get_expected_results():
    """Get expected test results for verification."""
    return {
        # Regional prioritization expectations
        'regional_winners': {
            'Bubble Bobble': ('Europe', 'Europe Bubble Bobble content'),
            'Defender': ('PAL', 'PAL Defender content'),
            'Maniac Mansion': ('Europe, USA', 'Europe USA Maniac Mansion content'),
            'Tetris': ('Europe', 'Europe Tetris content'),
            'Pacman': ('USA', 'USA Pacman content'),
        },
        
        # Format priority expectations
        'format_winners': {
            'Ghostbusters': ('crt', 'Ghostbusters cartridge content'),
            'Frogger': ('d64', 'USA Frogger disk content'),  # USA d64 beats Europe tap
            'Pitfall': ('crt', 'Europe Pitfall cartridge content'),  # crt beats all
        },
        
        # Multi-disk expectations
        'multidisk_games': {
            'Ultima 4': {  # Name cleaner converts "Ultima IV" to "Ultima 4"
                'parts': 4,
                'files': ['Ultima 4 (Disk 1).d64', 'Ultima 4 (Disk 2).d64', 
                         'Ultima 4 (Disk 3).d64', 'Ultima 4 (Disk 4).d64'],
                'm3u_content': [
                    'Ultima 4/Ultima 4 (Disk 1).d64|Disk 1',
                    'Ultima 4/Ultima 4 (Disk 2).d64|Disk 2',
                    'Ultima 4/Ultima 4 (Disk 3).d64|Disk 3',
                    'Ultima 4/Ultima 4 (Disk 4).d64|Disk 4',
                ]
            },
            'Wasteland': {
                'parts': 2,
                'files': ['Wasteland (Disk 1).d64', 'Wasteland (Disk 2).d64'],  # "Side" gets converted to "Disk"
                'm3u_content': [
                    'Wasteland/Wasteland (Disk 1).d64|Disk 1',
                    'Wasteland/Wasteland (Disk 2).d64|Disk 2',
                ]
            },
            "Bard's Tale": {
                'parts': 2,
                'files': ["Bard's Tale (Disk 1).d64", "Bard's Tale (Disk 2).d64"],  # Region info stripped
                'm3u_content': [
                    "Bard's Tale/Bard's Tale (Disk 1).d64|Disk 1",
                    "Bard's Tale/Bard's Tale (Disk 2).d64|Disk 2",
                ]
            },
            'Pool of Radiance': {
                'parts': 2,
                'files': ['Pool of Radiance (Disk 1).d64', 'Pool of Radiance (Disk 2).d64'],  # Region info stripped
                'm3u_content': [
                    'Pool of Radiance/Pool of Radiance (Disk 1).d64|Disk 1',
                    'Pool of Radiance/Pool of Radiance (Disk 2).d64|Disk 2',
                ]
            }
        },
        
        # Collection priority expectations
        'collection_winners': {
            'Donkey Kong': ('NoIntro', 'NoIntro Donkey Kong content'),
            'Galaga': ('NoIntro', 'NoIntro Galaga content'),
        },
        
        # Edge case expectations
        'edge_cases': {
            'R-Type': ('Europe', 'R-Type Europe content'),
            'Archon 2 - Adept': ('USA', 'Archon II USA content'),  # Name cleaner converts "II" to "2"
            'Wizardry': ('Europe', 'Wizardry v1.0 content'),  # Version numbers get stripped, v1.0 selected
            'Elite': ('Europe', 'Elite Europe v1.1 content'),  # Europe v1.1 should win
            'Jumpman': ('', 'Jumpman no region content'),
            'Lode Runner': ('', 'Lode Runner tape content'),
        },
        
        # Files that should be skipped
        'skipped_files': [
            'desktop.ini', 'Thumbs.db', '.DS_Store',
            'README.txt', 'Manual.pdf',
            'Game.zip', 'Game.rar', 'Game.txt'
        ],
    }
