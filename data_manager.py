"""
Data manager for handling TLE files and debris data.
"""
import os
import glob
from skyfield.api import EarthSatellite, load
from typing import Dict

class DataManager:
    def __init__(self, tle_cache_dir='tle_cache'):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.tle_cache_dir = os.path.join(current_dir, tle_cache_dir)
        self.ts = load.timescale()
        print(f"Using TLE cache directory: {self.tle_cache_dir}")

    def load_tle_file(self, filepath: str) -> Dict[str, EarthSatellite]:
        satellites = {}
        try:
            print(f"Loading TLE file: {filepath}")
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            for i in range(0, len(lines), 3):
                if i + 2 >= len(lines):
                    break
                    
                try:
                    name = lines[i]
                    line1 = lines[i + 1]
                    line2 = lines[i + 2]
                    
                    if len(line1) == 69 and len(line2) == 69 and line1.startswith('1 ') and line2.startswith('2 '):
                        satellite = EarthSatellite(line1, line2, name, self.ts)
                        satellites[name] = satellite
                    
                except Exception as e:
                    print(f"Error processing TLE set for {name}: {str(e)}")
                    continue
            
            print(f"Successfully loaded {len(satellites)} objects from {os.path.basename(filepath)}")
            
        except Exception as e:
            print(f"Error reading file {filepath}: {str(e)}")
        
        return satellites

    def load_all_debris(self) -> Dict[str, Dict[str, EarthSatellite]]:
        all_debris = {}
        tle_pattern = os.path.join(self.tle_cache_dir, "*.tle")
        tle_files = glob.glob(tle_pattern)
        
        print(f"\nSearching for TLE files in: {self.tle_cache_dir}")
        print(f"Found {len(tle_files)} TLE files")
        
        for filepath in tle_files:
            try:
                filename = os.path.basename(filepath)
                satellites = self.load_tle_file(filepath)
                if satellites:
                    all_debris[filename] = satellites
                    print(f"Successfully loaded {len(satellites)} objects from {filename}")
                else:
                    print(f"No valid objects loaded from {filename}")
            except Exception as e:
                print(f"Error processing {filepath}: {str(e)}")
        
        return all_debris