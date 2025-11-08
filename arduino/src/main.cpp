#include <Arduino.h>
#include "DFRobot_Heartrate.h"

DFRobot_Heartrate heartrate(DIGITAL_MODE);

void setup() {
  Serial.begin(115200);
}

void loop() {
  uint8_t rateValue;
  heartrate.getValue(A1);
  rateValue = heartrate.getRate();
  if(rateValue){
    Serial.println(rateValue);
  }
  delay(100);



}