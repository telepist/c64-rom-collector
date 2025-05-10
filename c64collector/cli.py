"""
Command-line interface for the C64 ROM collector.
"""
import argparse
import time
import sys
import os

# Add parent directory to path for imports to work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from c64collector.core.importer import import_games
from c64collector.core.merger import generate_merge_script
from c64collector.core.verifier import check_missing_files


def main():
    parser = argparse.ArgumentParser(description="C64 ROM Collection Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Import command
    import_parser = subparsers.add_parser("import", help="Import games from source directories")
    import_parser.add_argument("--src", default="src", help="Source directory")
    import_parser.add_argument("--db", default="c64_games.db", help="Database path")
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate merge script")
    generate_parser.add_argument("--db", default="c64_games.db", help="Database path")
    generate_parser.add_argument("--output", default="merge_collection.sh", help="Output script path")
    generate_parser.add_argument("--target", default="target", help="Target directory")
    
    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify the collection")
    verify_parser.add_argument("--db", default="c64_games.db", help="Database path")
    verify_parser.add_argument("--target", default="target", help="Target directory")
    
    # Version command
    subparsers.add_parser("version", help="Show version information")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run unit tests")
    test_parser.add_argument("--module", help="Run specific test module")
    test_parser.add_argument("--xml", action="store_true", help="Generate XML test reports")
    
    args = parser.parse_args()
    
    if args.command == "import":
        start_time = time.time()
        stats = import_games(args.src, args.db)
        end_time = time.time()
        
        print("\nImport Statistics:")
        print(f"Processed files: {stats['processed_files']}")
        print(f"Skipped files:   {stats['skipped_files']}")
        print(f"Error files:     {stats['error_files']}")
        print(f"Unique games:    {stats['unique_games']}")
        print(f"Multi-part games: {stats.get('multi_games', 0)}")
        print(f"Execution time:  {end_time - start_time:.2f} seconds")
        
    elif args.command == "generate":
        start_time = time.time()
        file_count = generate_merge_script(args.db, args.output, args.target)
        end_time = time.time()
        
        print(f"Generated script for {file_count} files.")
        print(f"Execution time: {end_time - start_time:.2f} seconds")
        
    elif args.command == "verify":
        start_time = time.time()
        results = check_missing_files(args.db, args.target)
        end_time = time.time()
        
        print("\nVerification Results:")
        print(f"Expected files:  {results['total_expected']}")
        print(f"Actual files:    {results['total_actual']}")
        print(f"Missing files:   {results['total_missing']}")
        
        if results['missing_singles']:
            print(f"\nMissing single part games: {len(results['missing_singles'])}")
            for i, game in enumerate(results['missing_singles'][:5], 1):  # Show first 5 only
                print(f"{i}. Missing: {game['name']}")
                print(f"   Source: {game['source']}")
        
        if results['missing_multis']:
            print(f"\nMissing multi part games: {len(results['missing_multis'])}")
            for i, game in enumerate(results['missing_multis'][:5], 1):  # Show first 5 only
                print(f"{i}. Missing: {game['name']}")
                print(f"   Source: {game['source']}")
                
        print(f"\nExecution time: {end_time - start_time:.2f} seconds")
    
    elif args.command == "version":
        print("C64 ROM Collection Manager v1.0.0")
    
    elif args.command == "test":
        print("Running unit tests...")
        from tests.run_tests import run_tests
        
        class TestArgs:
            def __init__(self, module=None, xml=False):
                self.test = module
                self.xml = xml
        
        test_args = TestArgs(args.module, args.xml)
        sys.exit(run_tests(test_args))
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
