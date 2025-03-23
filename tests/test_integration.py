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

class TestIntegration(unittest.TestCase):
    
    @patch('main.load.timescale')
    @patch('main.load.tle_file')
    def test_full_tracking_path(self, mock_tle_file, mock_timescale):
        """Test the full tracking path with simulated ISS movement"""
        # Create mock satellite and observer
        mock_satellite = MagicMock()
        mock_observer = MagicMock()
        
        # Set up mock TLE file loading
        mock_satellite.name = "ISS (ZARYA)"
        mock_tle_file.return_value = [mock_satellite]
        
        # Mock for the altitude test cases
        altitude_series = [-10, -5, 0, 2, 5, 10, 30, 60, 80]
        azimuth_series = [0, 45, 90, 135, 180, 225, 270, 315, 360]
        
        # Create a mock topocentric function that returns different altitudes each time
        mock_topos = MagicMock()
        mock_diff = MagicMock()
        mock_at = MagicMock()
        mock_altaz_results = []
        
        # Create mock alt/az/distance objects for each test case
        for i, (alt, az) in enumerate(zip(altitude_series, azimuth_series)):
            mock_alt = MagicMock()
            mock_alt.degrees = alt
            mock_az = MagicMock()
            mock_az.degrees = az
            mock_distance = MagicMock()
            mock_distance.km = 400 + i * 10  # Vary the distance slightly
            
            mock_altaz_results.append((mock_alt, mock_az, mock_distance))
        
        # Configure the mocks to return the sequence of values
        mock_satellite.__sub__.return_value = mock_diff
        mock_diff.at.return_value = mock_at
        mock_at.altaz.side_effect = mock_altaz_results
        
        # Test cases for different altitudes
        altitude_cases = []
        
        # Collect results for each simulated position
        for i, (alt, az) in enumerate(zip(altitude_series, azimuth_series)):
            # Get the position using our mocked objects
            pos = main.get_satellite_position(mock_satellite, mock_observer)
            
            # Store the results
            altitude_cases.append({
                'test_alt': alt,
                'test_az': az,
                'result_alt_angle': pos['altitude_angle'],
                'result_az_angle': pos['azimuth_angle'],
                'is_visible': pos['is_visible']
            })
        
        # Verify our test cases cover various scenarios
        # Below horizon cases
        below_horizon = [case for case in altitude_cases if case['test_alt'] <= 0]
        self.assertTrue(len(below_horizon) >= 3, "Should have at least 3 below horizon cases")
        for case in below_horizon:
            self.assertFalse(case['is_visible'], f"Should not be visible at altitude {case['test_alt']}")
        
        # Low altitude cases (just above horizon)
        low_altitude = [case for case in altitude_cases if 0 < case['test_alt'] <= 5]
        self.assertTrue(len(low_altitude) >= 2, "Should have at least 2 low altitude cases")
        for case in low_altitude:
            self.assertTrue(case['is_visible'], f"Should be visible at altitude {case['test_alt']}")
            self.assertGreater(case['result_alt_angle'], 0, 
                              f"Altitude angle should be > 0 at {case['test_alt']} degrees")
        
        # Normal altitude cases
        normal_altitude = [case for case in altitude_cases if case['test_alt'] > 5]
        self.assertTrue(len(normal_altitude) >= 3, "Should have at least 3 normal altitude cases")
        
        # Print all test cases for review
        print("\nAltitude Test Cases:")
        print("-" * 80)
        print(f"{'Actual Alt':>10} | {'Actual Az':>10} | {'Servo Alt':>10} | {'Servo Az':>10} | {'Visible':>7}")
        print("-" * 80)
        for case in altitude_cases:
            print(f"{case['test_alt']:10.1f} | {case['test_az']:10.1f} | "
                  f"{case['result_alt_angle']:10d} | {case['result_az_angle']:10d} | "
                  f"{str(case['is_visible']):>7}")
        print("-" * 80)

if __name__ == '__main__':
    unittest.main()
