"""Comprehensive integration test using enhanced fixtures."""
import unittest
import tempfile
import shutil
from pathlib import Path
from core.importer import import_games
from core.merger import generate_merge_script
from files.operations import read_file
from .fixtures.fixture_creator import create_comprehensive_fixtures, get_expected_results


class TestComprehensiveIntegration(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment with comprehensive fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.roms_dir = self.temp_dir / "roms"
        self.build_dir = self.temp_dir / "build"
        self.target_dir = self.temp_dir / "target"
        
        # Create directory structure
        self.build_dir.mkdir()
        self.target_dir.mkdir()
        
        # Create comprehensive fixtures
        self.collection_dirs = create_comprehensive_fixtures(self.roms_dir)
        
        # Set up database and script paths
        self.db_path = self.build_dir / "test.db"
        self.script_path = self.build_dir / "test_script.sh"
        
        # Get expected results
        self.expected = get_expected_results()
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_regional_prioritization_comprehensive(self):
        """Test regional prioritization with comprehensive examples."""
        # Import games
        stats = import_games(str(self.roms_dir), str(self.db_path))
        
        # Generate merge script
        generate_merge_script(str(self.db_path), str(self.script_path), str(self.target_dir))
        self._execute_script(str(self.script_path))
        
        # Verify regional winners
        for game_name, (expected_region, expected_content) in self.expected['regional_winners'].items():
            # Find the target file (could be .d64, .crt, etc.)
            target_files = list(self.target_dir.glob(f"{game_name}.*"))
            self.assertEqual(len(target_files), 1, f"Expected exactly one file for {game_name}")
            
            target_file = target_files[0]
            content = read_file(str(target_file))
            self.assertEqual(content.strip(), expected_content.encode(), 
                           f"Wrong content for {game_name}")
    
    def test_format_priority_comprehensive(self):
        """Test format priority with comprehensive examples."""
        # Import games
        import_games(str(self.roms_dir), str(self.db_path))
        
        # Generate merge script
        generate_merge_script(str(self.db_path), str(self.script_path), str(self.target_dir))
        self._execute_script(str(self.script_path))
        
        # Verify format winners
        for game_name, (expected_format, expected_content) in self.expected['format_winners'].items():
            target_files = list(self.target_dir.glob(f"{game_name}.*"))
            self.assertEqual(len(target_files), 1, f"Expected exactly one file for {game_name}")
            
            target_file = target_files[0]
            self.assertEqual(target_file.suffix[1:], expected_format, 
                           f"Wrong format selected for {game_name}")
            
            content = read_file(str(target_file))
            self.assertEqual(content.strip(), expected_content.encode(),
                           f"Wrong content for {game_name}")
    
    def test_multidisk_games_comprehensive(self):
        """Test multi-disk game handling with comprehensive examples."""
        # Import games
        import_games(str(self.roms_dir), str(self.db_path))
        
        # Generate merge script
        generate_merge_script(str(self.db_path), str(self.script_path), str(self.target_dir))
        self._execute_script(str(self.script_path))
        
        # Verify multi-disk games
        for game_name, game_info in self.expected['multidisk_games'].items():
            # Check that game directory exists
            game_dir = self.target_dir / game_name
            self.assertTrue(game_dir.exists(), f"Game directory {game_name} not found")
            self.assertTrue(game_dir.is_dir(), f"{game_name} should be a directory")
            
            # Check that M3U file exists
            m3u_file = self.target_dir / f"{game_name}.m3u"
            self.assertTrue(m3u_file.exists(), f"M3U file {game_name}.m3u not found")
            
            # Check M3U content
            m3u_content = read_file(str(m3u_file)).decode()
            for expected_line in game_info['m3u_content']:
                self.assertIn(expected_line, m3u_content,
                            f"M3U content missing line: {expected_line}")
            
            # Check that all disk files exist
            disk_files = list(game_dir.glob("*"))
            self.assertEqual(len(disk_files), game_info['parts'],
                           f"Wrong number of disk files for {game_name}")
            
            # Check individual disk files
            for expected_file in game_info['files']:
                disk_file = game_dir / Path(expected_file).name
                self.assertTrue(disk_file.exists(),
                              f"Disk file {expected_file} not found")
    
    def test_collection_priority_comprehensive(self):
        """Test collection priority with comprehensive examples."""
        # Import games
        import_games(str(self.roms_dir), str(self.db_path))
        
        # Generate merge script
        generate_merge_script(str(self.db_path), str(self.script_path), str(self.target_dir))
        self._execute_script(str(self.script_path))
        
        # Verify collection winners
        for game_name, (expected_collection, expected_content) in self.expected['collection_winners'].items():
            target_files = list(self.target_dir.glob(f"{game_name}.*"))
            self.assertEqual(len(target_files), 1, f"Expected exactly one file for {game_name}")
            
            target_file = target_files[0]
            content = read_file(str(target_file))
            self.assertEqual(content.strip(), expected_content.encode(),
                           f"Wrong collection selected for {game_name}")
    
    def test_edge_cases_comprehensive(self):
        """Test edge cases with comprehensive examples."""
        # Import games
        import_games(str(self.roms_dir), str(self.db_path))
        
        # Generate merge script
        generate_merge_script(str(self.db_path), str(self.script_path), str(self.target_dir))
        self._execute_script(str(self.script_path))
        
        # Verify edge cases
        for game_name, (expected_region, expected_content) in self.expected['edge_cases'].items():
            target_files = list(self.target_dir.glob(f"{game_name}.*"))
            self.assertEqual(len(target_files), 1, f"Expected exactly one file for {game_name}")
            
            target_file = target_files[0]
            content = read_file(str(target_file))
            self.assertEqual(content.strip(), expected_content.encode(),
                           f"Wrong content for edge case {game_name}")
    
    def test_skipped_files_comprehensive(self):
        """Test that certain files are properly skipped."""
        # Import games
        stats = import_games(str(self.roms_dir), str(self.db_path))
        
        # Generate merge script
        generate_merge_script(str(self.db_path), str(self.script_path), str(self.target_dir))
        self._execute_script(str(self.script_path))
        
        # Verify skipped files don't appear in target
        for skipped_file in self.expected['skipped_files']:
            target_files = list(self.target_dir.glob(f"*{skipped_file}*"))
            self.assertEqual(len(target_files), 0, 
                           f"Skipped file {skipped_file} found in target")
    
    def test_comprehensive_stats(self):
        """Test that import statistics are accurate."""
        # Import games
        stats = import_games(str(self.roms_dir), str(self.db_path))
        
        # Verify statistics
        self.assertGreater(stats['processed_files'], 0, "No files were processed")
        self.assertGreater(stats['unique_games'], 0, "No unique games found")
        self.assertGreaterEqual(stats['processed_files'], stats['unique_games'], 
                              "Processed files should be >= unique games")
        
        # Print stats for debugging
        print(f"\\nImport Statistics:")
        print(f"  Processed files: {stats['processed_files']}")
        print(f"  Unique games: {stats['unique_games']}")
        print(f"  Skipped files: {stats.get('skipped_files', 0)}")

    def test_alternative_versions_no_duplicate_m3u(self):
        """Test that alternative versions don't create duplicate M3U entries."""
        # Import games
        import_games(str(self.roms_dir), str(self.db_path))
        
        # Generate merge script
        generate_merge_script(str(self.db_path), str(self.script_path), str(self.target_dir))
        self._execute_script(str(self.script_path))
        
        # Look for any games with "Alt" in the fixtures
        alt_games = []
        for collection_dir in self.collection_dirs:
            collection_path = Path(collection_dir)
            for file_path in collection_path.rglob("*"):
                if file_path.is_file() and "(Alt)" in file_path.name:
                    import sys
                    import os
                    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
                    from utils.name_cleaner import clean_name
                    clean_game_name = clean_name(file_path.name)
                    alt_games.append(clean_game_name)
        
        # For each game that has an Alt version, verify no M3U file exists
        # (since they should be single-disk games)
        for game_name in alt_games:
            m3u_file = self.target_dir / f"{game_name}.m3u"
            self.assertFalse(m3u_file.exists(), 
                           f"M3U file {game_name}.m3u should not exist for single-disk game with Alt version")
            
            # Verify only one target file exists (the best version)
            target_files = list(self.target_dir.glob(f"{game_name}.*"))
            target_files = [f for f in target_files if not f.name.endswith('.m3u')]
            self.assertEqual(len(target_files), 1, 
                           f"Expected exactly one file for {game_name}, got {len(target_files)}")
            
            # Verify no subdirectory exists for single-disk games
            game_dir = self.target_dir / game_name
            self.assertFalse(game_dir.exists(), 
                           f"Directory {game_name} should not exist for single-disk game")
    
    def _execute_script(self, script_path):
        """Execute the generated script to create target files."""
        # Read the script and execute the copy commands
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        # Extract and execute copy commands
        for line in script_content.splitlines():
            if line.strip().startswith('cp '):
                # Parse: cp "source" "target"
                parts = line.split('"')
                if len(parts) >= 4:
                    source = parts[1]
                    target = parts[3]
                    
                    # Ensure target directory exists
                    target_path = Path(target)
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(source, target)
            elif line.strip().startswith('cat > '):
                # Handle M3U file creation
                target_match = line.split('"')[1]
                # Find the EOL block and create the file
                lines = script_content.splitlines()
                line_index = lines.index(line)
                content_lines = []
                for i in range(line_index + 1, len(lines)):
                    if lines[i].strip() == 'EOL':
                        break
                    content_lines.append(lines[i])
                
                # Write M3U file
                with open(target_match, 'w') as f:
                    f.write('\\n'.join(content_lines))


if __name__ == '__main__':
    unittest.main()
