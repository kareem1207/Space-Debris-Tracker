"""
Debris tracker for calculating positions of space debris.
"""
from typing import Dict
from skyfield.api import EarthSatellite, load, wgs84

class DebrisTracker:
    def __init__(self):
        """Initialize the debris tracker."""
        self.ts = load.timescale()
        self.location = wgs84.latlon(28.4089, -80.6044)  # Cape Canaveral coordinates
        
    def calculate_positions(self, debris_dict: Dict[str, EarthSatellite]) -> Dict[str, dict]:
        """Calculate current positions for debris objects."""
        current_time = self.ts.now()
        visible_objects = {}
        
        for name, satellite in debris_dict.items():
            try:
                # Calculate position
                difference = satellite - self.location
                topocentric = difference.at(current_time)
                alt, az, distance = topocentric.altaz()
                
                # Store position data
                position_data = {
                    'altitude': alt.degrees,
                    'azimuth': az.degrees,
                    'distance': distance.km,
                    'visible': alt.degrees > 0
                }
                
                # Only include if object is above horizon
                if position_data['visible']:
                    visible_objects[name] = position_data
                    
            except Exception as e:
                print(f"Error calculating position for {name}: {str(e)}")
                continue
        
        return visible_objects