# Testing Guide for C64 ROM Collector

This guide explains how to run tests for the C64 ROM Collector project.

## Prerequisites

1. Python 3.6 or higher is required
2. Required packages:
   ```
   pip install pytest
   ```
3. Optional packages:
   - For XML test reports:
     ```
     pip install unittest-xml-reporting
     ```
   - For coverage reports:
     ```
     pip install coverage
     ```

## Test Output Location

Test output files (databases, generated scripts, etc.) are stored in the `build/test_output` directory:
- `build/test_output/target/`: Temporary target directory for test ROM files
- `build/test_output/test.db`: Test database file
- `build/test_output/merge.sh`: Generated merge script for tests

This directory is:
- Created automatically during test runs
- Cleaned up automatically between test cases
- Listed in `.gitignore` (no test artifacts are committed)

### Unit Tests
Unit tests use mocked file system operations and databases where possible, minimizing actual file operations.

### Integration Tests
Integration tests use the `build/test_output` directory for actual file operations, simulating real usage of the application.

## Running Tests

### Using the CLI

Run all tests:
```bash
./c64_manager.sh test
```

Run only unit tests:
```bash
./c64_manager.sh test unit
```

Run only integration tests:
```bash
./c64_manager.sh test integration
```

Run a specific test module:
```bash
./c64_manager.sh test --test name_cleaner
```

Generate XML test reports (requires unittest-xml-reporting package):
```bash
./c64_manager.sh test --xml
```

You can combine these options:
```bash
./c64_manager.sh test unit --test format_handler --xml
```

#### Available Test Modules

Unit Tests:
- `database`: Tests for database operations
- `files`: Tests for file operations, including:
  - File operations and utilities
  - Path sanitization
  - Script generation operations
- `format_handler`: Tests for ROM format handling
- `importer`: Tests for the import process
- `merger`: Tests for the merge script generation
- `name_cleaner`: Tests for ROM name cleaning
- `processor`: Tests for file processing operations

Integration Tests:
- `cli_integration`: Tests for complete workflow and CLI operations

### Using the Test Runner Directly

You can also run tests using the test runner directly:

```bash
python -m tests.run_tests
```

Run specific test types:
```bash
python -m tests.run_tests --type unit
python -m tests.run_tests --type integration
```

Or run a specific test:
```bash
python -m tests.run_tests --test name_cleaner
```

## Writing Tests

Tests are organized in two directories:
- `tests/unit/`: Unit tests for individual components
- `tests/integration/`: Integration tests for complete workflows

Each test file should:
1. Follow the naming convention `test_*.py`
2. Contain test classes that inherit from `unittest.TestCase`
3. Include test methods that start with `test_`

### Example Test

```python
import unittest
from src.utils.name_cleaner import clean_name

class TestNameCleaner(unittest.TestCase):
    
    def test_clean_name_removes_region(self):
        self.assertEqual(clean_name("Game (USA).crt"), "Game")
        self.assertEqual(clean_name("Game (Europe).d64"), "Game")
```

## Test Coverage

The project aims for high test coverage across all core functionality. Coverage reports help identify untested code paths.

To run tests with coverage reporting:

1. Run the tests with coverage:
   ```
   coverage run -m tests.run_tests
   ```

2. Generate a coverage report:
   ```
   coverage report
   ```
   This shows a summary of coverage per module.

3. Generate a detailed HTML report:
   ```
   coverage html
   ```
   This creates an interactive HTML report in the `htmlcov` directory.

### Coverage Goals

- Core modules (src/core/): 90%+ coverage
- Database operations (src/db/): 90%+ coverage
- File operations (src/files/): 85%+ coverage
- Utilities (src/utils/): 85%+ coverage

Critical functionality such as file operations, database management, and ROM processing should have comprehensive test coverage.

## Mocking

For tests that require database or filesystem access, use the `unittest.mock` module to mock these dependencies.

Example:
```python
from unittest import mock

@mock.patch('os.walk')
def test_with_mocked_filesystem(mock_walk):
    mock_walk.return_value = [('/base', [], ['file1.txt'])]
    # Your test code here
```
