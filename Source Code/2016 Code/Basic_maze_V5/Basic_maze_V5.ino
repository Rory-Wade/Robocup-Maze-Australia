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
    1. Wall too close move backwards unless wall behind

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
  setup_logging(WARN);
  log(ERROR, "VERSION V5.01");
  log(DEBUG, "Setup Void - RUNNGING");
  pinSetup();

  delay(100);
  
  digitalWrite(DATA_IN_LED, LOW);
  lidarRun(softLoop);

  digitalWrite(DATA_OUT_LED, LOW);
  flashLED(50);

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
      
      log(DEBUG, "Heat Seen: %d" , testHeat());
      
      if(testHeat()){
        stopMotors();
        flashLED(500);
        
        sendData(HEAT);
        waitForData(HEAT);
      }

      log(VERBOSE, "IMU Updated");
      RampSeen = onRamp();
      
      



    } else {

      log(INFO, "TILE Reached");
      
      stopMotors();
      
      lidarRun(harshLoop);
      clearBuffer();
      calculateTiles();

      if(testHeat()){
        stopMotors();
        flashLED(500);
        
        sendData(HEAT);
        waitForData(HEAT);
      }
      
      if(HeatSeenRight || HeatSeenLeft){
        HeatSeenRight = HeatSeenLeft = false;
      }

      
      log(INFO, "Ramp Seen: %d" , onRamp());

       
      if(RampSeen){
 
        sendData(ACCEL);
        waitForData(ACCEL);

        RampSeen = RampUp = RampDown = false;
        
      }  

        log(INFO, "Silver Seen: %d" , SilverTileFound());
        log(INFO, "Black Seen: %d" , BlackTileFound());

        
        if(SilverTileFound() ){
          sendData(LIGHT);
          waitForData(LIGHT);
        }

      
      if(BlackTileFound()){
          flashLED(50);
          sendData(LIGHT);
          //sendData(TILES);
          
          moveBackward(400,400,400,400);
          delay(2500);

          turnRobot(BACKWARDS);
          
        }
          
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

