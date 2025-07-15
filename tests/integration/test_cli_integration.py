"""Integration tests for CLI commands."""
import unittest
import os
import shutil
import tempfile
import sqlite3
import sys
from pathlib import Path
from subprocess import run, PIPE

class TestCLIIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        # Get paths relative to this test file
        cls.test_dir = Path(__file__).parent.resolve()  # Get absolute path
        cls.fixtures_dir = cls.test_dir / "fixtures"
        cls.roms_dir = cls.fixtures_dir / "roms"
        
        # Get the project root directory (two levels up from the test file)
        cls.project_dir = cls.test_dir.parent.parent.resolve()  # Get absolute path
        cls.cli_path = cls.project_dir / "src" / "cli.py"
        
        # Use build directory for test output
        cls.build_dir = cls.project_dir / "build"
        cls.temp_dir = cls.build_dir / "test_output"
        cls.target_dir = cls.temp_dir / "target"
        cls.db_path = cls.temp_dir / "test.db"
        cls.merge_script = cls.temp_dir / "merge.sh"
        
        # Create build and target directories
        cls.build_dir.mkdir(exist_ok=True)
        cls.temp_dir.mkdir(exist_ok=True)
        cls.target_dir.mkdir(exist_ok=True)
        
        # Verify test files exist
        if not cls.roms_dir.exists():
            raise RuntimeError(f"Test ROM directory not found: {cls.roms_dir}")
        
        # Print debug info
        print("\nTest setup:")
        print(f"ROMs dir: {cls.roms_dir}")
        print(f"Target dir: {cls.target_dir}")
        print(f"DB path: {cls.db_path}")
        
        # List ROM files
        rom_files = list(cls.roms_dir.glob("*"))
        if not rom_files:
            raise RuntimeError(f"No ROM files found in: {cls.roms_dir}")
        print(f"ROM files found: {[f.name for f in rom_files]}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up the test environment."""
        if cls.temp_dir.exists():
            shutil.rmtree(cls.temp_dir)
            
    def setUp(self):
        """Set up the test case."""
        # Clear target directory before each test
        if self.target_dir.exists():
            shutil.rmtree(self.target_dir)
        self.target_dir.mkdir(exist_ok=True)
        
        # Remove test database if it exists
        if self.db_path.exists():
            # On Windows, we need to ensure no processes are using the database
            try:
                self.db_path.unlink()
            except PermissionError:
                # Wait a moment and try again
                import time
                time.sleep(0.1)
                try:
                    self.db_path.unlink()
                except PermissionError:
                    # If still locked, use a different database name
                    import uuid
                    self.db_path = self.temp_dir / f"test_{uuid.uuid4().hex[:8]}.db"

    def _run_cli_command(self, command, *args):
        """Run a CLI command and return its output."""
        # Convert all arguments to strings
        str_args = [str(arg) for arg in args]
        
        # Build the command
        full_command = [sys.executable, str(self.cli_path), command]
        full_command.extend(str_args)
        
        print("\nExecuting command:", " ".join(full_command))
        print("Working directory:", str(self.project_dir))
        
        # Run the command with proper Python interpreter from project root
        result = run(
            full_command,
            stdout=PIPE,
            stderr=PIPE,
            text=True,
            check=False,
            cwd=str(self.project_dir)  # Set working directory to project root
        )
        
        # Always print output for debugging
        print("Command output:", result.stdout)
        if result.stderr:
            print("Command error:", result.stderr)
            
        return result
    
    def test_import_command(self):
        """Test the import command with test ROMs."""
        result = self._run_cli_command(
            "import",
            "--src", str(self.roms_dir),
            "--db", str(self.db_path)
        )
        
        self.assertEqual(result.returncode, 0, 
                        f"Import command failed:\nOutput: {result.stdout}\nError: {result.stderr}")
        
        # Verify database was created and has expected content
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check game count (should be 20 unique games based on comprehensive fixtures)
        cursor.execute("SELECT COUNT(*) FROM games")
        game_count = cursor.fetchone()[0]
        self.assertEqual(game_count, 20)  # 20 unique games in comprehensive fixtures
        
        conn.close()
    
    def test_generate_command(self):
        """Test generating the merge script."""
        # First run import
        import_result = self._run_cli_command(
            "import",
            "--src", str(self.roms_dir),
            "--db", str(self.db_path)
        )
        self.assertEqual(import_result.returncode, 0)
        
        # Then generate
        result = self._run_cli_command(
            "generate",
            "--db", str(self.db_path),
            "--output", str(self.merge_script),
            "--target", str(self.target_dir)
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertTrue(self.merge_script.exists())
        
        # Verify script content contains expected games from comprehensive fixtures
        with open(self.merge_script) as f:
            content = f.read()
            # Check for games that should be in the script based on format priority
            self.assertIn("Galaga.crt", content)  # Should prefer .crt format
            self.assertIn("Ghostbusters.crt", content)  # Should prefer .crt over .d64/.tap
            self.assertIn("Pitfall.crt", content)  # Should prefer .crt over .d64/.tap
            self.assertIn("Bard's Tale (Disk 1).d64", content)  # Multi-part game
    
    def test_merge_command(self):
        """Test merging files to target directory."""
        # First generate the merge script
        import_result = self._run_cli_command(
            "import",
            "--src", str(self.roms_dir),
            "--db", str(self.db_path)
        )
        self.assertEqual(import_result.returncode, 0)
        
        generate_result = self._run_cli_command(
            "generate",
            "--db", str(self.db_path),
            "--output", str(self.merge_script),
            "--target", str(self.target_dir)
        )
        self.assertEqual(generate_result.returncode, 0)
        
        # Then run merge
        result = self._run_cli_command(
            "merge",
            "--target", str(self.target_dir),
            "--script", str(self.merge_script)
        )
        
        self.assertEqual(result.returncode, 0)
        
        # Verify the expected files exist in target based on comprehensive fixtures
        expected_files = [
            "Galaga.crt",
            "Ghostbusters.crt",
            "Pitfall.crt",
            "Bard's Tale/Bard's Tale (Disk 1).d64",
            "Bard's Tale/Bard's Tale (Disk 2).d64",
            "Bard's Tale.m3u"  # .m3u playlists are in root directory
        ]
        
        for file in expected_files:
            path = self.target_dir / file
            self.assertTrue(
                path.exists(),
                f"Expected file {file} not found in target directory"
            )
    
    def test_full_workflow(self):
        """Test the complete workflow from import to merge."""
        # First, import the ROMs
        import_result = self._run_cli_command(
            "import",
            "--src", str(self.roms_dir),
            "--db", str(self.db_path)
        )
        self.assertEqual(import_result.returncode, 0)
        
        # Generate merge script
        generate_result = self._run_cli_command(
            "generate",
            "--db", str(self.db_path),
            "--output", str(self.merge_script),
            "--target", str(self.target_dir)
        )
        self.assertEqual(generate_result.returncode, 0)
        
        # Run merge
        merge_result = self._run_cli_command(
            "merge",
            "--target", str(self.target_dir),
            "--script", str(self.merge_script)
        )
        self.assertEqual(merge_result.returncode, 0)
        
        # Verify final state
        self.assertTrue(self.db_path.exists())
        self.assertTrue(self.merge_script.exists())
        
        # List all files in target directory and subdirectories
        target_files = list(self.target_dir.glob("**/*"))
        self.assertGreaterEqual(len(target_files), 20)  # At least 20 files based on comprehensive fixtures
        
        # Convert paths to strings relative to target dir for easy comparison
        # Normalize paths to use forward slashes for cross-platform comparison
        target_paths = [
            str(f.relative_to(self.target_dir)).replace('\\', '/') 
            for f in target_files if f.is_file()
        ]
        
        # Verify priority rules were followed based on comprehensive fixtures
        self.assertIn("Galaga.crt", target_paths)  # Should use .crt format
        self.assertIn("Ghostbusters.crt", target_paths)  # Should use .crt over .d64/.tap
        self.assertIn("Pitfall.crt", target_paths)  # Should use .crt over .d64/.tap
        self.assertIn("Bard's Tale.m3u", target_paths)  # M3U playlist in root
        self.assertIn("Bard's Tale/Bard's Tale (Disk 1).d64", target_paths)
        self.assertIn("Bard's Tale/Bard's Tale (Disk 2).d64", target_paths)
    
    def test_full_workflow_format_priority(self):
        """Test that format priorities and collections are handled correctly."""
        # Run the full import/generate/merge workflow
        self._run_cli_command(
            "import",
            "--src", str(self.roms_dir),
            "--db", str(self.db_path)
        )
        
        self._run_cli_command(
            "generate",
            "--db", str(self.db_path),
            "--output", str(self.merge_script),
            "--target", str(self.target_dir)
        )
        
        self._run_cli_command(
            "merge",
            "--target", str(self.target_dir),
            "--script", str(self.merge_script)
        )
        
        # Verify format priorities based on comprehensive fixtures:
        # 1. .crt (cartridge) should be selected over .d64/.tap
        # 2. NoIntro collection should be preferred over TOSEC
        # 3. Europe/PAL regions should be preferred over USA/NTSC
        
        # Convert paths to strings relative to target dir for easy comparison
        target_paths = [
            str(f.relative_to(self.target_dir)).replace('\\', '/')  # Normalize path separators
            for f in self.target_dir.glob("**/*")
            if f.is_file()  # Only include files, not directories
        ]
        
        # Verify format priorities
        self.assertIn("Galaga.crt", target_paths)  # Should use NoIntro .crt
        self.assertIn("Ghostbusters.crt", target_paths)  # Should use TOSEC .crt over .d64/.tap
        self.assertIn("Pitfall.crt", target_paths)  # Should use TOSEC .crt over .d64/.tap
        
        # Verify regional priorities (Europe should be preferred)
        self.assertIn("Donkey Kong.d64", target_paths)  # Should use Europe version from NoIntro
        self.assertIn("Bubble Bobble.d64", target_paths)  # Should use Europe version from TOSEC
        
        # Verify multi-part game handling (NoIntro version selected)
        self.assertIn("Bard's Tale.m3u", target_paths)  # Playlist should be created
        self.assertIn("Bard's Tale/Bard's Tale (Disk 1).d64", target_paths)  # NoIntro Europe version
        self.assertIn("Bard's Tale/Bard's Tale (Disk 2).d64", target_paths)  # NoIntro Europe version
        
        # Verify collection priority (NoIntro over TOSEC when both have same format)
        self.assertIn("Donkey Kong.d64", target_paths)  # Should use NoIntro version

if __name__ == "__main__":
    unittest.main()
