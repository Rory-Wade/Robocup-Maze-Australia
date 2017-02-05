//  ------------------------------------------------------
// ----------            Main Loop             -----------
// ----------     Rescue Robot Code 2016       -----------
// ----------                                  -----------
// ---------- Team: Rory W, Ines K & Joseph F  -----------
// ----------         Mentor:Alex C            -----------
// -------------------------------------------------------

// HardWare: Teensy 3.2

/* 

  Thing to achieve!
    3. MARK code added to tile movement 

*/

#include <Wire.h>
#include <PWMServo.h>

#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include "Adafruit_TCS34725.h"

#include "pinout.h"
#include "lidar.h"
#include "movement.h"
#include "sensors.h"

#include "communication.h"
#include "debug_log.h"
#include "wall_follow.h"
#include "heat.h"
#include "drop_mechanism.h"

int startDelay = 3000;

void setup() {
  delay(startDelay); 
  setup_logging(INFO);
  log(ERROR, "VERSION V4.1");
  log(DEBUG, "Setup Void - RUNNGING");
  pinSetup();

  delay(100);
  
  digitalWrite(DATA_IN_LED, LOW);
  lidarRun(softLoop);

  digitalWrite(DATA_OUT_LED, LOW);
  flashLED(50);


  while (digitalRead(pause_button) == HIGH){
    updateTouch();
    
    if(touchFL == LOW && touchFR == LOW){
      
      flashLED(25);
      resetIMU();
      flashLED(50);
   } 
  }
  lidarRun(softLoop);
  
  float lidarStartingLeft  = Lidar_Left;
  float lidarStartingRight = Lidar_Right;

  delay(1000);
  
  digitalWrite(SATUES_LED, LOW);
  log(WARN, "ACCEL Void - DONE ");
  updateAccel();
  log(WARN, "LIGHT Void - DONE ");
  updateLight();
  log(WARN, "HEAT THRESH Void - DONE ");
  updateHeatThresh();
  log(WARN, "PRINT HEAT - DONE ");
  printHeat();
  log(WARN, "Setup Void - DONE \n");

  while(Lidar_Left > lidarStartingLeft - 50 && Lidar_Right > lidarStartingRight - 50){
  
    flashLED(10);
    lidarRun(softLoop);
    
  }
    delay(2000);
    sendData(TILES);
    waitForData(TILES); 
    tileMoveFinished();
  
}

void loop() {
  
  log(VERBOSE, "loop");
  pauseButton();

  if (!pause) { 
    if (moveTile()) {
      
      log(VERBOSE, "Lidar Run & PID Wall follow \n");
      
      touchAvoid();
      lidarRun(softLoop);
      
      FollowWalls();

    } else {

      log(INFO, "TILE Reached");
      
      stopMotors();
      
      lidarRun(harshLoop);
      clearBuffer();
      calculateTiles();
      
      if(BlackTileFound()){
          flashLED(50);
          while(1);
          //sendData(TILES); 
        }
          
          sendData(DIRECTION);
          sendData(TILES);
          waitForData(TILES);
           
      log(INFO, "Reseting Tile Data For Next Movement\n");

      tileMoveFinished();
      TileSide = false;
      
    }
  }
  else {

    log(VERBOSE, "Robot Paused");
    digitalWrite(RPLIDAR_MOTOR,LOW); 
    digitalWrite(LightSensorLED, LOW);

    updateTouch();
    
    if(touchFL == LOW && touchFR == LOW){
      
      flashLED(25);
      resetIMU();
      flashLED(50);
   } 
   
   log(DEBUG, "Heat Seen: %d" , testHeat());
   
  
  }
}


//-------------------------------------
//---------   Pause Button   ----------
//-------------------------------------

void pauseButton() {

  if (digitalRead(pause_button) == LOW) {
    log(INFO, "Pause button pressed");
    pause = !pause;

    stopMotors();

    while (digitalRead(pause_button) == LOW) {}
    
    log(INFO, "Pause button released"); //Rory is a ...something if(angry == yes){serial.println("Go fuck yourself");}

    if (pause) {
      digitalWrite(LightSensorLED, HIGH);
      lidarRun(harshLoop);
      calculateTiles();

      log(DEBUG, "Sending Tile Data");

      if(SilverTileFound() ){
          sendData(LIGHT);
          waitForData(LIGHT);
        }
      
      if(BlackTileFound()){
          sendData(LIGHT);
          sendData(DIRECTION);
          sendData(TILES);
          
          moveBackward(200,200,200,200);
          delay(1000);
          turnRobot(BACKWARDS);
          
        }else{
          sendData(TILES);
          sendData(DIRECTION);
          waitForData(TILES);
        }

      tileMoveFinished();
      reset_error();
      
    }else {
        delay(200);
        sendData(PAUSE);
    }

  }
}


