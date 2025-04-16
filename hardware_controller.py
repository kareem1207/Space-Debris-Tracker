import time
import serial

class HardwareController:
    def __init__(self, port="COM5", baud_rate=9600):
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None
        self.location= []
        self.no_port_mode = False

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            time.sleep(2)  
            print(f"Successfully connected to Arduino on {self.port}")
            self.serial_data=self.ser.read(100000).decode("utf-8")
            self.serial_data=self.serial_data.split("\n")[-2]
            print(self.serial_data)
            if "Latitude" in self.serial_data:
                print(self.serial_data)
                temp = self.serial_data.split(" ")
                self.location=[float(temp[1]),float(temp[-1])]
                print(type(self.location[0]))
            else:
                print(self.serial_data)
                self.location=[0,0]
                return 

        except serial.SerialException:
            print(f"Error: Could not connect to Arduino on {self.port}. Entering non-port mode.")
            self.no_port_mode = True
            self.location=[17.389801,78.321151] # This is non port mode location you can change it to your desired location (only change if you don't have a gps module)
        finally:
            return self.location

    def move_servos(self, azimuth, altitude):
        if not self.no_port_mode and self.ser:
            try:
                command = f"SERVO,{azimuth},{altitude}\n"
                self.ser.write(command.encode())
            except serial.SerialException as e:
                print(f"Serial error during servo command: {e}")
                self.no_port_mode = True
        else:
            print(f"Servo: Az={azimuth}, Alt={altitude}")

    def close(self):
        if not self.no_port_mode and self.ser:
            try:
                self.ser.close()
                print("Serial connection closed.")
            except:
                print("Error closing serial connection.")
        return True
if __name__ == "__main__":
    hc = HardwareController()
    hc.connect()