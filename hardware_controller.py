"""
Hardware controller for space debris tracking.
Handles Arduino connection, LCD display, and servo control.
"""
import time
import serial

class HardwareController:
    def __init__(self, port="COM9", baud_rate=9600):
        """Initialize the hardware controller with specified serial port and baud rate."""
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None
        self.no_port_mode = False

    def connect(self):
        """Connect to the Arduino."""
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            time.sleep(2)  
            print(f"Successfully connected to Arduino on {self.port}")
            return True
        except serial.SerialException:
            print(f"Error: Could not connect to Arduino on {self.port}. Entering non-port mode.")
            self.no_port_mode = True
            return False

    def initialize_lcd(self):
        """Initialize the LCD display."""
        if not self.no_port_mode and self.ser:
            try:
                lcd_init_cmd = "LCD_INIT\n"
                self.ser.write(lcd_init_cmd.encode())
                time.sleep(0.5)
                print("LCD initialized")
            except serial.SerialException as e:
                print(f"Serial error during LCD initialization: {e}")
                self.no_port_mode = True
        else:
            print("LCD initialization skipped in non-port mode.")

    def update_lcd(self, azimuth, altitude, visible):
        if not self.no_port_mode and self.ser:
            try:
                visibility = "Visible" if visible else "Not visible"
                lcd_data = f"LCD,{azimuth},{altitude},{visibility}\n"
                self.ser.write(lcd_data.encode())
                return True
            except serial.SerialException as e:
                print(f"Serial error during LCD update: {e}")
                self.no_port_mode = True
                return False
        else:
            print(f"LCD: Az={azimuth}, Alt={altitude}, {'Visible' if visible else 'Not visible'}")
            return True

    def move_servos(self, azimuth, altitude):
        """Send servo movement commands to Arduino."""
        if not self.no_port_mode and self.ser:
            try:
                command = f"SERVO,{azimuth},{altitude}\n"
                self.ser.write(command.encode())
                return True
            except serial.SerialException as e:
                print(f"Serial error during servo command: {e}")
                self.no_port_mode = True
                return False
        else:
            print(f"Servo: Az={azimuth}, Alt={altitude}")
            return True

    def close(self):
        if not self.no_port_mode and self.ser:
            try:
                self.ser.close()
                print("Serial connection closed.")
                return True
            except:
                print("Error closing serial connection.")
                return False
        return True