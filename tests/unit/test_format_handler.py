"""
Unit tests for the format handler utility.
"""
import unittest
from c64collector.utils.format_handler import (
    get_format_priority, 
    is_multi_part, 
    get_multi_part_info
)


class TestFormatHandler(unittest.TestCase):
    
    def test_get_format_priority(self):
        # Test format priorities with common extensions
        self.assertEqual(get_format_priority("game.crt"), 3)  # Cartridge
        self.assertEqual(get_format_priority("game.d64"), 2)  # Disk image
        self.assertEqual(get_format_priority("game.g64"), 2)  # Disk image
        self.assertEqual(get_format_priority("game.nib"), 2)  # Disk image
        self.assertEqual(get_format_priority("game.tap"), 1)  # Tape
        self.assertEqual(get_format_priority("game.t64"), 1)  # Tape
        
        # Test with real-world file variations
        self.assertEqual(get_format_priority("100% Dynamite (USA, Europe) (Compilation) (Side 1).nib"), 2)
        self.assertEqual(get_format_priority("Game (Europe) (Re-release).tap"), 1)
        self.assertEqual(get_format_priority("Game.unknown"), 0)  # Unknown format
        
    def test_is_multi_part(self):
        # Basic multi-part patterns
        self.assertTrue(is_multi_part("", "Game (Disk 1).crt"))
        self.assertTrue(is_multi_part("", "Game (Side 2).d64"))
        self.assertTrue(is_multi_part("", "Game (Part 3).tap"))
        
        # Real-world examples from No-Intro collection
        self.assertTrue(is_multi_part("", "100% Dynamite (USA, Europe) (Compilation) (Side 1).nib"))
        self.assertTrue(is_multi_part("", "10 Top Classics (USA, Europe) (Compilation) (Side 3).nib"))
        self.assertTrue(is_multi_part("", "Ace 2088 (Europe) (Side A).tap"))
        self.assertTrue(is_multi_part("", "Ace 2088 (Europe) (Side B).tap"))
        
        # Real-world examples from OneLoad64 collection
        self.assertTrue(is_multi_part("", "Agent X II (Part 1) (J1).crt"))
        self.assertTrue(is_multi_part("", "Bugsy - Part 1.crt"))
        self.assertTrue(is_multi_part("", "Bugsy - Part 2 - The Crimelord.crt"))
        self.assertTrue(is_multi_part("", "Army Moves (Side 1).crt"))
        self.assertTrue(is_multi_part("", "Deliverance - Stormlord II (Levels 1 and 2) (J1).crt"))
        
        # Path-based detection
        self.assertTrue(is_multi_part("path/to/Disk 1/", "Game.crt"))
        self.assertTrue(is_multi_part("Game/Side A/", "file.tap"))
        
        # Non-multi-part cases
        self.assertFalse(is_multi_part("", "Game.crt"))
        self.assertFalse(is_multi_part("", "Game (Special Edition).d64"))
        self.assertFalse(is_multi_part("", "Game (v2).tap"))
        self.assertFalse(is_multi_part("", "10th Frame (USA) (Tape Port Dongle).nib"))
        self.assertFalse(is_multi_part("", "Game (Europe) (Re-release).nib"))
        self.assertFalse(is_multi_part("", "Another World Savedisk (Double Density - 1990).d64"))
        self.assertFalse(is_multi_part("", "Lords of Doom EF-Savedisk.d64"))
        
    def test_get_multi_part_info(self):
        # Basic part number detection
        self.assertEqual(get_multi_part_info("", "Game (Disk 1).crt"), 1)
        self.assertEqual(get_multi_part_info("", "Game (Side 2).d64"), 2)
        self.assertEqual(get_multi_part_info("", "Game (Part 3).tap"), 3)
        
        # No-Intro collection examples
        self.assertEqual(
            get_multi_part_info("", "100% Dynamite (USA, Europe) (Compilation) (Side 1).nib"), 1)
        self.assertEqual(
            get_multi_part_info("", "100% Dynamite (USA, Europe) (Compilation) (Side 5).nib"), 5)
        self.assertEqual(
            get_multi_part_info("", "10 Top Classics (USA, Europe) (Compilation) (Side 3).nib"), 3)
        
        # OneLoad64 collection examples
        self.assertEqual(get_multi_part_info("", "Agent X II (Part 1) (J1).crt"), 1)
        self.assertEqual(get_multi_part_info("", "Agent X II (Part 2) (J1).crt"), 2)
        self.assertEqual(get_multi_part_info("", "Bugsy - Part 1.crt"), 1)
        self.assertEqual(get_multi_part_info("", "Bugsy - Part 2 - The Crimelord.crt"), 2)
        self.assertEqual(get_multi_part_info("", "Army Moves (Side 1).crt"), 1)
        self.assertEqual(get_multi_part_info("", "Army Moves (Side 2).crt"), 2)
        self.assertEqual(
            get_multi_part_info("", "Deliverance - Stormlord II (Levels 1 and 2) (J1).crt"), 1)
        self.assertEqual(
            get_multi_part_info("", "Deliverance - Stormlord II (Levels 3 and 4) (J1).crt"), 2)
        
        # Side A/B format (should convert to numbers)
        self.assertEqual(get_multi_part_info("", "Game (Side A).tap"), 1)
        self.assertEqual(get_multi_part_info("", "Game (Side B).tap"), 2)
        self.assertEqual(get_multi_part_info("", "Ace 2088 (Europe) (Side A).tap"), 1)
        self.assertEqual(get_multi_part_info("", "Ace 2088 (Europe) (Side B).tap"), 2)
        
        # Path-based part numbers
        self.assertEqual(get_multi_part_info("path/to/Disk 4/", "Game.crt"), 4)
        self.assertEqual(get_multi_part_info("Game/Side A/", "file.tap"), 1)
        self.assertEqual(get_multi_part_info("Game/Side B/", "file.tap"), 2)
        
        # Cases that should not have part numbers
        self.assertEqual(get_multi_part_info("", "Game.crt"), 0)
        self.assertEqual(get_multi_part_info("", "Game (Special Edition).d64"), 0)
        self.assertEqual(get_multi_part_info("", "Game (v2).tap"), 0)
        self.assertEqual(get_multi_part_info("", "10th Frame (USA) (Tape Port Dongle).nib"), 0)
        self.assertEqual(get_multi_part_info("", "Game (Europe) (Re-release).nib"), 0)
        self.assertEqual(
            get_multi_part_info("", "Another World Savedisk (Double Density - 1990).d64"), 0)
        self.assertEqual(
            get_multi_part_info("", "Lords of Doom EF-Savedisk.d64"), 0)
        
    def test_complex_directory_structures(self):
        # Test handling nested paths with region/version info
        base_path = "src/No-Intro/100% Dynamite (USA, Europe) (Compilation)/"
        filename = "100% Dynamite (USA, Europe) (Compilation) (Side 1).nib"
        self.assertTrue(is_multi_part(base_path, filename))
        self.assertEqual(get_multi_part_info(base_path, filename), 1)
        
        # Test paths with special characters and version markers
        base_path = "src/OneLoad64-Games-Collection-v3/Agent X II/"
        filename = "Agent X II (Part 1) (J1).crt"
        self.assertTrue(is_multi_part(base_path, filename))
        self.assertEqual(get_multi_part_info(base_path, filename), 1)
        
        # Test paths with dashes and descriptive part names
        base_path = "src/OneLoad64-Games-Collection-v3/"
        filename = "Bugsy - Part 2 - The Crimelord.crt"
        self.assertTrue(is_multi_part(base_path, filename))
        self.assertEqual(get_multi_part_info(base_path, filename), 2)
        
        # Test level-based parts
        base_path = "src/OneLoad64-Games-Collection-v3/"
        filename = "Deliverance - Stormlord II (Levels 1 and 2) (J1).crt"
        self.assertTrue(is_multi_part(base_path, filename))
        self.assertEqual(get_multi_part_info(base_path, filename), 1)


if __name__ == '__main__':
    unittest.main()
