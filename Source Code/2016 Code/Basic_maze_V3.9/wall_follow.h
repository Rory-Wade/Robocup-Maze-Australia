//  ------------------------------------------------------
// ----------             Movement             -----------
// ----------     Rescue Robot Code 2016       -----------
//  ---------                                  -----------
// ---------- Team: Rory W, Ines K & Joseph F  -----------
// ----------         Mentor:Alex C            -----------
// -------------------------------------------------------

#ifndef __WALL_FOLLOW
#define __WALL_FOLLOW


#include "pinout.h"
#include "movement.h"
#include "lidar.h"
#include "debug_log.h"

// Ziegler-Nichols method of giving K' values (loop times considered to be dT)
// Kc = ~5-6 for this robot
// dT = ~0.25-0.3s
// Pc = ~5-6s to complete
// Kp = 0.6 Kc
// Ki = 2*Kp * dt / Pc (how long the oscillation is)
// Kd = Kp * Pc / (8 dT)

// PID values
#define KP 3.5 // reaction intensity
#define KI 0.45 // how slowly it will react
#define KD 0.5     // dampening of oscillations

// start with KP = KI = KD at 0
// LOOP
// modify KP until it reacts appropriately
// modify KI very slowly until it's dampened mostly
// modify KD very slowly until larger oscillations are dampened
// GOTO LOOP

float left_motor_power, right_motor_power;
float left_power = 0;
float right_power = 0;

float integral =   0;
float derivative = 0;
float proportion = 0;

float last_error = 0;

#define DIST_FROM_WALL 170       // threshold for a wall to actually be there
#define WALL_FOLLOW_DISTANCE 155  // when following a single wall (not both), will follow this far away

#define UP 0
#define DOWN 1

int in_range_type(float val){
    if(val >= 0 && val <= MAX_POWER){
        return val;
    }
    else if(val < 0){
      return 0;
    }
    else if(val < MAX_POWER){
      return 1000;
    }
  return 0;    
}

int in_range(float val){
    if(val >= 0 && val <= MAX_POWER)
        return 1;
    return 0;
}

void reset_error(){
    proportion = integral = derivative = last_error = 0; // reset errors
}


void PID(float left, float right){
    log(VERBOSE,"PID running...");

    if(last_error > 200){
      reset_error();
      turnRobot(3);
    }
    // calculate all the values
    proportion = right - left;
    log(INFO, "Proportional error: %f", proportion);
    integral  += proportion;
    derivative = proportion - last_error;
    last_error = proportion;

    // calculate the turn
    float turn = KP*proportion + KI*integral + KD*derivative;

    // calculate the motor powers
    left_motor_power  = BASE_POWER - turn;
    right_motor_power = BASE_POWER + turn;

    log(DEBUG, "Motor powers - Left:%f Right:%f || PID Values - Left:%d Right:%f",left_motor_power, right_motor_power, left, right);

    if (in_range(left_motor_power))
    {
      left_power = left_motor_power;
    }
    else
    {
      log(WARN,"Left motor power %f out of range", left_motor_power);
    }

    if (in_range(right_motor_power))
    {
      right_power = right_motor_power;
    }
    else
    {
      log(WARN,"Right motor power %f out of range", right_motor_power);
    }

    moveForward(right_power, left_power, left_power, right_power);

}

void FollowWalls(){
  log(VERBOSE,"Wall Follow");

  
  
  int left_Walls = 0;
  int right_Walls = 0;

  int left_Walls_Values = 0;
  int right_Walls_Values = 0;
 
  if(Lidar_Front_Left < DIST_FROM_WALL){//front left;
    left_Walls_Values += (cos((15 * 71) / 4068) * Lidar_Front_Left);
    left_Walls++;
  }
  if(Lidar_Left < DIST_FROM_WALL){//left
    left_Walls_Values +=  Lidar_Left;
    left_Walls++;
    
  }
  if(Lidar_Front_Right < DIST_FROM_WALL){//front right
    right_Walls_Values += (cos((15 * 71) / 4068) * Lidar_Front_Right);
    right_Walls++;
    
  }
  if(Lidar_Right < DIST_FROM_WALL){//right
    right_Walls_Values +=  Lidar_Right;
    right_Walls++;
    
  }


  log(DEBUG, "After Values - Left:%d Div:%d Right:%d Div: %d THEREFOR LEFT: %d Right %d",left_Walls_Values, left_Walls, right_Walls_Values, right_Walls,left_Walls_Values/left_Walls ,right_Walls_Values/right_Walls);

  if(right_Walls > 0 && left_Walls > 0){
    log(DEBUG,"BOTH WALL FOLLOW");
    //both wall follow
    PID(left_Walls_Values/left_Walls , right_Walls_Values/right_Walls);
    
  }else if(left_Walls > 0){ 
    log(DEBUG,"LEFT WALL(s) FOUND");
    //left wall
    PID(left_Walls_Values/left_Walls , WALL_FOLLOW_DISTANCE);
    
  }else if(right_Walls > 0){
    log(DEBUG,"RIGHT WALL(s) FOUND");
    //right wall
    PID(WALL_FOLLOW_DISTANCE , right_Walls_Values/right_Walls);
    
  }
  else{//no walls
    log(INFO,"NO WALLS DETECTED, GOING BASE SPEED");
    updateAccel();
    if(currentDirection == 0){
      if(accelX > 180){
        PID(360, accelX);
      }else{
        PID(0, accelX);
      }
    }else{
       PID(currentDirection * 90, accelX);
    }

      //PID(WALL_FOLLOW_DISTANCE , WALL_FOLLOW_DISTANCE);
  }
}


#endif

