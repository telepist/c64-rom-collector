"""
Unit tests for the name cleaner utility.
"""
import unittest
from c64collector.utils.name_cleaner import clean_name


class TestNameCleaner(unittest.TestCase):
    
    def test_clean_name_removes_region(self):
        # Test removing region markers
        self.assertEqual(clean_name("Game (USA).crt"), "Game")
        self.assertEqual(clean_name("Game (Europe).d64"), "Game")
        self.assertEqual(clean_name("Game (PAL).tap"), "Game")
        self.assertEqual(clean_name("Game (NTSC).nib"), "Game") 
        self.assertEqual(clean_name("Game [Europe].d64"), "Game")
        
    def test_clean_name_removes_version(self):
        # Test removing version information
        self.assertEqual(clean_name("Game v1.0.crt"), "Game")
        self.assertEqual(clean_name("Game [v2.0].d64"), "Game")
        self.assertEqual(clean_name("Game (Version 2).tap"), "Game")
        
    def test_clean_name_removes_common_suffixes(self):
        # Test removing common suffixes
        self.assertEqual(clean_name("Game (Budget).crt"), "Game")
        self.assertEqual(clean_name("Game (Alt).d64"), "Game")
        self.assertEqual(clean_name("Game (Alternative).tap"), "Game")
        self.assertEqual(clean_name("Game (Unl).nib"), "Game")
        self.assertEqual(clean_name("Game [Aftermarket].crt"), "Game")
        
    def test_clean_name_converts_roman_numerals(self):
        # Test converting Roman numerals
        self.assertEqual(clean_name("Game II.crt"), "Game 2")
        self.assertEqual(clean_name("Game III.d64"), "Game 3")
        self.assertEqual(clean_name("Game IV.tap"), "Game 4")
        self.assertEqual(clean_name("Game VI.nib"), "Game 6")
        self.assertEqual(clean_name("Game VII.crt"), "Game 7")
        self.assertEqual(clean_name("Game VIII.d64"), "Game 8")
        
    def test_clean_name_handles_multipart_games(self):
        # Test handling multipart game names
        self.assertEqual(clean_name("Game (Disk 1).crt"), "Game")
        self.assertEqual(clean_name("Game (Side 2).d64"), "Game")
        self.assertEqual(clean_name("Game [Part 3].tap"), "Game")
        
    def test_clean_name_complex_examples(self):
        # Test complex examples
        self.assertEqual(clean_name("Super Game 2000 (Europe) (v1.2) (Side 1).d64"), "Super Game 2000")
        self.assertEqual(clean_name("Ultimate_Game-II [USA] [v3.0] [Disk 2].crt"), "Ultimate_Game-2")
        self.assertEqual(clean_name("Amazing Game III (PAL) (Alt) [Part 3].tap"), "Amazing Game 3")
        
    def test_clean_name_preserves_inner_words(self):
        # Test that inner words with Roman numeral patterns are preserved
        self.assertEqual(clean_name("Winter Games.crt"), "Winter Games")
        self.assertEqual(clean_name("California Games.d64"), "California Games")


if __name__ == '__main__':
    unittest.main()
