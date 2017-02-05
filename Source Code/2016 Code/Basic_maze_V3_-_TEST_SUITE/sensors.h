//  ------------------------------------------------------
// ----------              Sensors              -----------
// ----------     Rescue Robot Code 2016       -----------
//  ---------                                  -----------
// ---------- Team: Rory W, Ines K & Joseph F  -----------
// ----------         Mentor:Alex C            -----------
// -------------------------------------------------------

#ifndef __SENSORS
#define __SENSORS

#include "pinout.h"
#include "debug_log.h"
#include "movement.h"
#include "lidar.h"

void updateAccel(){
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);

  log(DEBUG,"Accelerometer Values: x:%f y:%f z:%f",euler.x(),euler.y(),euler.z());

  accelX = euler.x();
  accelY = euler.y();
  accelZ = euler.z();
  
}


bool testRamp(){
  bool returnValue = false;
  updateAccel();

    if(accelY > rampYValue){
      returnValue = true;
    }
  return returnValue;
}


void updateLight(){
  
}

void updateTouch(){

   log(DEBUG,"Touch Sensor   Front: %d FrontLeft: %d FrontRight: %d    Back: %d BackLeft: %d BackRight: %d",digitalRead(touchFront),digitalRead(touchFrontLeft),digitalRead(touchFrontRight),digitalRead(touchBack),digitalRead(touchBackLeft),digitalRead(touchBackRight));
  
   touchF  = digitalRead(touchFront);
   touchFL = digitalRead(touchFrontLeft);
   touchFR = digitalRead(touchFrontRight);
   touchB  = digitalRead(touchBack);
   touchBL = digitalRead(touchBackLeft);
   touchBR = digitalRead(touchBackRight);
}


#endif
