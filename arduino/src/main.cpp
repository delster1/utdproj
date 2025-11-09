#include <DFRobot_Heartrate.h>
#include "accelerometer.h"
#include <Adafruit_DRV2605.h>

DFRobot_Heartrate heartrate(DIGITAL_MODE);
DFRobot_LIS2DH12 acce(&Wire, 0x18);
Adafruit_DRV2605 vib;


void setup() {
  Serial.begin(115200);
  setupAccel(acce);
  if (! vib.begin()) {
    Serial.println("Could not find DRV2605");
    while (1) delay(10);
  }
  vib.begin();
  vib.setMode(DRV2605_MODE_REALTIME);
}

void loop() {
  // Heart Rate
  uint8_t rateValue;
  heartrate.getValue(A1);
  rateValue = heartrate.getRate();
  if(rateValue){
    Serial.println("HeartRate:" + rateValue);
  }
  else {
    Serial.println("HeartRate:NULL");
  }
  Serial.flush();

  // Accel
  AccelReading accelReading;
  accelReading = readGyro(acce);
  Serial.println("AccelX:"+accelReading.x);
  Serial.println("AccelY:"+accelReading.y);
  Serial.println("AccelZ:"+accelReading.z);
  Serial.flush();

  // Temp
  uint16_t val;
  double dat;
  val=analogRead(A0);//Connect LM35 on Analog 0
  dat = (double) val * (5/10.24);
  Serial.print("Temp:"); //Display the temperature on Serial monitor
  Serial.println(dat);
  Serial.flush();

  // Vibrator
  vib.setRealtimeValue(255); // val between 0 and 255 (or maybe 128 and 255?)
  delay(100);
  vib.setRealtimeValue(128);
  delay(100);


  delay(20);



}