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

class TestSatellitePosition(unittest.TestCase):
    
    def setUp(self):
        # Create mock objects for testing
        self.mock_satellite = MagicMock()
        self.mock_observer = MagicMock()
        self.mock_diff = MagicMock()
        self.mock_topocentric = MagicMock()
        self.mock_alt = MagicMock()
        self.mock_az = MagicMock()
        self.mock_distance = MagicMock()
        
        # Set up the chain of mocks to simulate skyfield behavior
        self.mock_satellite.__sub__.return_value = self.mock_diff
        self.mock_diff.at.return_value = self.mock_topocentric
        self.mock_topocentric.altaz.return_value = (self.mock_alt, self.mock_az, self.mock_distance)
        
        # Default properties
        self.mock_distance.km = 400.0
        self.mock_az.degrees = 180.0
        
    def test_below_horizon_altitude(self):
        """Test when ISS is below horizon (negative altitude)"""
        # Set up the mock altitude to return negative degrees
        self.mock_alt.degrees = -15.0
        
        # Call the function
        result = main.get_satellite_position(self.mock_satellite, self.mock_observer)
        
        # Assertions
        self.assertEqual(result['altitude_angle'], 0)
        self.assertEqual(result['alt_degrees'], 0.0)  # Should clamp to 0
        self.assertFalse(result['is_visible'])
        
    def test_zero_altitude(self):
        """Test when ISS is exactly at the horizon (0 altitude)"""
        # Set up the mock altitude to return zero degrees
        self.mock_alt.degrees = 0.0
        
        # Call the function
        result = main.get_satellite_position(self.mock_satellite, self.mock_observer)
        
        # Assertions
        self.assertEqual(result['altitude_angle'], 0)
        self.assertEqual(result['alt_degrees'], 0.0)
        self.assertFalse(result['is_visible'])
        
    def test_low_altitude(self):
        """Test when ISS is just above the horizon (very low altitude)"""
        # Set up the mock altitude to return a low positive value
        self.mock_alt.degrees = 2.0
        
        # Call the function
        result = main.get_satellite_position(self.mock_satellite, self.mock_observer)
        
        # Assertions
        self.assertGreater(result['altitude_angle'], 0)  # Should never be zero when visible
        self.assertEqual(result['alt_degrees'], 2.0)
        self.assertTrue(result['is_visible'])
        
    def test_medium_altitude(self):
        """Test when ISS is at a medium altitude"""
        # Set up the mock altitude
        self.mock_alt.degrees = 45.0
        
        # Call the function
        result = main.get_satellite_position(self.mock_satellite, self.mock_observer)
        
        # Assertions
        self.assertEqual(result['altitude_angle'], 90)  # Should be 90 degrees (middle of servo range)
        self.assertEqual(result['alt_degrees'], 45.0)
        self.assertTrue(result['is_visible'])
        
    def test_high_altitude(self):
        """Test when ISS is at a high altitude (near zenith)"""
        # Set up the mock altitude
        self.mock_alt.degrees = 85.0
        
        # Call the function
        result = main.get_satellite_position(self.mock_satellite, self.mock_observer)
        
        # Assertions
        self.assertAlmostEqual(result['altitude_angle'], 170, delta=2)  # Close to 180 (max servo)
        self.assertEqual(result['alt_degrees'], 85.0)
        self.assertTrue(result['is_visible'])
        
    def test_various_azimuth_angles(self):
        """Test various azimuth angles with constant altitude"""
        self.mock_alt.degrees = 30.0
        
        # Test several azimuth angles
        for az_deg in [0, 90, 180, 270, 359]:
            self.mock_az.degrees = az_deg
            result = main.get_satellite_position(self.mock_satellite, self.mock_observer)
            
            # Verify azimuth conversion from 0-360 to 0-180 range
            expected_az = int(np.interp(az_deg, [0, 360], [0, 180]))
            self.assertEqual(result['azimuth_angle'], expected_az)
            self.assertEqual(result['az_degrees'], az_deg)

if __name__ == '__main__':
    unittest.main()
