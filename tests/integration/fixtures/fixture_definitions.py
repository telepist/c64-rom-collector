"""Enhanced integration test fixtures for comprehensive testing."""

# Regional Variations Test Cases
REGIONAL_FIXTURES = {
    # Game with multiple regions - should select Europe first
    "Bubble Bobble (Europe).d64": "Europe Bubble Bobble content",
    "Bubble Bobble (USA).d64": "USA Bubble Bobble content", 
    "Bubble Bobble (World).d64": "World Bubble Bobble content",
    
    # Game with PAL/NTSC variants - should select PAL
    "Defender (PAL).d64": "PAL Defender content",
    "Defender (NTSC).d64": "NTSC Defender content",
    
    # Game with complex region strings
    "Maniac Mansion (Europe, USA).d64": "Europe USA Maniac Mansion content",
    "Maniac Mansion (Japan).d64": "Japan Maniac Mansion content",
    
    # Single region games
    "Tetris (Europe).d64": "Europe Tetris content",
    "Pacman (USA).d64": "USA Pacman content",
}

# Format Priority Test Cases  
FORMAT_PRIORITY_FIXTURES = {
    # Same game, different formats - should prioritize crt > d64 > tap
    "Ghostbusters.crt": "Ghostbusters cartridge content",
    "Ghostbusters.d64": "Ghostbusters disk content",
    "Ghostbusters.tap": "Ghostbusters tape content",
    
    # Region vs Format priority - d64 USA should beat tap Europe
    "Frogger (USA).d64": "USA Frogger disk content",
    "Frogger (Europe).tap": "Europe Frogger tape content",
    
    # Different formats with regions
    "Pitfall (Europe).crt": "Europe Pitfall cartridge content",
    "Pitfall (USA).d64": "USA Pitfall disk content",
    "Pitfall (World).tap": "World Pitfall tape content",
}

# Multi-disk Game Test Cases
MULTIDISK_FIXTURES = {
    # Standard multi-disk game
    "Ultima IV (Disk 1).d64": "Ultima IV disk 1 content",
    "Ultima IV (Disk 2).d64": "Ultima IV disk 2 content", 
    "Ultima IV (Disk 3).d64": "Ultima IV disk 3 content",
    "Ultima IV (Disk 4).d64": "Ultima IV disk 4 content",
    
    # Multi-disk with sides
    "Wasteland (Side 1).d64": "Wasteland side 1 content",
    "Wasteland (Side 2).d64": "Wasteland side 2 content",
    
    # Multi-disk with regions (should NOT extract regions)
    "Bard's Tale (Disk 1 Europe).d64": "Bard's Tale disk 1 content",
    "Bard's Tale (Disk 2 Europe).d64": "Bard's Tale disk 2 content",
    
    # Multi-disk with PAL/NTSC (should NOT extract regions)
    "Pool of Radiance (Disk 1 PAL NTSC).d64": "Pool of Radiance disk 1 content",
    "Pool of Radiance (Disk 2 PAL NTSC).d64": "Pool of Radiance disk 2 content",
}

# Collection Priority Test Cases
COLLECTION_FIXTURES = {
    # Same game in different collections - should prioritize NoIntro > TOSEC
    "nointro": {
        "Donkey Kong (Europe).d64": "NoIntro Donkey Kong content",
        "Galaga.crt": "NoIntro Galaga content",
    },
    "tosec": {
        "Donkey Kong (Europe).d64": "TOSEC Donkey Kong content", 
        "Galaga.crt": "TOSEC Galaga content",
    },
    "oneload64": {
        "Donkey Kong (Europe).d64": "OneLoad64 Donkey Kong content",
    }
}

# Edge Cases
EDGE_CASE_FIXTURES = {
    # Games with special characters
    "R-Type (Europe).d64": "R-Type Europe content",
    "Archon II - Adept (USA).d64": "Archon II USA content",
    
    # Games with version numbers
    "Wizardry v1.0 (Europe).d64": "Wizardry v1.0 content",
    "Wizardry v2.1 (USA).d64": "Wizardry v2.1 content",
    
    # Games with multiple parentheses
    "Elite (Europe) (v1.1).d64": "Elite Europe v1.1 content",
    "Elite (USA) (Crack).d64": "Elite USA Crack content",
    
    # No region specified
    "Jumpman.d64": "Jumpman no region content",
    "Lode Runner.tap": "Lode Runner tape content",
}

# Skippable Files (should be ignored)
SKIP_FIXTURES = {
    # System files
    "desktop.ini": "Windows system file",
    "Thumbs.db": "Windows thumbnail cache",
    ".DS_Store": "macOS system file",
    
    # Documentation
    "README.txt": "Documentation file",
    "Manual.pdf": "Game manual",
    
    # Unsupported formats
    "Game.zip": "Compressed archive",
    "Game.rar": "Compressed archive",
    "Game.txt": "Text file",
}
