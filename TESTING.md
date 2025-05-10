# Testing Guide for C64 ROM Collector

This guide explains how to run tests for the C64 ROM Collector project.

## Prerequisites

1. Python 3.6 or higher is required
2. Optional: Install the `unittest-xml-reporting` package for XML test reports:
   ```
   pip install unittest-xml-reporting
   ```

## Running Tests

### Using the CLI

Run all tests:
```bash
python c64_manager.py test
```

Run a specific test module:
```bash
python c64_manager.py test --module name_cleaner
```

Generate XML test reports (requires unittest-xml-reporting package):
```bash
python c64_manager.py test --xml
```

You can combine these options:
```bash
python c64_manager.py test --module format_handler --xml
```

#### Available Test Modules

- `database`: Tests for database operations
- `file_ops`: Tests for file operations
- `format_handler`: Tests for ROM format handling
- `importer`: Tests for the import process
- `merger`: Tests for the merge script generation
- `name_cleaner`: Tests for ROM name cleaning
- `processor`: Tests for file processing
- `verifier`: Tests for collection verification

### Using the Test Runner Directly

You can also run tests using the test runner directly:

```bash
python -m tests.run_tests
```

Or run a specific test:
```bash
python -m tests.run_tests --test name_cleaner
```

## Writing Tests

Tests are located in the `tests/unit` directory. Each test file should:

1. Follow the naming convention `test_*.py`
2. Contain test classes that inherit from `unittest.TestCase`
3. Include test methods that start with `test_`

### Example Test

```python
import unittest
from c64collector.utils.name_cleaner import clean_name

class TestNameCleaner(unittest.TestCase):
    
    def test_clean_name_removes_region(self):
        self.assertEqual(clean_name("Game (USA).crt"), "Game")
        self.assertEqual(clean_name("Game (Europe).d64"), "Game")
```

## Test Coverage

To run tests with coverage reporting:

1. Install the coverage package:
   ```
   pip install coverage
   ```

2. Run the tests with coverage:
   ```
   coverage run -m tests.run_tests
   ```

3. Generate a coverage report:
   ```
   coverage report
   ```

   Or an HTML report:
   ```
   coverage html
   ```

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
