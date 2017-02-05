//  ------------------------------------------------------
// ----------             Movement             -----------
// ----------     Rescue Robot Code 2016       -----------
//  ---------                                  -----------
// ---------- Team: Rory W, Ines K & Joseph F  -----------
// ----------         Mentor:Alex C            -----------
// -------------------------------------------------------

//TODO: DEBUG LOG

#ifndef __MOVEMENT
#define __MOVEMENT

#include "pinout.h"
#include "lidar.h"
#include "debug_log.h"
#include "sensors.h"


#define wallAhead 130.0 //distance ahead when facing a wall 
#define wallThreshold 40.0 // wall distance give
#define tileLength 320.0 // how far the robot needs to move !! BE CAREFULL CHANGING THIS AS IT EFFECTS ALL TILE MOVEMENT !!


//-------------------------------------
//---------     moveMotor()   ----------
//-------------------------------------

void moveMotor(int motor, int dir, int spd) {
  int i = 1;

  // try 3 times then give up
  while ((Dynamixel.turn(motor, dir, spd) == -1) && (i <= 3)) {
    Dynamixel.turn(motor, dir, spd);
    log(VERBOSE, "MOTOR %d ERROR #%d", motor, i);
    i++;
  }
}

//-------------------------------------
//---------   moveForward()  ----------
//-------------------------------------

void moveForward(int front, int back, int left, int right) {

  moveMotor(FMotor, RIGTH, front);
  moveMotor(BMotor, LEFT, back);
  moveMotor(LMotor, RIGTH, left);
  moveMotor(RMotor, LEFT, right);
}

//-------------------------------------
//---------     moveLeft()   ----------
//-------------------------------------

void moveLeft(int left, int right) {

  moveMotor(FMotor, RIGTH, 0);
  moveMotor(BMotor, RIGTH, 0);

  moveMotor(LMotor, LEFT, left);
  moveMotor(RMotor, LEFT, right);

}

//-------------------------------------
//---------   moveRight()   ----------
//-------------------------------------

void moveRight(int left, int right) {

  moveMotor(FMotor, RIGTH, 0);
  moveMotor(BMotor, LEFT, 0);

  moveMotor(LMotor, RIGTH, left);
  moveMotor(RMotor, RIGTH, right);

}

//-------------------------------------
//--------- moveBackwards()  ----------
//-------------------------------------

void moveBackward(int front, int back, int left, int right) {

  moveMotor(FMotor, LEFT, front);
  moveMotor(BMotor, RIGTH, back);
  moveMotor(LMotor, LEFT, left);
  moveMotor(RMotor, RIGTH, right);

}

//-------------------------------------
//---------   stopMotors()   ----------
//-------------------------------------

void stopMotors() {

  moveMotor(FMotor, RIGTH, 0);
  moveMotor(BMotor, RIGTH, 0);
  moveMotor(LMotor, RIGTH, 0);
  moveMotor(RMotor, RIGTH, 0);

}

//-------------------------------------
//---------   TurnRobot()    ----------
//-------------------------------------

void turnRobot(int direction) {
  log(ERROR, "TURN FUNCTION ENTERED");
  log(INFO, "Direction: %d", direction);

#define turnThreshold 1
#define speedMark1 20.0
#define speedMark2 40.0

int turnTimer = 0;

  
  switch (direction) {
    case LEFT:
      currentDirection = (currentDirection+3)%4; break;
      
    case RIGHT:
      currentDirection = (currentDirection+1)%4; break;
      
    case BACKWARDS:
      currentDirection += 2; break;
      
      case HEAT_TURN:
        log(ERROR, "Heat Turn");

        if(currentDirection % 10 == 0){
          currentDirection += 25;
          log(ERROR, "Heat Turn 1 Current %f" , currentDirection);
          
        }else{
          currentDirection += 15;
          log(ERROR, "Heat Turn 2 Current %f" , currentDirection);
          
        }
                            break;
    default:break;
  }
  
  //currentDirection = ((currentDirection + 40) % 40);
  log(ERROR, "Current Direction: %d", currentDirection);

  float targetAngle = currentDirection * 90;

  log(ERROR, "Target Angle: %f", targetAngle);

  updateAccel();
  switch (int(currentDirection)) {
    case 0:
      log(INFO, "CASE 0" );
      while ((accelX < (360.0 - turnThreshold) && accelX > turnThreshold) && digitalRead(pause_button) == HIGH && turnTimer < 50) {
        turnTimer++;
        updateAccel();

        log(INFO, "Accel: %f", accelX);

        if (accelX > 180) {
          log(DEBUG, "LESS THEN 180");
          if (accelX > 360 - speedMark1) {
            log(DEBUG, "Greater THEN 340");
            moveLeft(120, 120);
          } else if (accelX > 360 - speedMark2) {
            log(DEBUG, "LESS THEN 320");
            moveLeft(300, 300);
          } else {
            log(DEBUG, "ELSE ");
            moveLeft(600, 600);
          }
          log(DEBUG, "Moving LEFT");
        } else {
          if (accelX < speedMark1) {
            moveRight(120, 120);
          } else if (accelX < speedMark2) {
            moveRight(300, 300);
          } else {
            moveRight(600, 600);
          }
          log(DEBUG, "Moving RIGHT");
        }

      }

      break;
    default:
      log(INFO, "CASE > 0" );
      while (!(accelX < (targetAngle + turnThreshold) && accelX > (targetAngle - turnThreshold)) && digitalRead(pause_button) == HIGH && turnTimer < 50) {
        turnTimer++;
        updateAccel();
        log(INFO, "Accel: %f", accelX);

        if (accelX < targetAngle) {
          if (accelX > targetAngle - speedMark1) {
            moveLeft(120, 120);
          } else if (accelX > targetAngle - speedMark2) {
            moveLeft(300, 300);
          } else {
            moveLeft(600, 600);
          }
          log(DEBUG, "Moving LEFT");
        } else {
          if (accelX < targetAngle + speedMark1) {
            moveRight(120, 120);
          } else if (accelX < targetAngle + speedMark2) {
            moveRight(300, 300);
          } else {
            moveRight(600, 600);
          }
          log(DEBUG, "Moving RIGHT");
        }

      }

      break;
  }

  if(digitalRead(pause_button) == LOW){ pause = false;  }
  stopMotors();
  log(INFO, "Ending Accel Val: %f", accelX);
  while (digitalRead(pause_button) == LOW){
    delay(200);
  }
  
  Last_Lidar_Front = Last_Lidar_Back = Last_Lidar_Left = Last_Lidar_Right = Last_Lidar_Front_Left = Last_Lidar_Front_Right = Last_Lidar_Back_Right = Last_Lidar_Back_Left = 0;
}


//-------------------------------------
//--------- touchAvoid()----------
//-------------------------------------

void touchAvoid() {
  updateTouch();
  log(ERROR, "Front touch sensor value is: %d", touchF);
  if (touchF == LOW){
    moveBackward(100,100,100,100);
    log(ERROR, "Bumped wall, moving backwards");
    delay(400);
    stopMotors();
    log(ERROR, "Moved back from wall");
  }
  log(ERROR, "BUMP FUNCTION");
}

//-------------------------------------
//---------tileMoveFinished()----------
//-------------------------------------

void tileMoveFinished() {
  lidarRun(harshLoop);
  calculateTiles();
  
  flashLED(25);
  flashLED(50);
  
  log(WARN, "Lidar Tile 1 :%f", Lidar_Front);
  log(WARN, "Forward Value 1 :%f", Lidar_Front);
  
  if (Lidar_Front > tileLength - wallThreshold) { // MARK ------------------------
    if (Lidar_Front < (tileLength + wallAhead + wallThreshold)) {
      
      forwardTile = wallAhead + wallThreshold; // Only one tile ahead
      log(ERROR, "Less then one tile");

    } else {
      forwardTile = (Tile_Forwards * tileLength) - tileLength - wallAhead; // more then one tile ahead
      log(ERROR, "More then One tile");
    }

    moveTilefinished = true;

  } else {
    moveTilefinished = false; // No tiles Ahead
  }

  log(INFO, "Lidar Tile2:%f", Lidar_Front);
  log(INFO, "Forward Tile2:%f", forwardTile);
  
  updateTouch();
  
  if(touchF == LOW){
    moveBackward(300,300,300,300);
    delay(500);
    stopMotors();
  }
  
}

//-------------------------------------
//---------     moveTile()   ----------
//-------------------------------------

bool moveTile() {
  bool returnValue = false;
  updateTouch();
  if(!onRamp()){
    if(RampSeen){return false;}
    
    if (Lidar_Front <= forwardTile || ( Lidar_Front <= wallAhead && Lidar_Front > 0 ) || touchF == LOW) {
      log(ERROR, "Move Tile Turn Test");
      turnRobot(3);

      if(Lidar_Front <= (forwardTile - wallThreshold)){
        moveBackward(200,200,200,200);
        delay(200);
        stopMotors();
      }
      lidarRun(1000);
    }

    if ((Lidar_Front <= forwardTile) || ( Lidar_Front <= wallAhead && Lidar_Front != 0.0 ) || touchF == LOW) {
      if(touchF == LOW){
         moveBackward(100,100,100,100);
         log(WARN, "Bumped wall, moving backwards");
         delay(400);
         
        stopMotors();
      }
      
      returnValue = false;
      
      log(DEBUG, "A WALL INFRONT: %f . Wall Front Value : %f", Lidar_Front, forwardTile);
      
    } else { // Move forward
      log(DEBUG, " NO WALL INFRONT: %f . Wall Front Value: %f", Lidar_Front, forwardTile);
      
      returnValue = true;
  
    }
  
    if (Lidar_Front <= (forwardTile + 100.0)) {
      
      BASE_POWER = 150;
      MAX_POWER = 700;
      TileSide = true;
      
    } else if (Lidar_Front <= (forwardTile + 150.0)) {
      
      BASE_POWER = 300;
      MAX_POWER = 800;
      TileSide = true;
  
    }else if (Lidar_Front <= (forwardTile + 200.0)) {
      TileSide = true;
      BASE_POWER = 400;
      MAX_POWER = 900;
  
    } else {
      BASE_POWER = START_BASE_POWER;
      MAX_POWER = START_MAX_POWER;
      TileSide = false;
    }

    
  } else {
      log(WARN, "ROBOT ON RAMP Y:%f", accelY);
      BASE_POWER = START_BASE_POWER + 200;
      MAX_POWER = 1000;

      returnValue = true;
  }

  return returnValue;
}


#endif
