"""
Integration test for regional prioritization functionality.
"""
import unittest
import tempfile
import shutil
from pathlib import Path
import os
from core.importer import import_games
from core.merger import generate_merge_script
from files.operations import read_file
from db.database import DatabaseManager
from db.game_repository import GameRepository
from config import DATABASE_PATH, MERGE_SCRIPT_PATH, TARGET_DIR


class TestRegionalPrioritization(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment with regional variant files."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.roms_dir = self.temp_dir / "roms"
        self.build_dir = self.temp_dir / "build"
        self.target_dir = self.temp_dir / "target"
        
        # Create directory structure
        self.roms_dir.mkdir()
        self.build_dir.mkdir()
        self.target_dir.mkdir()
        
        # Create test collections
        tosec_dir = self.roms_dir / "TOSEC"
        tosec_dir.mkdir()
        
        # Create regional variant files
        (tosec_dir / "Game 4 (Europe).d64").write_text("Europe content")
        (tosec_dir / "Game 4 (USA).d64").write_text("USA content")
        (tosec_dir / "Game 4 (World).d64").write_text("World content")
        
        # Create non-regional file
        (tosec_dir / "Game 5.d64").write_text("No region content")
        
        # Create multi-disk game that should NOT be affected by regional extraction
        (tosec_dir / "MultiGame (Disk 1 PAL NTSC).d64").write_text("Multi disk 1 content")
        (tosec_dir / "MultiGame (Disk 2 PAL NTSC).d64").write_text("Multi disk 2 content")
        
        # Set up database and script paths
        self.db_path = self.build_dir / "test.db"
        self.script_path = self.build_dir / "test_script.sh"
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_regional_prioritization_workflow(self):
        """Test that regional prioritization works correctly in the full workflow."""
        # Import games
        stats = import_games(str(self.roms_dir), str(self.db_path))
        
        # Verify we have the expected number of games
        self.assertEqual(stats['unique_games'], 3)  # Game 4, Game 5, MultiGame
        self.assertEqual(stats['processed_files'], 6)  # 3 Game 4 variants + 1 Game 5 + 2 MultiGame disks
        
        # Generate merge script
        file_count = generate_merge_script(str(self.db_path), str(self.script_path), str(self.target_dir))
        
        # Expected files: 1 Game 4 (World selected), 1 Game 5, 2 MultiGame disks = 4 files
        # The M3U playlist is not counted in the file_count return value
        self.assertEqual(file_count, 4)
        
        # Execute the script to create target files
        self._execute_script(str(self.script_path))
        
        # Verify the correct regional variant was selected
        target_files = list(self.target_dir.glob("*"))
        target_file_names = [f.name for f in target_files]
        
        # Should have Game 4.d64 (Europe version), Game 5.d64, MultiGame.m3u, and MultiGame/ folder
        self.assertIn("Game 4.d64", target_file_names)
        self.assertIn("Game 5.d64", target_file_names)
        self.assertIn("MultiGame.m3u", target_file_names)
        self.assertIn("MultiGame", target_file_names)
        
        # Verify the content of Game 4.d64 is from the Europe version (highest priority)
        game4_content = read_file(str(self.target_dir / "Game 4.d64"))
        self.assertEqual(game4_content.strip(), b"Europe content")
        
        # Verify MultiGame folder contains the correct files
        multgame_dir = self.target_dir / "MultiGame"
        self.assertTrue(multgame_dir.is_dir())
        multgame_files = list(multgame_dir.glob("*"))
        self.assertEqual(len(multgame_files), 2)  # Should have 2 disk files
        
        # Verify MultiGame.m3u playlist exists
        m3u_file = self.target_dir / "MultiGame.m3u"
        self.assertTrue(m3u_file.exists())
        m3u_content = read_file(str(m3u_file))
        self.assertIn(b"MultiGame/MultiGame (Disk 1).d64|Disk 1", m3u_content)
        self.assertIn(b"MultiGame/MultiGame (Disk 2).d64|Disk 2", m3u_content)
    
    def test_regional_priority_order(self):
        """Test that regional priorities are correctly ordered."""
        # Import games
        import_games(str(self.roms_dir), str(self.db_path))
        
        # Check database content directly
        db = DatabaseManager(str(self.db_path))
        db.connect()
        
        # Get Game 4 versions ordered by priority
        db.execute('''
            SELECT v.region, v.region_priority 
            FROM games g 
            JOIN game_versions v ON g.id = v.game_id 
            WHERE g.clean_name = "Game 4" 
            ORDER BY v.region_priority DESC
        ''')
        versions = db.fetchall()
        
        # Should have 3 versions: Europe (6), PAL (5), World (4), USA (3)
        self.assertEqual(len(versions), 3)
        self.assertEqual(versions[0][0], "Europe")
        self.assertEqual(versions[0][1], 6)
        self.assertEqual(versions[1][0], "World")
        self.assertEqual(versions[1][1], 4)
        self.assertEqual(versions[2][0], "USA")
        self.assertEqual(versions[2][1], 3)
        
        db.close()
    
    def test_format_priority_over_regional_priority(self):
        """Test that format priority takes precedence over regional priority."""
        # Create additional test files to test format vs region priority
        tosec_dir = self.roms_dir / "TOSEC"
        
        # Create a US disk version and EU tape version of the same game
        (tosec_dir / "Game 6 (USA).d64").write_text("USA disk content")
        (tosec_dir / "Game 6 (Europe).tap").write_text("Europe tape content")
        
        # Import games
        import_games(str(self.roms_dir), str(self.db_path))
        
        # Check database content directly
        db = DatabaseManager(str(self.db_path))
        db.connect()
        
        # Get Game 6 versions ordered by priority (format first, then region)
        db.execute('''
            SELECT v.region, v.region_priority, v.format, v.format_priority
            FROM games g 
            JOIN game_versions v ON g.id = v.game_id 
            WHERE g.clean_name = "Game 6" 
            ORDER BY v.format_priority DESC, v.region_priority DESC
        ''')
        versions = db.fetchall()
        
        # Should have 2 versions: USA d64 should be first (format priority wins)
        self.assertEqual(len(versions), 2)
        self.assertEqual(versions[0][0], "USA")  # region
        self.assertEqual(versions[0][1], 3)      # region_priority
        self.assertEqual(versions[0][2], "d64")  # format
        self.assertEqual(versions[0][3], 2)      # format_priority
        
        self.assertEqual(versions[1][0], "Europe")  # region
        self.assertEqual(versions[1][1], 6)         # region_priority
        self.assertEqual(versions[1][2], "tap")     # format
        self.assertEqual(versions[1][3], 1)         # format_priority
        
        db.close()
        
        # Test that the USA disk version is selected in the merge script
        file_count = generate_merge_script(str(self.db_path), str(self.script_path), str(self.target_dir))
        self._execute_script(str(self.script_path))
        
        # Verify the USA disk version was selected over the Europe tape version
        game6_content = read_file(str(self.target_dir / "Game 6.d64"))
        self.assertEqual(game6_content.strip(), b"USA disk content")
    
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
                    f.write('\n'.join(content_lines))


if __name__ == '__main__':
    unittest.main()
