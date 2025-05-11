"""
Command-line interface for the C64 ROM collector.
"""
import argparse
import time
import sys
import os
import subprocess

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import ROMS_DIR, DATABASE_PATH, MERGE_SCRIPT_PATH, TARGET_DIR
from src.core.importer import import_games
from src.core.merger import generate_merge_script, clean_target_directory


def main():
    parser = argparse.ArgumentParser(description="C64 ROM Collection Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")    # Import command
    import_parser = subparsers.add_parser("import", help="Import games from ROM directories")
    import_parser.add_argument("--src", default=str(ROMS_DIR), help="ROMs directory")
    import_parser.add_argument("--db", default=str(DATABASE_PATH), help="Database path")
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate merge script")
    generate_parser.add_argument("--db", default=str(DATABASE_PATH), help="Database path")
    generate_parser.add_argument("--output", default=str(MERGE_SCRIPT_PATH), help="Output script path")
    generate_parser.add_argument("--target", default=str(TARGET_DIR), help="Target directory")
      # Merge command
    merge_parser = subparsers.add_parser("merge", help="Merge the collection to target directory")
    merge_parser.add_argument("--target", default=str(), help="Target directory")
    merge_parser.add_argument("--script", default=str(MERGE_SCRIPT_PATH), help="Merge script to run")
    
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
    
    elif args.command == "merge":
        start_time = time.time()
        print(f"Running merge script to create target collection...")
        
        # Clean target directory
        print(f"Cleaning target directory '{args.target}' first...")
        clean_result = clean_target_directory(args.target)
        
        if clean_result:
            # Run the merge script
            try:
                script_path = os.path.abspath(args.script)
                if os.path.exists(script_path):
                    # Make sure the script is executable
                    if os.name != 'nt':  # Not needed on Windows
                        os.chmod(script_path, 0o755)
                    
                    print(f"Executing merge script: {script_path}")
                    
                    # Handle execution differently based on platform
                    if os.name == 'nt':  # Windows
                        result = subprocess.run(['bash', script_path], shell=True, check=True)
                    else:  # Unix-like
                        result = subprocess.run([script_path], shell=True, check=True)
                    
                    end_time = time.time()
                    print(f"Merge completed successfully!")
                    print(f"Execution time: {end_time - start_time:.2f} seconds")
                else:
                    print(f"Error: Merge script '{script_path}' not found.")
                    print(f"Run the 'generate' command first to create the merge script.")
            except subprocess.CalledProcessError as e:
                print(f"Error executing merge script: {e}")
        else:
            print("Aborting merge due to errors while cleaning target directory.")
    
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
