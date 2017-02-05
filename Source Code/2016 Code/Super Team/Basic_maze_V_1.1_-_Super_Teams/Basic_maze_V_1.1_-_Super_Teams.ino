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

int traceArrayIndexCountingCounter = 0;

int startDelay = 3000;

int pathDirections[100];
int realDirection = 0;

void setup() {

  initTraceArray();
  delay(startDelay);
  setup_logging(ERROR);
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

  log(WARN, "Setup Void - DONE \n");

  float lidarStartingLeft  = Lidar_Left;
  float lidarStartingRight = Lidar_Right;

  readData();
  log(ERROR,"DATA RECIEVED FROM TEENSY");
  
    lidarRun(harshLoop);

  log(ERROR,"LIDAR HARSH LOOP COMPLETE");
  //Figure out which side the rescue robot is on, then do shit.
  if (Lidar_Left < lidarStartingLeft - 50.0) {
    //The rescue bot is on the left
    pathDirections[0] = 0;
    pathDirections[0] = 3;
  } else if (Lidar_Right < lidarStartingRight - 50.0){
    //the rescue bot is on the right
    pathDirections[0] = 0;
    pathDirections[1] = 1;

  }else{
    
    log(ERROR,"Could not determine robot position.");
  }

  log(ERROR,"ROBOT SPOTTED");
  
  for (int i = 2; traceArray[i][0] != 255; i++) {
      pathDirections[i] = returnDirectionFromDualCoordinates(traceArray[i][0], traceArray[i][1], traceArray[i+1][0], traceArray[i+1][1]);
  }

  log(ERROR,"ARRAY SORTED");
  // Map data
  //quality check

  
}

void loop() {

  /*
    Make an array of two values (the Lidar values for either side), and check that every loop while the robot hasn't moved.
    If this changes from a two to a one, then the victim robot has arrived.
    Go one square forward and if the victim robot is on the right, turn to the left and go one square forward then turn to the right and don't move.
    Otherwise go one square forward, turn to the right and go another square forward. Now go left again.
    Set the current direction to 0 (it should already be at 0).
    Now calculate the directions to go every tile from the array that is from the bluetooth.
    Do this by checking if Y1 > Y2, direction 2, if Y1 < Y2, direction 0, etcetera.
    Now add two to the direction, (because the robots map will be 180 degrees flipped from the other) and modulo 4, then add the current facing direction, and once again modulo 4 in order to find the relative direction, then turn and go that direction.
    Finally, if you've reached the end of the array, turn the direction that the lidar reads a two value.
    It must be a turn 1 or 3. Otherwise it's all a lie and you should just abort because the stuff has messed up a bit.



    int pastArray [3][255] = getBluetoothData(); //(is probably just a serial3.read()). This function should split the thing into an array and send it back too.


  */

  log(VERBOSE, "loop");
  pauseButton();

  if (!pause) {
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

      for(int i = 0; i < 5; i++){
        log(ERROR,"%d",traceArray[i][0]);
      }
      for(int z=0; z<6; z++){
        Serial.print("path direction  ");
        Serial.println(pathDirections[z]);
        }
      log(ERROR, "SUGGESTED DIRECTION MODULO Values: %d : %d",(((int)(pathDirections[traceArrayIndexCountingCounter]) , currentDirection % 4));
      log(ERROR, "SUGGESTED DIRECTION MODULO IS: %d",(((int)(pathDirections[traceArrayIndexCountingCounter]) - (int)realDirection) % 4));

      int turnDirection = abs(((int)(pathDirections[traceArrayIndexCountingCounter]) - realDirection) % 4);
      switch(turnDirection){
          case -1:
            turnDirection = 3;
          break;
          case -3:
            turnDirection = 1;
          break;
          case -2:
            turnDirection = 2;
          break;
        
        }
      
      switch(turnDirection){
        case 1:
          turnRobot(RIGHT);
          realDirection = (realDirection+1)%4;
        break;
        case 2:
          //FOLLOW THE WALL. Something went wrong
        break;
        case 3:
          turnRobot(LEFT);
          realDirection = (realDirection+3)%4;
        break;
      }
      
      traceArrayIndexCountingCounter++;

      lidarRun(harshLoop);
      clearBuffer();
      calculateTiles();

      if (SilverTileFound() ) {
        sendData(LIGHT);
        waitForData(LIGHT);
      }

      log(ERROR,"THE CURRENT DIRECTION SUGGESTED IS %d and the counter is at %d",pathDirections[traceArrayIndexCountingCounter],traceArrayIndexCountingCounter);
      
      if (BlackTileFound()) {
        flashLED(50);
        sendData(LIGHT);
        //sendData(TILES);
      }

      //sendData(TILES);
      //waitForData(TILES);

      tileMoveFinished();
      TileSide = false;

    }
  }
  else {

    log(VERBOSE, "Robot Paused");

    digitalWrite(RPLIDAR_MOTOR, LOW);
    digitalWrite(LightSensorLED, LOW);

    updateTouch();

    if (touchFL == LOW && touchFR == LOW) {

      flashLED(25);
      resetIMU();
      flashLED(50);
    }
  }
}

void initTraceArray() {
  for (int x = 0; x < 255; x++) {
    for (int y = 0; y < 3; y++) {
      traceArray[x][y] = 255;
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

    } else {
      delay(200);
      sendData(PAUSE);
    }

  }
}

int returnDirectionFromDualCoordinates(int x1,int  y1,int x2,int y2) {
  if (x1 < x2) {
    return 1;
  } else if (x1 > x2) {
    return 3;
  } else if (y1 < y2) {
    return 0;
  } else {
    return 2;
  }
}
//
////begin looping through the array of thingos
//for (int i = 255; i > -1; i--) {
//  if (pastArray[i][0] != null) {
//    if (pastArray[i + 1][0] != null) {
//      int x1 = (int)(pastArray[i + 1][0]);
//      int y1 = (int)(pastArray[i + 1][1]);
//      int x2 = (int)(pastArray[i][0]);
//      int y2 = (int)(pastArray[i][1]);
//
//      int absoluteDirectionToGo = returnDirectionFromDualCoordinates(x1, y1, x2, y2);
//      int relativeDirection = absoluteDirectionToGo + currentFacingDirection % 4;
//      turn(relativeDirection * 10);
//      moveTile();
//    }
//  }
//}


