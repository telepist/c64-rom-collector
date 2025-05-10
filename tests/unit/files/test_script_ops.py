"""Tests for script generation operations."""
import io
import os
import unittest

from src.files.script_ops import (
    prepare_path_for_script,
    write_copy_command,
    write_m3u_playlist
)

class TestScriptOps(unittest.TestCase):
    """Test suite for script generation operations."""
    
    def test_prepare_path_for_script_source(self):
        """Test preparing a source path for a script."""
        test_path = r'D:\games\c64\My Game (USA).crt'
        result = prepare_path_for_script(test_path, is_source=True)
        # Source paths should only be normalized, not sanitized
        self.assertEqual(result, 'D:/games/c64/My Game (USA).crt')
        
    def test_prepare_path_for_script_target(self):
        """Test preparing a target path for a script."""
        test_path = r'target\My Game (USA).crt'
        result = prepare_path_for_script(test_path, is_source=False)
        # Target paths should be normalized and sanitized
        self.assertEqual(result, 'target/My_Game_USA.crt')
        
    def test_write_copy_command(self):
        """Test writing a copy command to a shell script."""
        output = io.StringIO()
        write_copy_command(
            output,
            source_path='source/game.crt',
            target_path='target/game.crt',
            target_name='game.crt'
        )
        result = output.getvalue()
        
        # Check command format
        self.assertIn('echo "Copying game.crt"', result)
        self.assertIn('cp "source/game.crt" "target/game.crt"', result)
        self.assertIn('|| echo "Failed to copy game.crt"', result)
        
    def test_write_copy_command_sanitizes_display(self):
        """Test that copy command sanitizes display names."""
        output = io.StringIO()
        write_copy_command(
            output,
            source_path='source/My\\Game.crt',
            target_path='target/My_Game.crt',
            target_name='My\\Game.crt'
        )
        result = output.getvalue()
        
        # Check display name is cleaned
        self.assertIn('echo "Copying My/Game.crt"', result)
        
    def test_write_m3u_playlist(self):
        """Test writing an M3U playlist to a shell script."""
        output = io.StringIO()
        disk_files = [
            ('Game/Game (Disk 1).d64', 'Disk 1'),
            ('Game/Game (Disk 2).d64', 'Disk 2')
        ]
        
        write_m3u_playlist(output, 'target/Game.m3u', disk_files)
        result = output.getvalue()
        
        # Check playlist format
        self.assertIn('cat > "target/Game.m3u" << EOL', result)
        self.assertIn('Game/Game (Disk 1).d64|Disk 1', result)
        self.assertIn('Game/Game (Disk 2).d64|Disk 2', result)
        self.assertIn('EOL', result)
