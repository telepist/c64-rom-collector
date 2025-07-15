"""
Command-line interface for the C64 ROM collector.
"""
import argparse
import sys
import os
import time
import subprocess
import platform
from pathlib import Path

# Local imports from src/
from config import ROMS_DIR, DATABASE_PATH, MERGE_SCRIPT_PATH, TARGET_DIR
from core.importer import import_games
from core.merger import generate_merge_script, clean_target_directory


def detect_platform_and_shell():
    """Detect the current platform and shell environment."""
    os_name = platform.system().lower()
    env_shell = os.environ.get('SHELL', '').lower()
    
    if os_name == 'windows':
        if 'bash' in env_shell or 'git' in env_shell:
            return 'bash'
        return 'cmd'
    return 'shell'  # Unix-like systems


def run_merge_script(script_path, target_dir=str(TARGET_DIR)):
    """
    Run the merge script appropriate for the current platform.
    """
    script_dir = Path(script_path).parent
    script_name = Path(script_path).stem

    # Get both potential script paths
    sh_script = script_dir / f"{script_name}.sh"
    cmd_script = script_dir / f"{script_name}.cmd"

    # Detect environment
    shell_type = detect_platform_and_shell()
    
    try:
        if shell_type == 'cmd':
            if not cmd_script.exists():
                raise FileNotFoundError(f"Windows batch script not found: {cmd_script}")
            result = subprocess.run([str(cmd_script)], shell=True, check=True)
        else:  # bash or shell
            if not sh_script.exists():
                raise FileNotFoundError(f"Shell script not found: {sh_script}")
            if platform.system() != 'Windows':
                # Make script executable on Unix-like systems
                os.chmod(str(sh_script), 0o755)
            if shell_type == 'bash':
                # Git Bash on Windows or bash on Unix
                result = subprocess.run(['bash', str(sh_script)], check=True)
            else:
                # Unix shell
                result = subprocess.run([str(sh_script)], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing merge script: {e}")
        return False
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Run the 'generate' command first to create the merge script.")
        return False


def main():
    parser = argparse.ArgumentParser(description="C64 ROM Collection Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Import command
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
    merge_parser.add_argument("--target", default=str(TARGET_DIR), help="Target directory")
    merge_parser.add_argument("--script", default=str(MERGE_SCRIPT_PATH), help="Merge script to run")
    
    # Version command
    subparsers.add_parser("version", help="Show version information")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("type", nargs="?", choices=["unit", "integration"], 
                            help="Test type to run (unit or integration). If not specified, runs both.")
    test_parser.add_argument("--test", help="Run specific test module")
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
        
        # Clean target directory
        print(f"Cleaning target directory '{args.target}' first...")
        clean_result = clean_target_directory(args.target)

        print("Running merge script to create target collection...")
        
        if clean_result:
            # Run the appropriate merge script
            script_path = os.path.abspath(args.script)
            success = run_merge_script(script_path, args.target)
            
            if success:
                end_time = time.time()
                print("Merge completed successfully!")
                print(f"Execution time: {end_time - start_time:.2f} seconds")
        else:
            print("Aborting merge due to errors while cleaning target directory.")
    
    elif args.command == "version":
        print("C64 ROM Collection Manager v1.0.0")
    
    elif args.command == "test":
        # Add parent directory to path for importing tests
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from tests.run_tests import run_tests
        
        class TestArgs:
            def __init__(self, test_type=None, module=None, xml=False):
                self.type = test_type  # Can be "unit", "integration", or None (for both)
                self.test = module
                self.xml = xml
        
        if args.type == "unit":
            print("Running unit tests...")
        elif args.type == "integration":
            print("Running integration tests...")
        else:
            print("Running all tests...")
        
        test_args = TestArgs(args.type, args.test, args.xml)
        sys.exit(run_tests(test_args))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
