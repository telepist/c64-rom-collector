# Commodore 64 ROM Collection Manager

A comprehensive suite of Python tools for organizing, normalizing, and managing a Commodore 64 ROM collection.

## Overview

This project provides a set of tools to:

1. **Import and normalize** game information from various ROM collections
2. **Identify the best version** of each game based on format priority
3. **Create a consolidated "Best Collection"** with only the highest quality version of each game
4. **Verify the collection** for completeness and consistency

The system handles the complexities of C64 game naming conventions, multi-part games, and different ROM formats to build a clean, well-organized collection of Commodore 64 games.

## Tools Included

The package provides a unified command-line interface with the following commands:

### 1. `import` Command

Processes Commodore 64 game files from source directories and imports them into a SQLite database with normalized metadata.

```bash
./c64_manager.sh import
```

**Features:**
- Recursively scans the `roms/` directory for ROM files
- Cleans game names by removing region markers, version information, etc.
- Identifies multi-part games (games spanning multiple disks/tapes)
- Assigns format priorities (cartridge > disk > tape)
- Filters out utilities, tools, and non-game content
- Efficiently processes files in batches for better performance
- Creates database indexes for faster queries
- Provides detailed import statistics

### 2. `verify` Command

Verifies that all expected games are present in the "target" directory.

```bash
./c64_manager.sh verify
```

**Features:**
- Checks for missing single-part games
- Checks for missing multi-part games
- Reports detailed statistics about the collection
- Analyzes discrepancies between expected and actual files

### 3. `generate` Command

Creates a shell script to copy the best version of each game to the "target" directory.

```bash
./c64_manager.sh generate
```

### 4. `merge_collection.sh`

The generated shell script that performs the actual file copying operation.

### 5. `check_counts.py` and `compare_counts.py`

Additional verification tools to ensure collection integrity.

## Data Organization

The system maintains a SQLite database (`c64_games.db`) that tracks:
- Unique games with normalized names
- Different versions of games from each collection
- Individual files/parts for multi-part games
- Format and collection information for prioritization

## Format Priority System

The system prioritizes game formats in the following order:
1. **Cartridge files** (`.crt`) - Highest priority
2. **Disk images** (`.d64`, `.g64`, `.nib`) - Medium priority
3. **Tape images** (`.tap`, `.t64`) - Lowest priority

This ensures that the "target" directory contains the optimal format for each game.

## Multi-Part Game Handling

Multi-part games (those spanning multiple disks or tapes) are identified by:
- Patterns like `(Disk X)`, `(Side X)`, `(Part X)` in filenames
- Each part is tracked separately in the database
- Parts are kept together in the "target" directory

## Merge Rules

The system uses a sophisticated set of rules to select the best version of each game for the target collection:

### 1. Name Normalization
Before merging, game names are normalized through these steps:
- Removal of region markers (USA, Europe, PAL, NTSC, etc.)
- Removal of version information (v1.0, Version 2, etc.)
- Removal of collection markers (Compilation, Collection, etc.)
- Conversion of Roman numerals to Arabic numbers (II → 2, III → 3, etc.)
- Removal of other unnecessary information in parentheses

### 2. Format Selection
When multiple versions of the same game exist in different formats:
- Cartridge versions (`.crt`) are preferred over all others
- Disk image formats (`.d64`, `.g64`, `.nib`) are the second choice
- Tape formats (`.tap`, `.t64`) are used only if no better options exist

### 3. Collection Prioritization
When the same game with the same format exists in multiple collections:
- No-Intro collection is generally preferred
- Other collections are used in alphabetical order

### 4. Multi-Part Game Handling
For games that span multiple files (disks/tapes):
- All parts of a game are taken from the same collection and format
- Parts are kept together and named consistently
- If a game exists as both single and multi-part, the format priority rule applies first

### 5. File Selection Process
The merge process selects the best version of each game by:
1. For single-part games:
   - Select the version with highest format priority
   - If multiple versions have same format, prefer No-Intro collection
   - Otherwise use alphabetically first collection
2. For multi-part games:
   - Select all parts from the same version (same collection and format)
   - Apply same priority rules as single-part games
   - Keep parts together and ordered by part number

### 6. Naming in Target Directory
- Single part games: `<clean_name>.<format>`
- Multi part games: `<clean_name> (Disk <part_number>).<format>`
- This ensures consistent naming regardless of the original file name variations

## Project Structure

The project uses the following directory structure:

- `src/` - Contains source code
  - `core/` - ROM processing, importing, merging, verification
  - `db/` - Database operations and data models
  - `files/` - File system operations and path handling
  - `utils/` - General utility functions and name cleaning
  - `cli.py` - Command-line interface
- `roms/` - Contains original ROM collections (No-Intro, OneLoad64, etc.)
- `target/` - Contains the consolidated best version of each game
- `tests/` - Comprehensive test suite mirroring the main package structure
- `c64_games.db` - SQLite database containing normalized game metadata
- `c64_manager.sh` - Main shell script for running the manager
- `merge_collection.sh` - Generated script to copy games to the target directory

## Usage Instructions

### 1. Quick Start

1. Place your ROM collections in the `roms/` directory:
   - Create a subdirectory for each collection (e.g., `roms/No-Intro/`, `roms/OneLoad64/`)
   - Put your ROM files into these subdirectories

2. Run the all-in-one command to process your collection:
   ```bash
   ./c64_manager.sh run
   ```

   This command will:
   1. Import and process your ROM collections
   2. Generate the merge script
   3. Create your consolidated collection in the `target` directory

### 2. Step-by-Step Process

If you prefer more control or need to troubleshoot, you can run each step separately:

#### a. Initial Setup

1. Place your ROM collections in the `roms/` directory (each collection should be a separate subdirectory)

2. Run the import script to scan files and create the database:
   ```bash
   ./c64_manager.sh import
   ```
   
   This step will:
   - Recursively scan all collections in the `roms/` directory
   - Filter out non-game files and system utilities
   - Process and normalize all game files
   - Create a SQLite database with all game information
   - Display import statistics upon completion

#### b. Generate and Run Collection Merge

1. Generate the merge script (creates instructions for consolidating your collection):
   ```bash
   ./c64_manager.sh generate
   ```

2. Execute the merge to create your consolidated collection in the "target" directory:
   ```bash
   ./c64_manager.sh merge
   ```

### 3. Verify the Collection

Run the verification script to ensure all expected games are in the collection:
```bash
./c64_manager.sh verify
```

You can also use other commands:
```bash
./c64_manager.sh count    # Run the check_counts.py script
./c64_manager.sh compare  # Run the compare_counts.py script
./c64_manager.sh help     # Show all available commands
```

## Notes on Collection Inconsistencies

The verification process may show discrepancies between expected and actual file counts due to:

1. Inconsistent naming of multi-part games (some with `(Disk X)` pattern, some without)
2. Different formats of the same game present in the collection
3. Database counting issues related to multi-part game handling

The `check_missing.py` script includes detailed analysis functions to identify and explain these discrepancies.

## Requirements

- Python 3.6 or higher
- SQLite3
- Basic shell environment for running the merge script

## License

This project is for personal use only.
