"""
UI components for space debris tracking application.
"""
import os
from matplotlib import pyplot as plt
import numpy as np
import time
from datetime import datetime
import matplotlib.dates as mdates

class DebrisTrackerUI:
    def __init__(self):
        """Initialize the UI components."""
        self.clear_terminal()
        self.tracking_data = {
            'timestamps': [],
            'altitudes': [],
            'azimuths': [],
            'distances': [],
            'names': []
        }
        self.last_plot_time = time.time()
        self.plot_interval = 30  
        
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

        if visible:
            self.store_tracking_data(name, altitude, azimuth, distance)
            
        # Check if it's time to update the plot
        current_time = time.time()
        if current_time - self.last_plot_time >= self.plot_interval and len(self.tracking_data['timestamps']) > 1:
            self.plot_tracking_data()
            self.last_plot_time = current_time

    def store_tracking_data(self, name, altitude, azimuth, distance):
        """Store tracking data for later plotting."""
        self.tracking_data['timestamps'].append(datetime.now())
        self.tracking_data['altitudes'].append(altitude)
        self.tracking_data['azimuths'].append(azimuth)
        self.tracking_data['distances'].append(distance)
        self.tracking_data['names'].append(name)
        
        # Limit data points to prevent memory issues
        max_points = 1000
        if len(self.tracking_data['timestamps']) > max_points:
            for key in self.tracking_data:
                self.tracking_data[key] = self.tracking_data[key][-max_points:]

    def plot_tracking_data(self):
        """Generate plots from the collected tracking data."""
        if not self.tracking_data['timestamps']:
            return
            
        plt.figure(figsize=(12, 10))
        
        # First subplot: Altitude over time
        plt.subplot(3, 1, 1)
        plt.plot(self.tracking_data['timestamps'], self.tracking_data['altitudes'], 'b-')
        plt.title('Altitude Over Time')
        plt.ylabel('Altitude (degrees)')
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.grid(True)
        
        # Second subplot: Azimuth over time
        plt.subplot(3, 1, 2)
        plt.plot(self.tracking_data['timestamps'], self.tracking_data['azimuths'], 'r-')
        plt.title('Azimuth Over Time')
        plt.ylabel('Azimuth (degrees)')
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.grid(True)
        
        # Third subplot: Distance over time
        plt.subplot(3, 1, 3)
        plt.plot(self.tracking_data['timestamps'], self.tracking_data['distances'], 'g-')
        plt.title('Distance Over Time')
        plt.ylabel('Distance (km)')
        plt.xlabel('Time')
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.grid(True)
        
        plt.tight_layout()
        
        # Create plots directory if it doesn't exist
        plots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tracking_plots')
        os.makedirs(plots_dir, exist_ok=True)
        
        # Save plot
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plt.savefig(os.path.join(plots_dir, f'debris_track_{timestamp}.png'))
        
        # Show the plot in a non-blocking way
        plt.draw()
        plt.pause(0.001)  # Small pause to allow the plot to render
        plt.close()  # Close the figure to free memory
        
        print(f"\nPlot saved to tracking_plots/debris_track_{timestamp}.png")

    def generate_sky_map(self):
        """Generate a sky map showing the current position of tracked objects."""
        if not self.tracking_data['timestamps']:
            return
            
        plt.figure(figsize=(8, 8))
        ax = plt.subplot(111, projection='polar')
        
        # Get the most recent data points
        azimuths = np.radians(self.tracking_data['azimuths'][-20:])  # Convert to radians
        # For polar plot, radius is 90-altitude (zenith is center)
        altitudes = [90 - alt for alt in self.tracking_data['altitudes'][-20:]]
        names = self.tracking_data['names'][-20:]
        
        # Plot points
        sc = ax.scatter(azimuths, altitudes, c=range(len(azimuths)), cmap='viridis', alpha=0.7, s=50)
        
        # Add a colorbar to indicate time sequence (recent points are lighter)
        cbar = plt.colorbar(sc)
        cbar.set_label('Time Sequence (newer points are lighter)')
        
        # Set up the plot
        ax.set_theta_zero_location('N')  # Set 0 degrees to North
        ax.set_theta_direction(-1)  # Go clockwise
        ax.set_rmax(90)  # Max radius is 90 degrees from zenith
        ax.set_rticks([0, 30, 60, 90])  # Show altitude lines
        ax.set_rlabel_position(45)
        ax.set_rlabel_position(-22.5)  # Offset the labels
        ax.grid(True)
        
        # Add labels
        plt.title('Sky Map of Tracked Objects', va='bottom')
        
        # Create plots directory if it doesn't exist
        plots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tracking_plots')
        os.makedirs(plots_dir, exist_ok=True)
        
        # Save plot
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plt.savefig(os.path.join(plots_dir, f'sky_map_{timestamp}.png'))
        
        plt.draw()
        plt.pause(0.001)
        plt.close()
        
        print(f"\nSky map saved to tracking_plots/sky_map_{timestamp}.png")