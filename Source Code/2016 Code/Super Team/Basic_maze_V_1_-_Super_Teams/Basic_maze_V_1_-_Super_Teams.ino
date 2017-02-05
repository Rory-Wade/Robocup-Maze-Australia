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
    1. 9 tiles
    2. 
    
    

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
  setup_logging(DEBUG);
  log(ERROR, "VERSION V4.1");
  log(DEBUG, "Setup Void - RUNNGING\n");
  pinSetup();

  delay(100);
  
  digitalWrite(DATA_IN_LED, LOW);
  lidarRun(softLoop);

  digitalWrite(DATA_OUT_LED, LOW);
  flashLED(50);

  digitalWrite(SATUES_LED, LOW);
  
  updateAccel();
  updateLight();
  updateHeatThresh();
  printHeat();
  
  log(WARN, "Setup Void - DONE \n");
}

void loop() {
  
  log(VERBOSE, "loop");
  pauseButton();

  if (pause) { 
    if (moveTile()) {
      
      log(VERBOSE, "Lidar Run & PID Wall follow \n");
      
      touchAvoid();
      lidarRun(softLoop);
      
      touchAvoid();
      FollowWalls();
      
      touchAvoid();
      
    } else {

      log(INFO, "TILE Reached");
      
      stopMotors();
      
      lidarRun(harshLoop);
      clearBuffer();
      calculateTiles();

        if(SilverTileFound() ){
          sendData(LIGHT);
          waitForData(LIGHT);
        }

      
      if(BlackTileFound()){
          flashLED(50);
          sendData(LIGHT);
          //sendData(TILES);
        }
          
          sendData(TILES);
          waitForData(TILES);
          
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

          sendData(TILES);
          sendData(DIRECTION);
          waitForData(TILES);
       
          tileMoveFinished();
          reset_error();
          
    }else {
        delay(200);
        sendData(PAUSE);
    }

  }
}


