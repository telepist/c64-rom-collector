# Commodore 64 ROM Collection Manager

A comprehensive suite of Python tools for organizing, normalizing, and managing a Commodore 64 ROM collection.

## Overview

This project provides a set of tools to:

1. **Import and normalize** game information from various ROM collections
2. **Identify the best version** of each game based on format priority
3. **Create a consolidated "Best Collection"** with only the highest quality version of each game

The system handles the complexities of C64 game naming conventions, multi-part games, and different ROM formats to build a clean, well-organized collection of Commodore 64 games.

## Platform Support

The tool runs on both Unix-like systems (Linux, macOS) and Windows:
- For Unix-like systems and Git Bash: Use `c64_manager.sh`
- For Windows Command Prompt: Use `c64_manager.cmd`

All commands described below work identically on both platforms - just use the appropriate script for your environment.

## Tools Included

The package provides a unified command-line interface with the following commands:

### 1. `run` Command

Executes the complete ROM collection management process by running the import, generate, and merge commands in sequence.

Unix-like systems:
```bash
./c64_manager.sh run
```

Windows CMD:
```cmd
c64_manager.cmd run
```

**Features:**
- Imports and processes ROM collections
- Generates the merge plan for best versions
- Creates the consolidated collection in one step
- Provides a convenient all-in-one solution

### 2. `import` Command

Processes Commodore 64 game files from source directories and imports them into a SQLite database with normalized metadata.

Unix-like systems:
```bash
./c64_manager.sh import
```

Windows CMD:
```cmd
c64_manager.cmd import
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

### 3. `generate` Command

Analyzes the imported ROM collection and creates a merge plan that identifies the best version of each game.

Unix-like systems:
```bash
./c64_manager.sh generate
```

Windows CMD:
```cmd
c64_manager.cmd generate
```

### 4. `merge` Command

Creates the consolidated collection by copying the best version of each game to the target directory, following format priorities and organization rules.

Unix-like systems:
```bash
./c64_manager.sh merge
```

Windows CMD:
```cmd
c64_manager.cmd merge
```

**Features:**
- Copies each game's best version based on format priorities
- Properly organizes multi-part games into subdirectories
- Maintains consistent naming across the collection
- Cleans target directory before merge to prevent conflicts
- Handles platform-specific path issues automatically
- Uses an internal file copying script for reliable execution

### 5. `count` Command

Additional tool to verify ROM counts and collection statistics.

Unix-like systems:
```bash
./c64_manager.sh count
```

Windows CMD:
```cmd
c64_manager.cmd count
```

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
- `build/` - Contains generated files and build artifacts
  - `c64_games.db` - SQLite database with normalized game metadata
  - `merge_collection.sh` - Generated script for collection management
- `c64_manager.sh` - Main shell script for running the manager
- `c64_manager.cmd` - Windows Command Prompt script for running the manager

## Usage Instructions

### 1. Quick Start

1. Place your ROM collections in the `roms/` directory:
   - Create a subdirectory for each collection (e.g., `roms/No-Intro/`, `roms/OneLoad64/`)
   - Put your ROM files into these subdirectories

2. Run the all-in-one command to process your collection:

   Unix-like systems:
   ```bash
   ./c64_manager.sh run
   ```

   Windows CMD:
   ```cmd
   c64_manager.cmd run
   ```

   This command will:
   1. Import and process your ROM collections
   2. Analyze and plan the collection merge
   3. Create your consolidated collection in the `target` directory

### 2. Step-by-Step Process

If you prefer more control or need to troubleshoot, you can run each step separately:

#### a. Initial Setup

1. Place your ROM collections in the `roms/` directory (each collection should be a separate subdirectory)

2. Run the import script to scan files and create the database:

   Unix-like systems:
   ```bash
   ./c64_manager.sh import
   ```

   Windows CMD:
   ```cmd
   c64_manager.cmd import
   ```

   This step will:
   - Recursively scan all collections in the `roms/` directory
   - Filter out non-game files and system utilities
   - Process and normalize all game files
   - Create a SQLite database with all game information
   - Display import statistics upon completion

#### b. Generate and Run Collection Merge

1. Generate the merge plan to identify the best versions:

   Unix-like systems:
   ```bash
   ./c64_manager.sh generate
   ```

   Windows CMD:
   ```cmd
   c64_manager.cmd generate
   ```

2. Run the merge command to create your consolidated collection:

   Unix-like systems:
   ```bash
   ./c64_manager.sh merge
   ```

   Windows CMD:
   ```cmd
   c64_manager.cmd merge
   ```

### 3. Additional Commands

You can use other commands:

   Unix-like systems:
   ```bash
   ./c64_manager.sh count    # Check ROM counts and collection statistics
   ./c64_manager.sh version  # Show version information
   ./c64_manager.sh help     # Show all available commands
   ```

   Windows CMD:
   ```cmd
   c64_manager.cmd count    # Check ROM counts and collection statistics
   c64_manager.cmd version  # Show version information
   c64_manager.cmd help     # Show all available commands
   ```

## Notes on Collection Organization

The collection management system handles:

1. Consistent naming of multi-part games using standardized patterns 
2. Different formats of the same game across collections
3. Database tracking of all ROM files and their relationships

The system ensures that games are properly organized by:
- Using standard patterns for multi-part game naming
- Maintaining format consistency within game sets
- Tracking all versions and relationships in the database

## Development Environment

### VS Code Configuration

The project includes VS Code configuration files for improved development experience:

- **`.vscode/settings.json`**: Configures Python analysis paths and linting settings
- **`.vscode/launch.json`**: Provides debug configurations for running tests and CLI commands
- **`.vscode/tasks.json`**: Defines tasks for running tests and build operations
- **`pyrightconfig.json`**: Configures Pylance for proper import resolution
- **`.env`**: Sets PYTHONPATH for consistent import resolution

These configurations ensure that:
- Import statements are properly resolved by Pylance
- Tests can be run and debugged from VS Code
- The project structure is properly understood by the editor

If you're using VS Code, you may need to reload the window (Ctrl+Shift+P → "Developer: Reload Window") after opening the project for the first time to apply the Python path configuration.

### Running Tests

The project includes comprehensive test suites:

**All tests:**
```bash
./c64_manager.sh test
```

**Integration tests only:**
```bash
PYTHONPATH=src python -m pytest tests/integration/ -v
```

**Unit tests only:**
```bash
PYTHONPATH=src python -m pytest tests/unit/ -v
```

## Requirements

- Python 3.6 or higher
- SQLite3
- Basic shell environment for running the merge script

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Note**: This tool is for managing ROM collections and does not include any ROM files. Users are responsible for ensuring they have the legal right to use any ROM files they manage with this tool.
