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
            self.db_path.unlink()

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
        
        # Check game count
        cursor.execute("SELECT COUNT(*) FROM games")
        game_count = cursor.fetchone()[0]
        self.assertEqual(game_count, 4)  # 3 single games + 1 multi-part game
        
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
        
        # Verify script content
        with open(self.merge_script) as f:
            content = f.read()
            self.assertIn("Game1.crt", content)  # Should prefer .crt over .d64
            self.assertIn("Game2.d64", content)  # Should prefer .d64 over .tap
            self.assertIn("Game3.crt", content)  # Single format
            self.assertIn("MultiGame (Disk 1).d64", content)  # Multi-part
    
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
        
        self.assertEqual(result.returncode, 0)        # Verify the expected files exist in target
        expected_files = [
            "Game1.crt",
            "Game2.d64",
            "Game3.crt",
            "MultiGame/MultiGame (Disk 1).d64",
            "MultiGame/MultiGame (Disk 2).d64",
            "MultiGame/MultiGame (Disk 3).d64",
            "MultiGame.m3u"  # .m3u playlists are in root directory
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
        self.assertGreaterEqual(len(target_files), 6)  # At least 6 files plus directory
        
        # Convert paths to strings relative to target dir for easy comparison
        # Normalize paths to use forward slashes for cross-platform comparison
        target_paths = [
            str(f.relative_to(self.target_dir)).replace('\\', '/') 
            for f in target_files if f.is_file()
        ]
        
        # Verify priority rules were followed
        self.assertIn("Game1.crt", target_paths)  # Should use .crt over .d64
        self.assertIn("Game2.d64", target_paths)  # Should use .d64 over .tap
        self.assertIn("Game3.crt", target_paths)
        self.assertIn("MultiGame.m3u", target_paths)  # M3U playlist in root
        self.assertIn("MultiGame/MultiGame (Disk 1).d64", target_paths)
        self.assertIn("MultiGame/MultiGame (Disk 2).d64", target_paths)
        self.assertIn("MultiGame/MultiGame (Disk 3).d64", target_paths)
    
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
        
        # Verify format priorities:
        # 1. .crt (cartridge) from NoIntro should be selected over .d64 from TOSEC (Game1)
        # 2. .d64 (disk) from NoIntro should be selected over .tap from TOSEC (Game2)
        # 3. NoIntro version of multi-part game should be selected over TOSEC version
        
        # Convert paths to strings relative to target dir for easy comparison
        target_paths = [
            str(f.relative_to(self.target_dir)).replace('\\', '/')  # Normalize path separators
            for f in self.target_dir.glob("**/*")
            if f.is_file()  # Only include files, not directories
        ]
        
        # Verify single file format priorities
        self.assertIn("Game1.crt", target_paths)  # Should use NoIntro .crt over TOSEC .d64
        self.assertNotIn("Game1.d64", target_paths)  # Lower priority format should not be used
        
        self.assertIn("Game2.d64", target_paths)  # Should use NoIntro .d64 over TOSEC .tap
        self.assertNotIn("Game2.tap", target_paths)  # Lower priority format should not be used
        
        self.assertIn("Game3.crt", target_paths)  # Only exists in one format
        
        # Verify multi-part game handling (NoIntro version selected over TOSEC version)
        self.assertIn("MultiGame.m3u", target_paths)  # Playlist should be created
        self.assertIn("MultiGame/MultiGame (Disk 1).d64", target_paths)  # NoIntro version
        self.assertIn("MultiGame/MultiGame (Disk 2).d64", target_paths)  # NoIntro version
        self.assertIn("MultiGame/MultiGame (Disk 3).d64", target_paths)  # NoIntro version
        
        # TOSEC variants should not be used
        self.assertNotIn("MultiGame/MultiGame (Disk 1 PAL NTSC).d64", target_paths)
        self.assertNotIn("MultiGame/MultiGame (Disk 2 PAL NTSC).d64", target_paths)
        self.assertNotIn("MultiGame/MultiGame (Disk 3 PAL NTSC).d64", target_paths)

if __name__ == "__main__":
    unittest.main()
