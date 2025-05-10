"""
Tests for the path sanitizer utilities.
"""
import unittest
from src.utils.path_sanitizer import sanitize_directory_name, sanitize_full_path

class TestPathSanitizer(unittest.TestCase):
    
    def test_sanitize_directory_name(self):
        # Test removal of trailing dots and spaces
        self.assertEqual(sanitize_directory_name("Game."), "Game")
        self.assertEqual(sanitize_directory_name("Game.."), "Game")
        self.assertEqual(sanitize_directory_name("Game "), "Game")
        self.assertEqual(sanitize_directory_name(" Game "), "Game")
        self.assertEqual(sanitize_directory_name("Chase H.Q."), "Chase H.Q")
        self.assertEqual(sanitize_directory_name("S.C.I."), "S.C.I")
        self.assertEqual(sanitize_directory_name("F.I.S.T."), "F.I.S.T")
        self.assertEqual(sanitize_directory_name("R.B.I. Baseball"), "R.B.I. Baseball")
        
        # Test replacement of problematic characters        
        self.assertEqual(sanitize_directory_name("Game<1>"), "Game_1")
        self.assertEqual(sanitize_directory_name("Game:Part"), "Game_Part")
        self.assertEqual(sanitize_directory_name('Game|2'), "Game_2")
        self.assertEqual(sanitize_directory_name('Game?'), "Game")
        self.assertEqual(sanitize_directory_name('Game*'), "Game")
        self.assertEqual(sanitize_directory_name('Game\\Part2'), "Game_Part2")
        self.assertEqual(sanitize_directory_name('Game/Part2'), "Game_Part2")
        
        # Test multiple spaces and underscores
        self.assertEqual(sanitize_directory_name("Game  Name"), "Game Name")
        self.assertEqual(sanitize_directory_name("Game__Name"), "Game_Name")
        self.assertEqual(sanitize_directory_name("Game _ Name"), "Game _ Name")
        
        # Test edge cases
        self.assertEqual(sanitize_directory_name("..."), "unnamed")
        self.assertEqual(sanitize_directory_name(""), "unnamed")
        self.assertEqual(sanitize_directory_name("   "), "unnamed")
        
    def test_sanitize_full_path(self):
        # Test simple paths
        self.assertEqual(
            sanitize_full_path("target/Game."),
            "target/Game"
        )
        
        # Test nested paths
        self.assertEqual(
            sanitize_full_path("target/Game./Part."),
            "target/Game/Part"
        )
        
        # Test absolute paths
        self.assertEqual(
            sanitize_full_path("/target/Game./Part."),
            "/target/Game/Part"
        )
        
        # Test complex paths with multiple issues       
        self.assertEqual(
            sanitize_full_path("target/Game?<1>/Part:2./Final*"),
            "target/Game_1/Part_2/Final"
        )
        
if __name__ == '__main__':
    unittest.main()
