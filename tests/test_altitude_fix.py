import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import numpy as np

# Add parent directory to path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    import main
except ImportError:
    # Try a direct import as a fallback
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
    import main

class TestAltitudeFix(unittest.TestCase):
    """Tests specifically for the altitude fix implementation"""
    
    def test_very_low_altitude_fix(self):
        """Test the fix for very low altitude values (0-5 degrees)"""
        # Create mock objects
        mock_satellite = MagicMock()
        mock_observer = MagicMock()
        
        # Set up for very low altitude cases
        test_altitudes = [0.1, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0]
        results = []
        
        # Test each altitude value
        for test_alt in test_altitudes:
            # Create mock chain
            mock_diff = MagicMock()
            mock_topocentric = MagicMock()
            mock_alt = MagicMock()
            mock_alt.degrees = test_alt
            mock_az = MagicMock()
            mock_az.degrees = 180.0  # Fixed azimuth for these tests
            mock_distance = MagicMock()
            mock_distance.km = 400.0
            
            # Link mocks
            mock_satellite.__sub__.return_value = mock_diff
            mock_diff.at.return_value = mock_topocentric
            mock_topocentric.altaz.return_value = (mock_alt, mock_az, mock_distance)
            
            # Get position
            result = main.get_satellite_position(mock_satellite, mock_observer)
            
            # Store results
            results.append({
                'input_alt': test_alt,
                'output_alt_angle': result['altitude_angle'],
                'is_visible': result['is_visible']
            })
        
        # Print results for visual inspection
        print("\nVery Low Altitude Fix Test Results:")
        print("-" * 60)
        print(f"{'Input Alt':>10} | {'Output Alt Angle':>16} | {'Visible':>7}")
        print("-" * 60)
        for result in results:
            print(f"{result['input_alt']:10.1f} | {result['output_alt_angle']:16d} | {str(result['is_visible']):>7}")
        print("-" * 60)
        
        # Assertions
        for result in results:
            # All these tests should be visible
            self.assertTrue(result['is_visible'], 
                          f"ISS at {result['input_alt']} degrees should be visible")
            
            # Ensure altitude angle is never zero for visible ISS
            self.assertGreater(result['output_alt_angle'], 0,
                             f"Altitude angle should be > 0 when ISS is visible at {result['input_alt']} degrees")
            
            # Very low altitudes should be amplified
            if result['input_alt'] < 2.0:
                self.assertGreaterEqual(result['output_alt_angle'], 5,
                                     f"Very low altitudes ({result['input_alt']} deg) should be amplified")

if __name__ == '__main__':
    unittest.main()
