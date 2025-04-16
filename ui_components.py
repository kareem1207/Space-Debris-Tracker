import os
from matplotlib import pyplot as plt
import numpy as np
import time
from datetime import datetime
import matplotlib.dates as mdates

class DebrisTrackerUI:
    def __init__(self):
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
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def display_tracking_info(self, name, altitude, azimuth, distance, visible,loc):
        self.clear_terminal()
        
        visibility_status = "VISIBLE" if visible else "BELOW HORIZON"
        
        print("╔═════════════════════════════════════════════════════╗")
        print("║               SPACE DEBRIS TRACKER                   ║")
        print("╠═════════════════════════════════════════════════════╣")
        print(f"║ Object:    {name[:45]}".ljust(57) + "║")
        print(f"║ Altitude:  {altitude:3.1f}°".ljust(57) + "║")
        print(f"║ Azimuth:   {azimuth:3.1f}°".ljust(57) + "║")
        print(f"║ Your loc:   {loc[0]}°".ljust(57) + "     ║")
        print(f"║ Your deg:   {loc[1]}°".ljust(57) + "     ║")
        print(f"║ Distance:  {distance:.1f} km".ljust(57) + "║")
        print(f"║ Status:    {visibility_status}".ljust(57) + "║")
        print("╚═════════════════════════════════════════════════════╝")
        print("\nPress Ctrl+C to stop tracking")

        if visible:
            self.store_tracking_data(name, altitude, azimuth, distance)
            
        current_time = time.time()
        if current_time - self.last_plot_time >= self.plot_interval and len(self.tracking_data['timestamps']) > 1:
            self.plot_tracking_data()
            self.last_plot_time = current_time

    def store_tracking_data(self, name, altitude, azimuth, distance):
        self.tracking_data['timestamps'].append(datetime.now())
        self.tracking_data['altitudes'].append(altitude)
        self.tracking_data['azimuths'].append(azimuth)
        self.tracking_data['distances'].append(distance)
        self.tracking_data['names'].append(name)
        max_points = 1000
        if len(self.tracking_data['timestamps']) > max_points:
            for key in self.tracking_data:
                self.tracking_data[key] = self.tracking_data[key][-max_points:]

    def plot_tracking_data(self):
        if not self.tracking_data['timestamps']:
            return
            
        plt.figure(figsize=(12, 10))
        plt.subplot(3, 1, 1)
        plt.plot(self.tracking_data['timestamps'], self.tracking_data['altitudes'], 'b-')
        plt.title('Altitude Over Time')
        plt.ylabel('Altitude (degrees)')
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.grid(True)

        plt.subplot(3, 1, 2)
        plt.plot(self.tracking_data['timestamps'], self.tracking_data['azimuths'], 'r-')
        plt.title('Azimuth Over Time')
        plt.ylabel('Azimuth (degrees)')
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.grid(True)
        
        plt.subplot(3, 1, 3)
        plt.plot(self.tracking_data['timestamps'], self.tracking_data['distances'], 'g-')
        plt.title('Distance Over Time')
        plt.ylabel('Distance (km)')
        plt.xlabel('Time')
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.grid(True)
        
        plt.tight_layout()
        
        plots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tracking_plots')
        os.makedirs(plots_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plt.savefig(os.path.join(plots_dir, f'debris_track_{timestamp}.png'))
        plt.draw()
        plt.pause(0.001)  
        plt.close()  
        
        print(f"\nPlot saved to tracking_plots/debris_track_{timestamp}.png")

    def generate_sky_map(self):
        if not self.tracking_data['timestamps']:
            return
            
        plt.figure(figsize=(8, 8))
        ax = plt.subplot(111, projection='polar')
        
        azimuths = np.radians(self.tracking_data['azimuths'][-20:]) 
        altitudes = [90 - alt for alt in self.tracking_data['altitudes'][-20:]]
        names = self.tracking_data['names'][-20:]
        
        sc = ax.scatter(azimuths, altitudes, c=range(len(azimuths)), cmap='viridis', alpha=0.7, s=50)
       
        cbar = plt.colorbar(sc)
        cbar.set_label('Time Sequence (newer points are lighter)')
    
        ax.set_theta_zero_location('N')  
        ax.set_theta_direction(-1)  
        ax.set_rmax(90)  
        ax.set_rticks([0, 30, 60, 90])  
        ax.set_rlabel_position(45)
        ax.set_rlabel_position(-22.5)  
        ax.grid(True)
        
        plt.title('Sky Map of Tracked Objects', va='bottom')
        
        plots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tracking_plots')
        os.makedirs(plots_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plt.savefig(os.path.join(plots_dir, f'sky_map_{timestamp}.png'))
        
        plt.draw()
        plt.pause(0.001)
        plt.close()
        
        print(f"\nSky map saved to tracking_plots/sky_map_{timestamp}.png")