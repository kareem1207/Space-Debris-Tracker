"""
Main program for space debris tracking.
"""
import time
from data_manager import DataManager
from debris_tracker import DebrisTracker
from hardware_controller import HardwareController
from ui_components import DebrisTrackerUI

def main():
    """Main program entry point."""
    # Initialize components
    data_manager = DataManager()
    tracker = DebrisTracker()
    hardware = HardwareController()
    ui = DebrisTrackerUI()

    # Load all debris data from TLE files
    print("\nLoading debris data...")
    all_debris = data_manager.load_all_debris()
    
    if not all_debris:
        print("\nNo debris data found in TLE cache directory.")
        print(f"Please ensure TLE files are present in: {data_manager.tle_cache_dir}")
        print("Expected files: high_risk_debris.tle, iridium_debris.tle, recent_debris.tle")
        return

    # Print summary of loaded data
    print("\nLoaded debris data summary:")
    total_objects = 0
    for source, debris_dict in all_debris.items():
        print(f"- {source}: {len(debris_dict)} objects")
        total_objects += len(debris_dict)
    print(f"Total objects loaded: {total_objects}\n")
    print("Starting tracking in 3 seconds...")
    time.sleep(3)
    
    # Initialize hardware if available
    hardware.connect()
    
    # Start tracking loop
    try:
        while True:
            found_visible = False
            # Track objects from each source
            for source, debris_dict in all_debris.items():
                visible_objects = tracker.calculate_positions(debris_dict)
                
                if visible_objects:
                    # Display first visible object
                    for name, data in visible_objects.items():
                        # Update UI and hardware
                        ui.display_tracking_info(
                            name, 
                            data['altitude'],
                            data['azimuth'],
                            data['distance'],
                            data['visible']
                        )
                        
                        hardware.move_servos(data['azimuth'], data['altitude'])
                        hardware.update_lcd(data['azimuth'], data['altitude'], True)
                        
                        found_visible = True
                        break  # Only show the first visible object
                    
                    if found_visible:
                        break
            
            if not found_visible:
                ui.display_tracking_info("No objects", 0, 0, 0, False)
                hardware.update_lcd(0, 0, False)
            
            # Wait before next update
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nStopping debris tracker...")
    finally:
        hardware.close()
        print("Tracking system shutdown complete")

if __name__ == "__main__":
    main()
