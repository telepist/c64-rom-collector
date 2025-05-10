"""Tests for path sanitization operations."""
import unittest

from src.files.path_sanitizer import (
    sanitize_directory_name,
    sanitize_full_path
)

class TestPathSanitizer(unittest.TestCase):
    """Test suite for path sanitization functions."""
    
    def test_sanitize_directory_name_basic(self):
        """Test basic directory name sanitization."""
        test_cases = {
            "Simple Name": "Simple_Name",
            "Game (USA)": "Game_USA",
            "My<>Game": "My_Game",
            "Bad:Chars?*|": "Bad_Chars",
            "Multiple   Spaces": "Multiple_Spaces",
        }
        
        for input_name, expected in test_cases.items():
            with self.subTest(input_name=input_name):
                result = sanitize_directory_name(input_name)
                self.assertEqual(result, expected)

    def test_sanitize_directory_name_empty(self):
        """Test sanitizing empty or dot-only names."""
        test_cases = {
            "": "unnamed",
            ".": "unnamed",
            "...": "unnamed",
            " . . ": "unnamed",
        }
        
        for input_name, expected in test_cases.items():
            with self.subTest(input_name=input_name):
                result = sanitize_directory_name(input_name)
                self.assertEqual(result, expected)

    def test_sanitize_directory_name_trims(self):
        """Test that sanitization trims extra characters."""
        test_cases = {
            "...My Game...": "My_Game",
            "  Spaces  ": "Spaces",
            "___Game___": "Game",
            ". . Game . .": "Game",
        }
        
        for input_name, expected in test_cases.items():
            with self.subTest(input_name=input_name):
                result = sanitize_directory_name(input_name)
                self.assertEqual(result, expected)

    def test_sanitize_full_path(self):
        """Test sanitizing a full path."""
        test_cases = {
            "games/My Game/File.crt": "games/My_Game/File.crt",
            "/root/Bad:Name/Game?*.crt": "/root/Bad_Name/Game.crt",
            "C:/Games/Multi   Space/File.crt": "C:/Games/Multi_Space/File.crt",
            "A/B/C/../File.crt": "A/B/C/File.crt",
        }
        
        for input_path, expected in test_cases.items():
            with self.subTest(input_path=input_path):
                result = sanitize_full_path(input_path)
                self.assertEqual(result, expected)

    def test_sanitize_full_path_preserves_root(self):
        """Test that sanitization preserves root components."""
        test_cases = {
            "/My Game": "/My_Game",
            "C:/Bad:Name": "C:/Bad_Name",
            "//server/share/File Name": "//server/share/File_Name",
        }
        
        for input_path, expected in test_cases.items():
            with self.subTest(input_path=input_path):
                result = sanitize_full_path(input_path)
                self.assertEqual(result, expected)
