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
        # Test format priorities
        self.assertEqual(get_format_priority("game.crt"), 3)  # Cartridge
        self.assertEqual(get_format_priority("game.d64"), 2)  # Disk image
        self.assertEqual(get_format_priority("game.g64"), 2)  # Disk image
        self.assertEqual(get_format_priority("game.nib"), 2)  # Disk image
        self.assertEqual(get_format_priority("game.tap"), 1)  # Tape
        self.assertEqual(get_format_priority("game.t64"), 1)  # Tape
        self.assertEqual(get_format_priority("game.unknown"), 0)  # Unknown format
        
    def test_is_multi_part(self):
        # Test multi-part detection
        self.assertTrue(is_multi_part("", "Game (Disk 1).crt"))
        self.assertTrue(is_multi_part("", "Game (Side 2).d64"))
        self.assertTrue(is_multi_part("", "Game (Part 3).tap"))
        self.assertTrue(is_multi_part("path/to/", "Game Disk 1.crt"))  # Path contains "Disk 1"
        self.assertFalse(is_multi_part("", "Game.crt"))
        self.assertFalse(is_multi_part("", "Game (Special Edition).d64"))
        
    def test_get_multi_part_info(self):
        # Test extracting part numbers
        self.assertEqual(get_multi_part_info("", "Game (Disk 1).crt"), 1)
        self.assertEqual(get_multi_part_info("", "Game (Side 2).d64"), 2)
        self.assertEqual(get_multi_part_info("", "Game (Part 3).tap"), 3)
        self.assertEqual(get_multi_part_info("path/to/Disk 4/", "Game.crt"), 4)
        self.assertEqual(get_multi_part_info("", "Game.crt"), 0)  # No part number
        self.assertEqual(get_multi_part_info("", "Game (Special Edition).d64"), 0)


if __name__ == '__main__':
    unittest.main()
