"""
Unit tests for the processor module.
"""
import unittest
from unittest import mock
import os
from core.processor import process_file, scan_directory


class TestProcessor(unittest.TestCase):
    
    def test_process_file(self):
        # Test processing a single file
        file_path = "path/to/Game (Europe) (v1.2).crt"
        collection = "Collection1"
        
        result = process_file(file_path, collection)
        
        self.assertEqual(result['source_path'], file_path)
        self.assertEqual(result['original_name'], "Game (Europe) (v1.2).crt")
        self.assertEqual(result['clean_name'], "Game")
        self.assertEqual(result['format'], "crt")
        self.assertEqual(result['collection'], "Collection1")
        self.assertEqual(result['format_priority'], 3)
        self.assertEqual(result['is_multi_part'], 0)
        self.assertEqual(result['part_number'], 0)
        
    def test_process_multi_part_file(self):
        # Test processing a multi-part file
        file_path = "path/to/Game (Europe) (Disk 2).d64"
        collection = "Collection1"
        
        result = process_file(file_path, collection)
        
        self.assertEqual(result['clean_name'], "Game")
        self.assertEqual(result['format'], "d64")
        self.assertEqual(result['format_priority'], 2)
        self.assertEqual(result['is_multi_part'], 1)
        self.assertEqual(result['part_number'], 2)
        
    def test_process_empty_name(self):
        # Test with a file that results in an empty clean name
        # This could happen with files named only with markers, like "(Europe).crt"
        file_path = "path/to/(Europe).crt"
        collection = "Collection1"
        
        result = process_file(file_path, collection)
        
        self.assertIsNone(result)
        
    @mock.patch('os.walk')
    @mock.patch('core.processor.process_file')
    @mock.patch('core.processor.should_skip_file')
    def test_scan_directory(self, mock_should_skip, mock_process_file, mock_walk):
        # Mock os.walk to return some test files
        mock_walk.return_value = [
            ('/base/dir', ['subdir'], ['game1.crt', 'game2.d64', 'utility.tap', 'bad.bin']),
            ('/base/dir/subdir', [], ['game3.tap', 'bios.crt'])
        ]
        
        # Mock should_skip_file to skip utility.tap and bios.crt
        def mock_skip(path, filename):
            return filename in ['utility.tap', 'bios.crt', 'bad.bin']
        mock_should_skip.side_effect = mock_skip
        
        # Mock process_file to return test data for valid files
        def mock_process(file_path, collection):
            filename = os.path.basename(file_path)
            if filename == 'game1.crt':
                return {'clean_name': 'Game1', 'format': 'crt', 'is_multi_part': 0}
            elif filename == 'game2.d64':
                return {'clean_name': 'Game2', 'format': 'd64', 'is_multi_part': 0}
            elif filename == 'game3.tap':
                return {'clean_name': 'Game3', 'format': 'tap', 'is_multi_part': 1}
            return None
        mock_process_file.side_effect = mock_process
        
        # Call the function
        result, skipped, errors = scan_directory('/base/dir', 'TestCollection')
        
        # Check results
        self.assertEqual(len(result), 3)  # 3 valid games processed
        self.assertEqual(skipped, 3)  # 3 files skipped
        self.assertEqual(errors, 0)  # No errors


if __name__ == '__main__':
    unittest.main()
