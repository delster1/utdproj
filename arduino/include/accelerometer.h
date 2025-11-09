#ifndef ACCELEROMETER_H
#define ACCELEROMETER_H

#include <Arduino.h>
#include <Wire.h>
#include "DFRobot_LIS2DH12.h"

// Simple POD to return 3-axis acceleration values in mg
struct AccelReading {
    long x;
    long y;
    long z;
};

// Initialize the accelerometer chip
void setupAccel(DFRobot_LIS2DH12 acce);

// Read acceleration and return x,y,z in mg
AccelReading readGyro(DFRobot_LIS2DH12 acce);

#endif // ACCELEROMETER_H

