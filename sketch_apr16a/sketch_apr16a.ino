#include <SoftwareSerial.h>
#include <TinyGPS++.h>
#include <Servo.h>

SoftwareSerial gpsSerial(4, 3); // RX, TX for GPS
TinyGPSPlus gps;

Servo servoAzimuth;
Servo servoAltitude;

String inputString = "";

void setup()
{
  Serial.begin(9600);
  gpsSerial.begin(9600);
  Serial.println("Waiting for GPS signal...");

  servoAzimuth.attach(9);   // Attach azimuth servo to pin 9
  servoAltitude.attach(10); // Attach altitude servo to pin 10
}

void loop()
{
  // GPS Processing
  while (gpsSerial.available())
  {
    gps.encode(gpsSerial.read());

    if (gps.location.isUpdated())
    {
      Serial.print("Latitude: ");
      Serial.print(gps.location.lat(), 6);
      Serial.print(" | Longitude: ");
      Serial.println(gps.location.lng(), 6);
    }
  }

  // Servo Control via Serial
  while (Serial.available())
  {
    char inChar = (char)Serial.read();
    if (inChar == '\n')
    {
      processCommand(inputString);
      inputString = "";
    }
    else
    {
      inputString += inChar;
    }
  }
}

void processCommand(String cmd)
{
  // Expected format: SERVO,azimuth,altitude
  if (cmd.startsWith("SERVO"))
  {
    int firstComma = cmd.indexOf(',');
    int secondComma = cmd.indexOf(',', firstComma + 1);

    if (firstComma > 0 && secondComma > firstComma)
    {
      int az = cmd.substring(firstComma + 1, secondComma).toInt();
      int alt = cmd.substring(secondComma + 1).toInt();

      az = constrain(az, 0, 180);
      alt = constrain(alt, 0, 180);

      servoAzimuth.write(az);
      servoAltitude.write(alt);
    }
  }
}
