#include <DFRobot_Heartrate.h>
#include "accelerometer.h"
#include <Adafruit_DRV2605.h>

DFRobot_Heartrate heartrate(DIGITAL_MODE);
DFRobot_LIS2DH12 acce(&Wire, 0x18);
Adafruit_DRV2605 vib;
uint8_t rateValue;
uint8_t prevRateValue;
bool heartRateStarted = 0;

bool vibrating = false;


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

  
    
  
  Serial.flush();

  // Accel
  AccelReading accelReading;
  accelReading = readGyro(acce);
  


  // Temp
  uint16_t val;
  double dat;
  val=analogRead(A0);//Connect LM35 on Analog 0
  dat = (double) val * (5/10.24);
  
  Serial.flush();

  // Vibrator
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    Serial.println(input);
    if (input == "START"){
      if (vibrating == false) {
        vib.setRealtimeValue(0); // val between 0 and 255 (or maybe 128 and 255?)
        vibrating = true;
      }
      
    }
  }
  // //Fallback demo code w/o serial
  // if (vibrating == false) {
  //   vib.setRealtimeValue(0); // val between 0 and 255 (or maybe 128 and 255?)
  //   vibrating = true;
  // }
  

  //button
  if (digitalRead(4) == LOW && vibrating) {
    vib.setRealtimeValue(128);
    vibrating = false;
  }
  for (int i = 0; i < 20; i++){
    Serial.println();
  }
  Serial.print("AccelX:");
  Serial.println(accelReading.x);
  Serial.print("AccelY:");
  Serial.println(accelReading.y);
  Serial.print("AccelZ:");
  Serial.println(accelReading.z);
  Serial.print("Temp:"); //Display the temperature on Serial monitor
  Serial.println(dat);
  // Heart Rate
  heartrate.getValue(A2);
  rateValue = heartrate.getRate();
  if (rateValue == 0){
    if (!heartRateStarted) {
      Serial.println("HeartRate:NULL");
    }
    else {
      Serial.print("HeartRate:");
      Serial.println(prevRateValue);
      
    }
  }
  else {
    Serial.print("HeartRate:");
    Serial.println(rateValue);
    prevRateValue = rateValue;
    heartRateStarted = 1;
  }
  delay(200);
  
  
}