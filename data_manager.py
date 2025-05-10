import os
import glob
from skyfield.api import EarthSatellite, load
import requests
from datetime import datetime

class DataManager:
    def __init__(self, tle_cache_dir='tle_cache'):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.tle_cache_dir = os.path.join(current_dir, tle_cache_dir)
        self.ts = load.timescale()
        print(f"Using TLE cache directory: {self.tle_cache_dir}")
        
        os.makedirs(self.tle_cache_dir, exist_ok=True)

    def load_tle_file(self, filepath):
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

    def fetch_online_tle(self, combine_sources=True):
        """
        Fetch TLE data from online sources with more comprehensive debris data
        combine_sources: If True, combines data from multiple debris catalogs
        """
        debris_sources = [
            'https://celestrak.org/NORAD/elements/gp.php?GROUP=iridium-33-debris&FORMAT=tle',
            'https://celestrak.org/NORAD/elements/gp.php?GROUP=cosmos-2251-debris&FORMAT=tle',
            'https://celestrak.org/NORAD/elements/gp.php?GROUP=fengyun-1c-debris&FORMAT=tle',
            'https://celestrak.org/NORAD/elements/gp.php?GROUP=1999-025&FORMAT=tle',  # NOAA-15 debris
            'https://celestrak.org/NORAD/elements/gp.php?GROUP=latest-launches&FORMAT=tle',
            'https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle'
        ]
        
        fallback_sources = [
            'https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle',
            'https://celestrak.org/NORAD/elements/gp.php?GROUP=last-30-days&FORMAT=tle'
        ]
        
        all_satellite_dict = {}
        used_sources = []

        try:
            if combine_sources:
                for url in debris_sources:
                    try:
                        print(f"Fetching TLE data from: {url}")
                        response = requests.get(url)
                        
                        if response.status_code == 200 and "Invalid query" not in response.text:
                            satellites = load.tle_file(url)
                            
                            for sat in satellites:
                                all_satellite_dict[sat.name] = sat
                            
                            used_sources.append(url)
                            print(f"Added {len(satellites)} objects from {url}")
                            
                            source_name = url.split('GROUP=')[1].split('&')[0]
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                            cache_filename = os.path.join(self.tle_cache_dir, f"debris_{source_name}_{timestamp}.tle")
                            
                            with open(cache_filename, 'w', encoding='utf-8') as f:
                                f.write(response.text)
                            print(f"Saved {source_name} data to {cache_filename}")
                        else:
                            print(f"Invalid response from {url}, skipping...")
                            
                    except Exception as e:
                        print(f"Error fetching from {url}: {str(e)}")
                
                if not all_satellite_dict:
                    print("No debris data fetched from primary sources, trying fallbacks...")
                    for url in fallback_sources:
                        try:
                            satellites = load.tle_file(url)
                            for sat in satellites:
                                all_satellite_dict[sat.name] = sat
                            used_sources.append(url)
                            print(f"Added {len(satellites)} objects from fallback {url}")
                        except Exception as e:
                            print(f"Error with fallback {url}: {str(e)}")
                
                if all_satellite_dict:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                    combined_filename = os.path.join(self.tle_cache_dir, f"combined_debris_{timestamp}.tle")
                    
                    try:
                        with open(combined_filename, 'w', encoding='utf-8') as f:
                            for sat_name, sat in all_satellite_dict.items():
                                f.write(f"{sat_name}\n")
                                f.write(f"{sat.model.line1}\n")
                                f.write(f"{sat.model.line2}\n")
                        print(f"Saved combined data with {len(all_satellite_dict)} objects to {combined_filename}")
                    except Exception as e:
                        print(f"Failed to save combined data: {str(e)}")
                
                print(f"Successfully fetched a total of {len(all_satellite_dict)} objects from {len(used_sources)} sources")
                return {"online_combined_debris": all_satellite_dict}
            
            else:
                url = debris_sources[0]
                print(f"Fetching TLE data from single source: {url}")
                satellites = load.tle_file(url)
                
                satellite_dict = {}
                for sat in satellites:
                    satellite_dict[sat.name] = sat
                    
                print(f"Successfully fetched {len(satellite_dict)} objects from {url}")
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                cache_filename = os.path.join(self.tle_cache_dir, f"online_debris_{timestamp}.tle")
                
                try:
                    response = requests.get(url)
                    if response.status_code == 200:
                        with open(cache_filename, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        print(f"Saved online TLE data to {cache_filename}")
                except Exception as e:
                    print(f"Failed to save TLE data to cache: {str(e)}")
                
                return {"online_debris": satellite_dict}
                
        except Exception as e:
            print(f"Error in fetch_online_tle: {str(e)}")
            return {}

    def load_all_debris(self, fetch_online=True, use_local=False):
        """
        Load debris data with options to control sources.
        fetch_online: Whether to fetch data from online source
        use_local: Whether to load data from local cache files
        """
        all_debris = {}
        
        if fetch_online:
            try:
                online_debris = self.fetch_online_tle()
                all_debris.update(online_debris)
                print(f"Using online data as primary source")
            except Exception as e:
                print(f"Failed to fetch online data: {str(e)}")
                if not use_local:
                    print("Online fetch failed. Falling back to local cache.")
                    use_local = True
        
        if use_local:
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

if __name__ == "__main__":
    data_manager = DataManager()
    all_debris = data_manager.load_all_debris(fetch_online=True, use_local=True)
    print(f"Total debris collections loaded: {len(all_debris)}")
    
    total_satellites = sum(len(satellites) for satellites in all_debris.values())
    print(f"Total satellite objects loaded: {total_satellites}")