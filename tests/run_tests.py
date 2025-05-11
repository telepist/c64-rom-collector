"""
Test runner for all unit tests.
"""
import unittest
import sys
import os
from pathlib import Path

# Add the project root directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_tests(args=None):
    """Run the test suite with specified options."""
    # Discover tests
    test_loader = unittest.TestLoader()
    
    if args and args.test:
        # Run specific test module
        module_name = args.test
        if not module_name.startswith('test_'):
            module_name = f'test_{module_name}'
          # Look for test file in unit directory (flat structure)
        test_file = Path(__file__).parent / 'unit' / f'{module_name}.py'
        if not test_file.exists():
            print(f"Error: Test module '{module_name}' not found.")
            return 1
            
        test_suite = test_loader.discover(str(Path(__file__).parent / 'unit'),
                                          pattern=f'{module_name}.py',
                                          top_level_dir=str(Path(__file__).parent))
    else:
        # Run all tests recursively
        test_suite = test_loader.discover(str(Path(__file__).parent / 'unit'), 
                                          pattern='test_*.py',
                                          top_level_dir=str(Path(__file__).parent))
    
    # Set up the test runner
    runner_class = unittest.TextTestRunner
    runner_kwargs = {'verbosity': 2}
    
    if args and getattr(args, 'xml', False):
        try:
            import xmlrunner
            runner_class = xmlrunner.XMLTestRunner
            runner_kwargs = {'output': 'test-reports', 'verbosity': 2}
        except ImportError:
            print("Warning: xmlrunner not found. Using default test runner.")
    
    # Run tests
    runner = runner_class(**runner_kwargs)
    result = runner.run(test_suite)
    
    # Return exit code (0 for success, 1 for failure)
    return len(result.failures) + len(result.errors)


if __name__ == '__main__':
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description="C64 ROM Collection Manager Test Runner")
    parser.add_argument('--test', help='Run a specific test module (without the test_ prefix)')
    parser.add_argument('--xml', action='store_true', help='Generate XML test reports')
    args = parser.parse_args()
    
    # Run tests and set exit code
    sys.exit(run_tests(args))
