#include <DFRobot_Heartrate.h>
#include "accelerometer.h"
#include <Adafruit_DRV2605.h>

DFRobot_Heartrate heartrate(DIGITAL_MODE);
DFRobot_LIS2DH12 acce(&Wire, 0x18);
Adafruit_DRV2605 vib;
uint8_t rateValue;
uint8_t prevRateValue;
bool heartRateStarted = 1;
const int ledPin = LED_BUILTIN;



void setup() {
  Serial.begin(115200);
  setupAccel(acce);
  if (! vib.begin()) {
    Serial.println("Could not find DRV2605");
    while (1) delay(10);
  }
  vib.begin();
  vib.setMode(DRV2605_MODE_REALTIME);

  pinMode(ledPin, OUTPUT);
}

void loop() {
  digitalWrite(ledPin, HIGH);

  // Wait for 1000 milliseconds (1 second)
  delay(200);

  // Step 2: Turn the LED OFF
  // LOW (0V or ground) turns the LED off
  digitalWrite(ledPin, LOW);

  // Wait for 1000 milliseconds (1 second)
  delay(200);



  // Heart Rate
  heartrate.getValue(A2);
  rateValue = heartrate.getRate();
  if (rateValue > 0){
    heartRateStarted = 1;
  }else{
    heartRateStarted = 0;
  }
  // Check to see if heart rate has been gotten at all
  if(!heartRateStarted){
    Serial.println("HeartRate:NULL");
  }
  // If it has, print a value
  else {
    Serial.print("HeartRate:");
    Serial.println(rateValue);
  }
    
  
  Serial.flush();

  // Accel
  AccelReading accelReading;
  accelReading = readGyro(acce);
  Serial.print("AccelX:");
  Serial.println(accelReading.x);
  Serial.print("AccelY:");
  Serial.println(accelReading.y);
  Serial.print("AccelZ:");
  Serial.println(accelReading.z);

  // Temp
  uint16_t val;
  double dat;
  val=analogRead(A0);//Connect LM35 on Analog 0
  dat = (double) val * (5/10.24);
  Serial.print("Temp:"); //Display the temperature on Serial monitor
  Serial.println(dat);
  Serial.flush();

  // Vibrator
  vib.setRealtimeValue(128); // val between 0 and 255 (or maybe 128 and 255?)
  delay(20);
  vib.setRealtimeValue(0);


  delay(20);



}