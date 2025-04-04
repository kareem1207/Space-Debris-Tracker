from typing import Dict
from skyfield.api import EarthSatellite, load, wgs84

class DebrisTracker:
    def __init__(self):
        self.ts = load.timescale()
        self.location = wgs84.latlon(28.4089, -80.6044)  
    def calculate_positions(self, debris_dict: Dict[str, EarthSatellite]) -> Dict[str, dict]:
        current_time = self.ts.now()
        visible_objects = {}
        
        for name, satellite in debris_dict.items():
            try:
                difference = satellite - self.location
                topocentric = difference.at(current_time)
                alt, az, distance = topocentric.altaz()
                
                position_data = {
                    'altitude': alt.degrees,
                    'azimuth': az.degrees,
                    'distance': distance.km,
                    'visible': alt.degrees > 0
                }
                
                if position_data['visible']:
                    visible_objects[name] = position_data
                    
            except Exception as e:
                print(f"Error calculating position for {name}: {str(e)}")
                continue
        
        return visible_objects