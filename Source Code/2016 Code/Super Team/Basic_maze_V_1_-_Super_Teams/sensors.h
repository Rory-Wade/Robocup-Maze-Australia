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

uint16_t r, g, b, c, colorTemp, lux;


void updateAccel(){
  //inertia mesurment unit 

  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);

  log(DEBUG,"Accelerometer Values: x:%f y:%f z:%f",euler.x(),euler.y(),euler.z());
  
  accelX = euler.x();
  accelY = euler.y();
  accelZ = euler.z();

  if(accelX < 0.01){
     digitalWrite(DATA_IN_LED, HIGH);
     
  }else{
     digitalWrite(DATA_IN_LED, LOW);
     
  }
  delay(2);
  
}


void resetIMU(){
  
  
  digitalWrite(AccelReset, LOW);
  delay(500);
  currentDirection = 0;
  digitalWrite(AccelReset, HIGH);
  /* Initialise the sensor */
  while (!bno.begin()){
    
    /* There was a problem detecting the BNO055 ... check your connections */
    log(ERROR,"no BNO055 detected ... Check your wiring or I2C ADDR! Please restart Program!");
    delay(2000);
    digitalWrite(DATA_IN_LED, HIGH);
  }
  updateAccel();
  digitalWrite(DATA_IN_LED, LOW);
}

void updateLight(){

  tcs.getRawData(&r, &g, &b, &c);
  colorTemp = tcs.calculateColorTemperature(r, g, b);
  lux = tcs.calculateLux(r, g, b);

  log(DEBUG, "Colour Temperature: %dK Lux: %d R: %d G: %d B: %d C: %d", colorTemp, lux, r, g, b, c);  
}

bool BlackTileFound(){
  updateLight();

  if(lux > BlackValue - colourThresh * 2 && lux < BlackValue + colourThresh * 2){
    return true;
    
  }else{
    return false;
    
  }

}


bool SilverTileFound(){
  updateLight();

  if(lux > SilverValue - colourThresh * 2 && lux < SilverValue + colourThresh * 2){
    return true;
    
  }else{
    return false;
    
  }

}


bool onRamp(){
  bool returnValue = false;
  updateAccel();

    if(accelY > rampYValue){
      returnValue = true;
      RampUp = true;
      
      }else if(accelY < -rampYValue){
        returnValue = true;
        RampDown = true;

      }
  return returnValue;
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



void I2CScan(){
  byte error, address;
  int nDevices;
 
  Serial.println("Scanning...");
 
  nDevices = 0;
  for(address = 1; address < 127; address++ )
  {
    // The i2c_scanner uses the return value of
    // the Write.endTransmisstion to see if
    // a device did acknowledge to the address.
    Wire.beginTransmission(address);
    error = Wire.endTransmission();
 
    if (error == 0)
    {
      Serial.print("I2C device found at address 0x");
      if (address<16)
        Serial.print("0");
      Serial.print(address,HEX);
      Serial.println("  !");
 
      nDevices++;
    }
    else if (error==4)
    {
      Serial.print("Unknow error at address 0x");
      if (address<16)
        Serial.print("0");
      Serial.println(address,HEX);
    }    
  }
  if (nDevices == 0)
    Serial.println("No I2C devices found\n");
  else
    Serial.println("done\n");
}

#endif
