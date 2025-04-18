
#include <SoftwareSerial.h>
#include <TinyGPS++.h>

SoftwareSerial gpsSerial(4, 3);
TinyGPSPlus gps;

void setup()
{
  Serial.begin(9600);
  gpsSerial.begin(9600);
  Serial.println("Waiting for GPS signal...");
}

void loop()
{

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
}