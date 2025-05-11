---
applyTo: '**'
---
# AI Assistant Instructions

## Initial Context Gathering
1. At the start of each new chat session, immediately check the README.md file to understand:
   - Project overview and purpose
   - Available tools and commands
   - Project structure and conventions
   - Database schema (if applicable)
   - File format priorities and handling rules
   - Special cases (like multi-part files)

## Project Structure
The project is organized into the following main directories:

```
.
├── roms/                # ROM collections (No-Intro, OneLoad64, etc.)
├── src/                # Source code
│   ├── core/          # ROM processing, importing, merging, verification
│   ├── db/           # Database operations and data access
│   ├── files/        # File operations and path handling
│   ├── utils/        # General utility functions and name cleaning
│   └── cli.py        # Command-line interface
├── target/            # Output directory for processed ROMs
└── tests/             # Test suite with unit tests
```

Special Directories:
- `roms/`: Contains original ROM collections (excluded from version control)
- `src/`: Contains source code
- `target/`: Stores processed and normalized ROM files
- `tests/`: Comprehensive test suite mirroring the main package structure

Key Files:
- `c64_manager.sh`: Main command-line interface
- `c64_games.db`: SQLite database for ROM metadata
- `merge_collection.sh`: Generated script for collection management

## Coding Standards

### Code Organization
1. Follow modular design principles:
   - Each module should have a single, well-defined responsibility
   - Limit module dependencies and coupling
   - Use clear and consistent naming conventions
   - Keep modules focused and concise

### Separation of Concerns
1. Maintain clear layer separation:
   - Core logic (`src/core/`): Business rules and ROM processing
   - Data access (`src/db/`): Database operations and data models
   - File operations (`src/files/`): File system operations and path handling
   - Utilities (`src/utils/`): General helper functions
   - CLI interface (`src/cli.py`): Command-line interface and user interaction
2. Avoid mixing concerns:
   - Keep UI/CLI logic separate from business logic
   - Database operations should be isolated in the db layer
   - File operations should be handled by files module
3. File system access guidelines:
   - All file operations must go through the `src/files` module
   - Core modules should use file operations from the files module
   - Use consistent path handling through provided functions
   - Handle file system errors at appropriate levels
   - Provide meaningful error messages for file operations
   - Use type hints and proper error handling
   - Support both Windows and Unix-style paths
   - Follow platform-independent path handling practices

### Testing Requirements
1. All code must be unit tested:
   - Every module must have corresponding tests in `tests/unit/`
   - Test files should use a flat structure under `tests/unit/`
   - Test files should be named `test_*.py` matching their tested module
   - Each public function must have test coverage
   - Test edge cases and error conditions
2. Test organization:
   - Group related test cases using test classes
   - Use descriptive test names that explain the scenario and tested module
   - Test filenames should clearly indicate their tested module (e.g., `test_database.py` for `src/db/database.py`)
   - Follow the "Arrange-Act-Assert" pattern
   - Mock external dependencies (database, filesystem)

### Best Practices
1. Code quality:
   - Write self-documenting code with clear names
   - Add docstrings to all public functions and classes
   - Keep functions small and focused
   - Use type hints for better code clarity
2. Error handling:
   - Use appropriate exception types
   - Handle errors at the appropriate level
   - Provide meaningful error messages
3. Configuration:
   - Keep configuration separate from code
   - Use environment variables for sensitive data
   - Make parameters configurable where appropriate

## Command Usage
Follow the established command patterns:
- Use `./c64_manager.sh` for main operations
    - `run` for running the main script, runs `import`, `generate`, and `merge` commands
    - `import` for importing ROMs
    - `generate` for generating output files
    - `merge` for merging collections
    - `clean` for cleaning up files
    - `test` for running tests
    
- Respect the command structure for import, verify, and generate operations