/*
 * RoboPeak RPLIDAR Arduino Example
 * This example shows the easy and common way to fetch data from an RPLIDAR
 * 
 * You may freely add your application code based on this template
 *
 * USAGE:
 * ---------------------------------
 * 1. Download this sketch code to your Arduino board
 * 2. Connect the RPLIDAR's serial port (RX/TX/GND) to your Arduino board (Pin 0 and Pin1)
 * 3. Connect the RPLIDAR's motor ctrl pin to the Arduino board pin 3 
 */
 
/* 
 * Copyright (c) 2014, RoboPeak 
 * All rights reserved.
 * RoboPeak.com
 *
 * Redistribution and use in source and binary forms, with or without modification, 
 * are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, 
 *    this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice, 
 *    this list of conditions and the following disclaimer in the documentation 
 *    and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY 
 * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES 
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT 
 * SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT 
 * OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR 
 * TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, 
 * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */
 
// This sketch code is based on the RPLIDAR driver library provided by RoboPeak
#include <RPLidar.h>

// You need to create an driver instance 
RPLidar lidar;

#define RPLIDAR_MOTOR 3 // The PWM pin for control the speed of RPLIDAR's motor.
                        // This pin should connected with the RPLIDAR's MOTOCTRL signal 
float North = -1;                
float South = -1;
float East  = -1;
float West  = -1;

float NorthSouth = -1; 
float SouthEast  = -1;
float EastWest   = -1;
float NorthWest  = -1;
                      
void setup() {
  // bind the RPLIDAR driver to the arduino hardware serial
  lidar.begin(Serial1);
  Serial.begin(250000);
  
  // set pin modes
  pinMode(RPLIDAR_MOTOR, OUTPUT);
}

void pushData(){
  if(North >= 0 && South >= 0 && East >= 0 && West >= 0 && NorthSouth >= 0 && SouthEast >= 0 && EastWest >= 0 && NorthWest >= 0){

    Serial.print("North:");
    Serial.println(North);

    Serial.print("East:");
    Serial.println(East);

    Serial.print("south:");
    Serial.println(South);

    Serial.print("West:");
    Serial.println(West);

    Serial.println("");

    Serial.print("NorthSouth:");
    Serial.println(NorthSouth);

    Serial.print("SouthEast:");
    Serial.println(SouthEast);

    Serial.print("EastWest:");
    Serial.println(EastWest);

    Serial.print("NorthWest:");
    Serial.println(NorthWest);

    Serial.println("");
    Serial.println("");
    
    North = -1;
    South = -1;
    East = -1;
    West = -1;

    NorthSouth = -1; 
    SouthEast  = -1;
    EastWest   = -1;
    NorthWest  = -1;
  
  }else{

  }
}

void loop() {
  if (IS_OK(lidar.waitPoint())) {
    float distance = lidar.getCurrentPoint().distance; //distance value in mm unit
    float angle    = lidar.getCurrentPoint().angle; //anglue value in degree
    bool  startBit = lidar.getCurrentPoint().startBit; //whether this point is belong to a new scan
    byte  quality  = lidar.getCurrentPoint().quality; //quality of the current measurement

  
  

   if(angle >= 358.0 || angle <= 2.0 && quality > 10){
      North = distance;
      
   }else if(angle >= 88.0 && angle <= 92.0 && quality > 10){
      East = distance;
      
   }else if(angle >= 178.0 && angle <= 182.0 && quality > 10){
      South = distance;
      
   }else if(angle >= 268.0 && angle <= 272.0 && quality > 10){
      West = distance;
      
   }else if(angle >= 43.0 && angle <= 47.0 && quality > 10){
      NorthSouth = distance;
      
   }else if(angle >= 133.0 && angle <= 137.0 && quality > 10){
      SouthEast = distance;
      
   }else if(angle >= 223.0 && angle <= 227.0 && quality > 10){
      EastWest = distance;
      
   }else if(angle >= 313.0 && angle <= 317.0 && quality > 10){
      NorthWest = distance;
      
   }
    pushData();

    
  } else {
    analogWrite(RPLIDAR_MOTOR, 255); //stop the rplidar motor
    
    // try to detect RPLIDAR... 
    rplidar_response_device_info_t info;
    Serial.print("Wait: ");
    Serial.print(IS_OK(lidar.waitPoint()));
    Serial.print(" : ");
    Serial.println(IS_OK(lidar.getDeviceInfo(info, 100)));
    if (IS_OK(lidar.getDeviceInfo(info, 100))) {
       // detected...
       lidar.startScan();
    
       // start motor rotating at max allowed speed
       analogWrite(RPLIDAR_MOTOR, 250);
       delay(1000);
    }
  }
}
