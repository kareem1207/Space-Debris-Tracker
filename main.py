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
    all_debris = data_manager.load_all_debris()
    
    if not all_debris:
        print("\nNo debris data found in TLE cache directory.")
        print(f"Please ensure TLE files are present in: {data_manager.tle_cache_dir}")
        print("Expected files: high_risk_debris.tle, iridium_debris.tle, recent_debris.tle")
        emissions_tracker.stop()
        print(f"Carbon emissions data saved to: {tracker_output_dir}")
        return

    print("\nLoaded debris data summary:")
    total_objects = 0
    for source, debris_dict in all_debris.items():
        print(f"- {source}: {len(debris_dict)} objects")
        total_objects += len(debris_dict)
    print(f"Total objects loaded: {total_objects}\n")
    plots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tracking_plots')
    os.makedirs(plots_dir, exist_ok=True)
    print(f"Tracking plots will be saved to: {plots_dir}")
    
    print("Starting tracking in 3 seconds...")
    time.sleep(3)
    loc = hardware.connect()
    try:
        if loc[0]==0 and loc[1]==0:
            raise Exception("Gps module failed to send the data")
    except Exception as e:
        print(f"Found an error: {e}")
        print("Please check the GPS module connection and try again.")
        return
    tracker = DebrisTracker(loc)

    
    try:
        last_sky_map_time = time.time()
        sky_map_interval = 60  
        
        while True:
            found_visible = False
            for source, debris_dict in all_debris.items():
                visible_objects = tracker.calculate_positions(debris_dict)
                
                if visible_objects:
                    for name, data in visible_objects.items():
                        ui.display_tracking_info(
                            name, 
                            data['altitude'],
                            data['azimuth'],
                            data['distance'],
                            data['visible'],
                            loc
                        )
                        
                        hardware.move_servos(data['azimuth'], data['altitude'])
                        
                        found_visible = True
                        break  
                    
                    if found_visible:
                        break
            
            if not found_visible:
                ui.display_tracking_info("No objects", 0, 0, 0, False,loc)
            
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
