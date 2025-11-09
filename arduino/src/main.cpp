#include <Arduino.h>
#include "DFRobot_Heartrate.h"
#include "accelerometer.h"

DFRobot_Heartrate heartrate(DIGITAL_MODE);
DFRobot_LIS2DH12 acce(&Wire, 0x18);

void setup() {
  Serial.begin(115200);
  setupAccel(acce);
}

void loop() {
  uint8_t rateValue;
  heartrate.getValue(A1);
  rateValue = heartrate.getRate();
  if(rateValue){
    Serial.println(rateValue);
  }
  delay(100);

  readGyro(acce);



}