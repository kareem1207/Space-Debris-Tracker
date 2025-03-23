from time import sleep, time
import sys
import os
import signal
import serial
from skyfield.api import Topos, load
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

MAX_DATA_POINTS = 1000
arduino_port = "COM9"
baud_rate = 9600
no_port_mode = False
stop_tracking = False
ser = None

ts = load.timescale()

def connect_arduino():
    global no_port_mode, ser
    try:
        ser = serial.Serial(arduino_port, baud_rate, timeout=1)
        sleep(2)
        print("Successfully connected to Arduino")
        return True
    except serial.SerialException:
        print("Error: Could not connect to Arduino. Entering non-port mode.")
        no_port_mode = True
        return False

def load_satellite_data():
    tle_url = "https://celestrak.org/NORAD/elements/stations.txt"
    print("Fetching satellite data...")
    try:
        satellites = load.tle_file(tle_url)
        if not satellites:
            raise Exception("No satellites found in TLE data")
        
        satellite_dict = {sat.name: sat for sat in satellites}
        
        if "ISS (ZARYA)" not in satellite_dict:
            print("Available satellites:", list(satellite_dict.keys()))
            raise Exception("ISS not found in satellite data")
            
        satellite = satellite_dict["ISS (ZARYA)"]
        print("ISS data loaded successfully")
        return satellite
    except Exception as e:
        print(f"Error: Could not fetch TLE data. {str(e)}")
        print("Check your internet connection or try a different TLE source.")
        sys.exit(1)

def initialize_lcd():
    global no_port_mode
    if not no_port_mode and ser:
        try:
            lcd_init_cmd = "LCD_INIT\n"
            ser.write(lcd_init_cmd.encode())
            sleep(0.5)
            print("LCD initialized")
        except serial.SerialException as e:
            print(f"Serial error during LCD initialization: {e}")
            no_port_mode = True
    else:
        print("LCD initialization skipped in non-port mode.")

def update_lcd(azimuth, altitude, visible):
    global no_port_mode
    if not no_port_mode and ser:
        try:
            visibility = "Visible" if visible else "Not visible"
            lcd_data = f"LCD,{azimuth},{altitude},{visibility}\n"
            ser.write(lcd_data.encode())
        except serial.SerialException as e:
            print(f"Serial error during LCD update: {e}")
            no_port_mode = True
    else:
        print(f"LCD: Az={azimuth}, Alt={altitude}, {visible}")

def on_stop_clicked(event):
    global stop_tracking
    stop_tracking = True
    print("\nStop button clicked. Terminating tracking...")

def create_plot():
    fig = plt.figure(figsize=(10, 8))
    
    ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=5)
    ax1.set_title('ISS Tracking Data')
    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('Angle (degrees)')
    ax1.grid(True)
    
    info_text = ax1.text(0.05, 0.95, '', transform=ax1.transAxes, fontsize=10, 
                        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    button_ax = plt.subplot2grid((6, 1), (5, 0))
    stop_button = Button(button_ax, 'Stop Tracking', color='lightcoral', hovercolor='coral')
    stop_button.on_clicked(on_stop_clicked)
    
    azimuth_line, = ax1.plot([], [], label='Azimuth', color='blue')
    altitude_line, = ax1.plot([], [], label='Altitude', color='red')
    ax1.legend()
    
    return fig, ax1, azimuth_line, altitude_line, info_text

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def limit_data(data_list):
    if len(data_list) > MAX_DATA_POINTS:
        return data_list[-MAX_DATA_POINTS:]
    return data_list

def cleanup():
    if not no_port_mode and ser:
        try:
            ser.close()
            print("Serial connection closed.")
        except:
            pass
    plt.close('all')

def get_satellite_position(satellite, observer):
    t = ts.now()
    diff = satellite - observer
    topocentric = diff.at(t)
    alt, az, distance = topocentric.altaz()
    
    is_visible = alt.degrees > 0
    altitude_degrees = max(0, alt.degrees)
    
    azimuth_angle = int(np.interp(az.degrees, [0, 360], [0, 180]))
    altitude_angle = int(np.interp(altitude_degrees, [0, 90], [0, 180]))
    
    if is_visible and altitude_angle == 0 and altitude_degrees > 0:
        altitude_angle = max(1, int(altitude_degrees * 2))
    
    return {
        'azimuth_angle': azimuth_angle,
        'altitude_angle': altitude_angle,
        'az_degrees': az.degrees,
        'alt_degrees': altitude_degrees,
        'distance': distance.km,
        'is_visible': is_visible
    }

def send_servo_command(azimuth, altitude):
    global no_port_mode
    if not no_port_mode and ser:
        try:
            command = f"SERVO,{azimuth},{altitude}\n"
            ser.write(command.encode())
        except serial.SerialException as e:
            print(f"Serial error during servo command: {e}")
            no_port_mode = True

def signal_handler(sig, frame):
    global stop_tracking
    stop_tracking = True
    print("\nCtrl+C detected. Terminating...")

def main():
    global stop_tracking
    
    signal.signal(signal.SIGINT, signal_handler)
    
    connect_arduino()
    
    satellite = load_satellite_data()
    observer = Topos(latitude_degrees=17.3850, longitude_degrees=78.4867)
    print(f"Observer location: 17.3850°N, 78.4867°E")
    
    initialize_lcd()

    azimuth_data = []
    altitude_data = []
    time_data = []
    visibility_data = []
    
    fig, ax1, azimuth_line, altitude_line, info_text = create_plot()
    plt.ion()
    
    print("Starting ISS tracking...")
    start_time = time()
    update_count = 0
    
    try:
        while not stop_tracking:
            try:
                pos = get_satellite_position(satellite, observer)
                
                send_servo_command(pos['azimuth_angle'], pos['altitude_angle'])
                update_lcd(pos['azimuth_angle'], pos['altitude_angle'], pos['is_visible'])
                
                current_time = time() - start_time
                azimuth_data.append(pos['azimuth_angle'])
                altitude_data.append(pos['altitude_angle'])
                time_data.append(current_time)
                visibility_data.append(1 if pos['is_visible'] else 0)
                
                azimuth_data = limit_data(azimuth_data)
                altitude_data = limit_data(altitude_data)
                time_data = limit_data(time_data)
                visibility_data = limit_data(visibility_data)
                
                visibility_status = "VISIBLE" if pos['is_visible'] else "BELOW HORIZON"
                status_text = (
                    f"ISS Status:\n"
                    f"Az: {pos['azimuth_angle']}° ({pos['az_degrees']:.1f}°)\n"
                    f"Alt: {pos['altitude_angle']}° ({pos['alt_degrees']:.1f}°)\n"
                    f"Distance: {pos['distance']:.1f} km\n"
                    f"Status: {visibility_status}"
                )
                
                clear_terminal()
                print("╔═════════════════════════════════════╗")
                print("║           ISS TRACKER               ║")
                print("╠═════════════════════════════════════╣")
                print(f"║ Azimuth:   {pos['azimuth_angle']:3d}° ({pos['az_degrees']:.1f}°)".ljust(37) + "║")
                print(f"║ Altitude:  {pos['altitude_angle']:3d}° ({pos['alt_degrees']:.1f}°)".ljust(37) + "║")
                print(f"║ Distance:  {pos['distance']:.1f} km".ljust(37) + "║")
                print(f"║ Status:    {visibility_status}".ljust(37) + "║")
                print("╚═════════════════════════════════════╝")
                print(f"Runtime: {current_time:.1f}s | Updates: {update_count} | {'PORT MODE' if not no_port_mode else 'NON-PORT MODE'}")
                
                update_count += 1
                if update_count % 5 == 0 or len(time_data) <= 5:
                    info_text.set_text(status_text)
                    azimuth_line.set_data(time_data, azimuth_data)
                    altitude_line.set_data(time_data, altitude_data)
                    ax1.relim()
                    ax1.autoscale_view()
                    fig.canvas.draw_idle()
                
                fig.canvas.flush_events()
                
                sleep(2)

            except Exception as e:
                print(f"Error: {e}")
                sleep(5)
    
    finally:
        plt.ioff()
        cleanup()
        
        if azimuth_data and altitude_data:
            final_fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            final_fig.suptitle('ISS Tracking Results', fontsize=16)
            
            sns.lineplot(x=time_data, y=azimuth_data, label='Azimuth', ax=ax1, color='blue')
            sns.lineplot(x=time_data, y=altitude_data, label='Altitude', ax=ax1, color='red')
            ax1.set_xlabel('Time (seconds)')
            ax1.set_ylabel('Angle (degrees)')
            ax1.set_title('Azimuth and Altitude')
            ax1.legend()
            ax1.grid(True)
            
            visibility_colors = ['gray' if v == 0 else 'green' for v in visibility_data]
            ax2.scatter(time_data, visibility_data, c=visibility_colors, s=50)
            ax2.set_xlabel('Time (seconds)')
            ax2.set_ylabel('Visibility (0=Hidden, 1=Visible)')
            ax2.set_title('ISS Visibility')
            ax2.set_yticks([0, 1])
            ax2.set_yticklabels(['Hidden', 'Visible'])
            ax2.grid(True)
            
            plt.tight_layout()
            plt.show()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Critical error: {e}")
        cleanup()
        sys.exit(1)
