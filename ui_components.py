"""
UI components for space debris tracking application.
"""
import os
from matplotlib import pyplot as plt

class DebrisTrackerUI:
    def __init__(self):
        """Initialize the UI components."""
        self.clear_terminal()
        
    def clear_terminal(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def display_tracking_info(self, name, altitude, azimuth, distance, visible):
        """Display tracking information in a formatted box."""
        self.clear_terminal()
        
        visibility_status = "VISIBLE" if visible else "BELOW HORIZON"
        
        print("╔═════════════════════════════════════════════════════╗")
        print("║               SPACE DEBRIS TRACKER                   ║")
        print("╠═════════════════════════════════════════════════════╣")
        print(f"║ Object:    {name[:45]}".ljust(57) + "║")
        print(f"║ Altitude:  {altitude:3.1f}°".ljust(57) + "║")
        print(f"║ Azimuth:   {azimuth:3.1f}°".ljust(57) + "║")
        print(f"║ Distance:  {distance:.1f} km".ljust(57) + "║")
        print(f"║ Status:    {visibility_status}".ljust(57) + "║")
        print("╚═════════════════════════════════════════════════════╝")
        print("\nPress Ctrl+C to stop tracking")