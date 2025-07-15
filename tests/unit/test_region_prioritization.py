"""
Unit tests for regional prioritization functionality.
"""
import unittest
from utils.name_cleaner import extract_region, get_region_priority


class TestRegionPrioritization(unittest.TestCase):
    
    def test_extract_region(self):
        """Test region extraction from game names."""
        # Test standard region extraction
        self.assertEqual(extract_region('Game 4 (USA).d64'), 'USA')
        self.assertEqual(extract_region('Game 4 (Europe).d64'), 'Europe')
        self.assertEqual(extract_region('Game 4 (World).d64'), 'World')
        self.assertEqual(extract_region('Game 4 (Japan).d64'), 'Japan')
        self.assertEqual(extract_region('Game 4 (PAL).d64'), 'PAL')
        self.assertEqual(extract_region('Game 4 (NTSC).d64'), 'NTSC')
        
        # Test multi-region
        self.assertEqual(extract_region('Game 4 (USA, Europe).d64'), 'USA, Europe')
        
        # Test no region
        self.assertEqual(extract_region('Game 4.d64'), '')
        
        # Test multi-part games should not extract regions
        self.assertEqual(extract_region('MultiGame (Disk 1 PAL NTSC).d64'), '')
        self.assertEqual(extract_region('MultiGame (Disk 2 PAL NTSC).d64'), '')
        self.assertEqual(extract_region('Game (Side 1 Europe).d64'), '')
        
        # Test normalization
        self.assertEqual(extract_region('Game (Eur).d64'), 'Europe')
        self.assertEqual(extract_region('Game (Jp).d64'), 'Japan')
        self.assertEqual(extract_region('Game (En).d64'), 'English')
    
    def test_get_region_priority(self):
        """Test region priority calculation."""
        # Test exact matches
        self.assertEqual(get_region_priority('Europe'), 6)
        self.assertEqual(get_region_priority('PAL'), 5)
        self.assertEqual(get_region_priority('World'), 4)
        self.assertEqual(get_region_priority('USA'), 3)
        self.assertEqual(get_region_priority('Japan'), 2)
        self.assertEqual(get_region_priority('NTSC'), 1)
        self.assertEqual(get_region_priority(''), 0)
        
        # Test partial matches (higher priority regions should be selected)
        self.assertEqual(get_region_priority('USA, Europe'), 6)  # Europe wins
        self.assertEqual(get_region_priority('Europe, Japan'), 6)  # Europe wins
        self.assertEqual(get_region_priority('PAL NTSC'), 5)  # PAL wins
        
        # Test unknown regions
        self.assertEqual(get_region_priority('Unknown'), 0)
    
    def test_regional_variants_vs_multidisk(self):
        """Test that regional variants are handled differently from multi-disk games."""
        # Regional variants should have region info extracted
        usa_region = extract_region('Game 4 (USA).d64')
        europe_region = extract_region('Game 4 (Europe).d64')
        
        self.assertEqual(usa_region, 'USA')
        self.assertEqual(europe_region, 'Europe')
        self.assertGreater(get_region_priority(europe_region), get_region_priority(usa_region))
        
        # Multi-disk games should not have region info extracted
        disk1_region = extract_region('MultiGame (Disk 1 PAL NTSC).d64')
        disk2_region = extract_region('MultiGame (Disk 2 PAL NTSC).d64')
        
        self.assertEqual(disk1_region, '')
        self.assertEqual(disk2_region, '')
        self.assertEqual(get_region_priority(disk1_region), get_region_priority(disk2_region))


if __name__ == '__main__':
    unittest.main()
