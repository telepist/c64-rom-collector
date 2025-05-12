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
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    test_base = Path(__file__).parent
    found_tests = False
    
    def is_running_all_tests():
        return args is None or not hasattr(args, 'type') or not args.type
        
    def is_running_test_type(test_type):
        return is_running_all_tests() or \
               (hasattr(args, 'type') and args.type == test_type)
    
    if args and hasattr(args, 'test') and args.test:
        # Run specific test module
        module_name = args.test
        if not module_name.startswith('test_'):
            module_name = f'test_{module_name}'
        module_pattern = f'{module_name}.py'
        
        # Check test directories based on type
        test_dirs = []
        if is_running_test_type("unit"):
            test_dirs.append('unit')
        if is_running_test_type("integration"):
            test_dirs.append('integration')
            
        for test_dir in test_dirs:
            path = test_base / test_dir / module_pattern
            if path.exists():
                suite = test_loader.discover(
                    str(path.parent),
                    pattern=module_pattern,
                    top_level_dir=str(test_base)
                )
                test_suite.addTests(suite)
                found_tests = True
                
        if not found_tests:
            test_type = f" in {args.type} tests" if hasattr(args, 'type') and args.type else ""
            print(f"Error: Test module '{module_name}' not found{test_type}.")
            return 1
    else:
        # Run all tests of specified type
        if is_running_test_type("unit"):
            unit_dir = test_base / 'unit'
            if unit_dir.exists():
                unit_tests = test_loader.discover(
                    str(unit_dir),
                    pattern='test_*.py',
                    top_level_dir=str(test_base)
                )
                test_suite.addTests(unit_tests)
                found_tests = True
            
        if is_running_test_type("integration"):
            int_dir = test_base / 'integration'
            if int_dir.exists():
                integration_tests = test_loader.discover(
                    str(int_dir),
                    pattern='test_*.py',
                    top_level_dir=str(test_base)
                )
                test_suite.addTests(integration_tests)
                found_tests = True
        
        if not found_tests:
            test_type = "unit" if hasattr(args, 'type') and args.type == "unit" else \
                       "integration" if hasattr(args, 'type') and args.type == "integration" else \
                       "unit or integration"
            print(f"No {test_type} tests found.")
            return 1
    
    # Set up the test runner
    runner_class = unittest.TextTestRunner
    runner_kwargs = {'verbosity': 2}
    
    if args and hasattr(args, 'xml') and args.xml:
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
