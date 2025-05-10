import time
from data_manager import DataManager
from debris_tracker import DebrisTracker
from hardware_controller import HardwareController
from ui_components import DebrisTrackerUI
import os
from codecarbon import EmissionsTracker

def main():
    tracker_output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'emissions')
    os.makedirs(tracker_output_dir, exist_ok=True)
    emissions_tracker = EmissionsTracker(
        project_name="Space Debris Tracker",
        output_dir=tracker_output_dir,
        log_level="error"
    )
    
    emissions_tracker.start()
    print("\nCarbon emissions tracking started.")
    
    data_manager = DataManager()
    hardware = HardwareController(port="COM5", baud_rate=9600)
    ui = DebrisTrackerUI()

    print("\nLoading debris data...")
    try:
        print("Fetching combined debris data from multiple online sources...")
        all_debris = data_manager.load_all_debris(fetch_online=True, use_local=True)
    except Exception as e:
        print(f"\nError loading online debris data: {str(e)}")
        print("Attempting to use local cache as fallback...")
        all_debris = data_manager.load_all_debris(fetch_online=False, use_local=True)
    
    if not all_debris:
        print("\nNo debris data found online or in TLE cache directory.")
        print(f"Please check your internet connection or ensure TLE files are present in: {data_manager.tle_cache_dir}")
        print("If you want to use local files, you can run the data_manager.py script separately first to download and cache the data.")
        emissions_tracker.stop()
        print(f"Carbon emissions data saved to: {tracker_output_dir}")
        return

    print("\nLoaded debris data summary:")
    total_objects = 0
    for source, debris_dict in all_debris.items():
        if isinstance(debris_dict, dict):
            source_objects = len(debris_dict)
            total_objects += source_objects
            print(f"- {source}: {source_objects} objects")
    
    print(f"Total objects loaded: {total_objects}\n")
    
    if total_objects == 0:
        print("No valid debris objects found in the data.")
        emissions_tracker.stop()
        return
        
    plots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tracking_plots')
    os.makedirs(plots_dir, exist_ok=True)
    print(f"Tracking plots will be saved to: {plots_dir}")
    
    print("Starting tracking in 3 seconds...")
    time.sleep(3)
    loc = hardware.connect()
    try:
        if loc[0]==0 and loc[1]==0:
            raise Exception("GPS module failed to send the data")
    except Exception as e:
        print(f"Found an error: {e}")
        print("Please check the GPS module connection and try again.")
        return
    tracker = DebrisTracker(loc)

    try:
        last_sky_map_time = time.time()
        sky_map_interval = 60  
        
        while True:
            all_visible_objects = {}
            
            for source, debris_dict in all_debris.items():
                if not isinstance(debris_dict, dict):
                    continue
                    
                visible_objects = tracker.calculate_positions(debris_dict)
                if visible_objects:
                    all_visible_objects.update(visible_objects)
            
            prioritized_objects = {name: data for name, data in all_visible_objects.items() 
                                 if data.get('visible', False) is True}
            
            if prioritized_objects:
                name, data = next(iter(prioritized_objects.items()))
                ui.display_tracking_info(
                    name, 
                    data['altitude'],
                    data['azimuth'],
                    data['distance'],
                    data['visible'],
                    loc
                )
                
                hardware.move_servos(data['azimuth'], data['altitude'])
            elif all_visible_objects:
                name, data = next(iter(all_visible_objects.items()))
                ui.display_tracking_info(
                    name, 
                    data['altitude'],
                    data['azimuth'],
                    data['distance'],
                    data['visible'],
                    loc
                )
            else:
                ui.display_tracking_info("No objects", 0.0, 0.0, 0.0, False, loc)
            
            current_time = time.time()
            if current_time - last_sky_map_time >= sky_map_interval and ui.tracking_data['timestamps']:
                ui.generate_sky_map()
                last_sky_map_time = current_time
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nStopping debris tracker...")
        if ui.tracking_data['timestamps']:
            print("Generating final tracking plots...")
            ui.plot_tracking_data()
            ui.generate_sky_map()
            
    finally:
        hardware.close()
        emissions = emissions_tracker.stop()
        print(f"Carbon emissions tracking stopped.")
        print(f"Total emissions: {emissions:.6f} kg CO2eq")
        print(f"Carbon emissions data saved to: {tracker_output_dir}")
        print("Tracking system shutdown complete")

if __name__ == "__main__":
    main()
