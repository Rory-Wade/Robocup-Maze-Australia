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


// TODO ------------------------------------------- TODO
//ADD ACCEL smarts to turning
// WORK OUT THE SITUATION WHEN ALL FOUR SIDES ARE EQUAL TILES


#include "pinout.h"
#include "lidar.h"
#include "debug_log.h"
#include "sensors.h"


#define wallAhead 150.0 //distance ahead when facing a wall 
#define wallThreshold 40.0 // wall distance give
#define tileLength 300.0 // how far the robot needs to move !! BE CAREFULL CHANGING THIS AS IT EFFECTS ALL TILE MOVEMENT !!



//-------------------------------------
//---------tileMoveFinished()----------
//-------------------------------------

void tileMoveFinished(){
  lidarRun();
  calculateTiles();
  
 log(WARN, "Forward Value:%f",Lidar_Front);
  if(Lidar_Front > tileLength){
    if(Lidar_Front < (tileLength + wallAhead + wallThreshold)){
      forwardTile = wallAhead; // Only one tile ahead
      log(WARN, "Less then one tile");
      
    }else{
      forwardTile = (Tile_Forwards * tileLength) - tileLength - wallAhead; // more then one tile ahead
      log(WARN, "More then One tile");
    }
    
    moveTilefinished = true;
    
  }else{
    moveTilefinished = false; // No tiles Ahead
  }
  
  log(INFO, "Forward Tile:%f",forwardTile);
  delay(1000);
}


//-------------------------------------
//---------     moveTile()   ----------
//-------------------------------------

bool moveTile(){
  bool returnValue = false; 
  
  if(Lidar_Front <= forwardTile && Lidar_Front >= (forwardTile - wallThreshold)){
      returnValue = false;
      log(DEBUG, "2 WALL INFRONT: %f . Wall Front Value : %f", Lidar_Front, forwardTile);
    }else{
      log(DEBUG, " NO WALL INFRONT: %f . Wall Front Value: %f", Lidar_Front, forwardTile);
      returnValue = true;
      
    }

    if(Lidar_Front <= (forwardTile + 50.0)){
      BASE_POWER = 100;
      MAX_POWER = 700;
    }else if(Lidar_Front <= (forwardTile + 100.0)){
      BASE_POWER = 200;
      MAX_POWER = 900;
      
    }else{
      BASE_POWER = START_BASE_POWER;
      MAX_POWER = START_MAX_POWER;
    }
 
  return returnValue;
}

//-------------------------------------
//---------     moveMotor()   ----------
//-------------------------------------

  void moveMotor(int motor,int dir,int spd){
  int i = 1;
  
  while((Dynamixel.turn(motor,dir,spd) == -1) && (i<=2)){
    Dynamixel.turn(motor,dir,spd);
    log(DEBUG,"MOTOR %d ERROR #%d",motor,i);
    i++;
  }

}

//-------------------------------------
//---------   moveForward()  ----------
//-------------------------------------
 
  void moveForward(int front,int back, int left, int right){
    
    moveMotor(FMotor,RIGTH,front);
    moveMotor(BMotor,LEFT,back);
    moveMotor(LMotor,RIGTH,left);
    moveMotor(RMotor,LEFT,right);
}

//-------------------------------------
//---------   moveForward()  ----------
//-------------------------------------
 
  void moveAllForward(int speed){
    
    moveMotor(FMotor,RIGTH,speed);
    moveMotor(BMotor,LEFT,speed);
    moveMotor(LMotor,RIGTH,speed);
    moveMotor(RMotor,LEFT,speed);
}
//-------------------------------------
//---------     moveLeft()   ----------
//-------------------------------------

  void moveLeft(int left, int right){ 

    moveMotor(FMotor,RIGTH,0);
    moveMotor(BMotor,RIGTH,0);
    
    moveMotor(LMotor,LEFT,left);
    moveMotor(RMotor,LEFT,right);

}

//-------------------------------------
//---------   moveRightt()   ----------
//-------------------------------------

  void moveRight(int left, int right){ 
    
    moveMotor(FMotor,RIGTH,0);
    moveMotor(BMotor,LEFT,0);
    
    moveMotor(LMotor,RIGTH,left);
    moveMotor(RMotor,RIGTH,right);
    
}

//-------------------------------------
//--------- moveBackwards()  ----------
//-------------------------------------

  void moveBackward(int front,int back, int left, int right){

    moveMotor(FMotor,LEFT,front);
    moveMotor(BMotor,RIGTH,back);
    moveMotor(LMotor,LEFT,left);
    moveMotor(RMotor,RIGTH,right);
       
}

//-------------------------------------
//---------   stopMotors()   ----------
//-------------------------------------

  void stopMotors(){

    moveMotor(FMotor,RIGTH,0);
    moveMotor(BMotor,RIGTH,0);
    moveMotor(LMotor,RIGTH,0);
    moveMotor(RMotor,RIGTH,0);
       
}

//-------------------------------------
//---------   TurnRobot()    ----------
//-------------------------------------

 void turnRobot(int direction){
  log(INFO,"TURN FUNCTION ENTERED"); 
  log(INFO,"Direction: %d", direction); 

  #define turnThreshold 1
  #define speedMark1 20.0
  #define speedMark2 40.0
  
  switch(direction){
      case LEFT: 

      currentDirection--;

                    break; 
      case RIGHT:   

      currentDirection++;

                    break;
      case BACKWARDS:   

      currentDirection += 2;

                    break;
      default:      

        return;

      break; 
   }
    log(INFO,"Current Direction 1 : %d",currentDirection);
   currentDirection += 4;
   log(INFO,"Current Direction 2 : %d",currentDirection);
   currentDirection = currentDirection % 4;
    log(INFO,"Current Direction 3 : %d",currentDirection);
    
   float targetAngle = currentDirection * 90.0;
   
    log(INFO,"Target Angle: %f",targetAngle);
    
   updateAccel();
   switch(currentDirection){
      case 0: 
      log(ERROR, "CASE 0" );
        while((accelX < (360.0 - turnThreshold) && accelX > turnThreshold)){
        updateAccel();
         log(INFO,"Accel: %f",accelX);
         
        if(accelX > 180){
            log(ERROR, "LESS THEN 180");
            if(accelX > 360 - speedMark1){
              log(ERROR, "Greater THEN 340");
              moveLeft(90,90);
            }else if(accelX > 360 - speedMark2){
              log(ERROR, "LESS THEN 320");
              moveLeft(200,200);
            }else{
              log(ERROR, "ELSE ");
              moveLeft(600,600);
            }
          log(INFO,"Moving LEFT");
        }else{
           if(accelX < speedMark1){
              moveRight(90,90);
            }else if(accelX < speedMark2){
              moveRight(200,200);
            }else{
              moveRight(600,600);
            }
          log(INFO,"Moving RIGHT");
        }

      } 

                    break; 
      
      default:  
        log(ERROR, "CASE > 0" );
        while(!(accelX < (targetAngle + turnThreshold) && accelX > (targetAngle - turnThreshold)) ){
        updateAccel();
         log(INFO,"Accel: %f",accelX);
         
        if(accelX < targetAngle){
            if(accelX > targetAngle - speedMark1){
              moveLeft(90,90);
            }else if(accelX > targetAngle - speedMark2){
              moveLeft(200,200);
            }else{
              moveLeft(600,600);
            }
          log(INFO,"Moving LEFT");
        }else{
           if(accelX < targetAngle + speedMark1){
              moveRight(90,90);
            }else if(accelX < targetAngle + speedMark2){
              moveRight(200,200);
            }else{
              moveRight(600,600);
            }
          log(INFO,"Moving RIGHT");
        }

      }    

                    break; 
   }

  stopMotors();
  log(INFO,"Ending Accel Val: %f",accelX);
}

 
//-------------------------------------
//--------- fixTilePostion()----------
//-------------------------------------

  void fixTilePostion(){
    //log(ERROR, "FIXED TILE POS");
    calculateTiles();
    if(Lidar_Front > (Tile_Forwards * tileLength + (wallAhead + wallThreshold)) && Lidar_Front < (Tile_Forwards * tileLength + (wallAhead - wallThreshold)) ){
      log(ERROR, "FIXED TILE POS FIXING");
//    while(Lidar_Front > (Tile_Forwards * tileLength + (wallAhead + wallThreshold)) && Lidar_Front < (Tile_Forwards * tileLength + (wallAhead - wallThreshold)) ){
//      //moveBackward(100,100,100,100);
//    }
    //stopMotors();
  }else{
      
    }

  }



  #endif
