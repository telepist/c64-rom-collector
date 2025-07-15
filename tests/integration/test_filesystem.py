"""Comprehensive integration test using real filesystem fixtures."""
import unittest
import tempfile
import shutil
from pathlib import Path
from core.importer import import_games
from core.merger import generate_merge_script
from files.operations import read_file
from db.database import DatabaseManager
from .fixtures.fixture_creator import get_expected_results


class TestFilesystemIntegration(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment with real filesystem fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.build_dir = self.temp_dir / "build"
        self.target_dir = self.temp_dir / "target"
        
        # Create directory structure
        self.build_dir.mkdir()
        self.target_dir.mkdir()
        
        # Copy real fixtures from the fixtures directory
        fixtures_dir = Path(__file__).parent / "fixtures" / "roms"
        self.roms_dir = self.temp_dir / "roms"
        shutil.copytree(fixtures_dir, self.roms_dir)
        
        # Set up database and script paths
        self.db_path = self.build_dir / "test.db"
        self.script_path = self.build_dir / "test_script.sh"
        
        # Get expected results
        self.expected = get_expected_results()
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_filesystem_regional_prioritization(self):
        """Test regional prioritization using real filesystem fixtures."""
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
            
            print(f"[OK] {game_name}: {expected_region} region selected")
    
    def test_filesystem_format_priority(self):
        """Test format priority using real filesystem fixtures."""
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
            
            print(f"[OK] {game_name}: {expected_format} format selected")
    
    def test_filesystem_multidisk_games(self):
        """Test multi-disk game handling using real filesystem fixtures."""
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
            
            # Verify content of first disk file (just check it's not empty)
            first_disk = disk_files[0]
            content = read_file(str(first_disk))
            self.assertGreater(len(content), 0, f"Empty content in first disk of {game_name}")
            # Content should contain the game name or disk info
            content_str = content.decode()
            self.assertTrue(any(word in content_str for word in [game_name.split()[0], "disk", "content"]),
                           f"Unexpected content in first disk of {game_name}: {content_str}")
            
            print(f"[OK] {game_name}: {game_info['parts']} parts with M3U playlist")
    
    def test_filesystem_collection_priority(self):
        """Test collection priority using real filesystem fixtures."""
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
            
            print(f"[OK] {game_name}: {expected_collection} collection selected")
    
    def test_filesystem_edge_cases(self):
        """Test edge cases using real filesystem fixtures."""
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
            
            print(f"[OK] {game_name}: edge case handled correctly")
    
    def test_filesystem_skipped_files(self):
        """Test that certain files are properly skipped using real filesystem fixtures."""
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
        
        # Verify skipped files are not in the database
        db = DatabaseManager(str(self.db_path))
        db.connect()
        
        try:
            for skipped_file in self.expected['skipped_files']:
                db.execute("SELECT COUNT(*) FROM game_parts WHERE source_path LIKE ?", 
                          (f"%{skipped_file}%",))
                count = db.fetchone()[0]
                self.assertEqual(count, 0, f"Skipped file {skipped_file} found in database")
        finally:
            db.close()
        print(f"[OK] {len(self.expected['skipped_files'])} file types properly skipped")
    
    def test_filesystem_comprehensive_stats(self):
        """Test that import statistics are accurate using real filesystem fixtures."""
        # Import games
        stats = import_games(str(self.roms_dir), str(self.db_path))
        
        # Verify statistics
        self.assertGreater(stats['processed_files'], 0, "No files were processed")
        self.assertGreater(stats['unique_games'], 0, "No unique games found")
        self.assertGreaterEqual(stats['processed_files'], stats['unique_games'], 
                              "Processed files should be >= unique games")
        
        # Print detailed stats
        print(f"\\nComprehensive Import Statistics:")
        print(f"  Processed files: {stats['processed_files']}")
        print(f"  Unique games: {stats['unique_games']}")
        print(f"  Skipped files: {stats.get('skipped_files', 0)}")
        
        # Verify we have the expected number of fixture files
        total_fixture_files = sum(len(list(Path(self.roms_dir / collection).glob("*"))) 
                                 for collection in ["NoIntro", "TOSEC", "OneLoad64"])
        print(f"  Total fixture files: {total_fixture_files}")
        
        # Count ROM files (excluding skipped files)
        rom_extensions = ['.d64', '.crt', '.tap', '.t64', '.g64', '.nib', '.prg']
        rom_files = []
        for collection in ["NoIntro", "TOSEC", "OneLoad64"]:
            collection_dir = Path(self.roms_dir / collection)
            for ext in rom_extensions:
                rom_files.extend(list(collection_dir.glob(f"*{ext}")))
        
        print(f"  ROM files found: {len(rom_files)}")
        print(f"  Skipped files: {total_fixture_files - len(rom_files)}")
    
    def test_filesystem_realistic_workflow(self):
        """Test the complete workflow using real filesystem fixtures."""
        # This test simulates the real-world usage pattern
        
        # Step 1: Import from filesystem
        print("\\n=== Step 1: Import Phase ===")
        stats = import_games(str(self.roms_dir), str(self.db_path))
        print(f"Imported {stats['processed_files']} files into {stats['unique_games']} games")
        
        # Step 2: Generate merge script
        print("\\n=== Step 2: Generate Phase ===")
        file_count = generate_merge_script(str(self.db_path), str(self.script_path), str(self.target_dir))
        print(f"Generated script to copy {file_count} files")
        
        # Step 3: Execute merge script
        print("\\n=== Step 3: Merge Phase ===")
        self._execute_script(str(self.script_path))
        
        # Step 4: Verify results
        print("\\n=== Step 4: Verification ===")
        target_files = list(self.target_dir.glob("*"))
        target_dirs = [f for f in target_files if f.is_dir()]
        target_files = [f for f in target_files if f.is_file()]
        
        print(f"Created {len(target_files)} files and {len(target_dirs)} directories")
        
        # Verify we have some multi-disk games
        m3u_files = list(self.target_dir.glob("*.m3u"))
        print(f"Created {len(m3u_files)} M3U playlists")
        
        # Verify directory structure
        for target_dir in target_dirs:
            disk_files = list(target_dir.glob("*"))
            print(f"  {target_dir.name}/: {len(disk_files)} disk files")
        
        # Basic sanity checks
        self.assertGreater(len(target_files), 0, "No files were created")
        self.assertGreater(len(target_dirs), 0, "No multi-disk games found")
        self.assertGreater(len(m3u_files), 0, "No M3U playlists created")
        
        print("\n[SUCCESS] Complete workflow test passed!")
    
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
