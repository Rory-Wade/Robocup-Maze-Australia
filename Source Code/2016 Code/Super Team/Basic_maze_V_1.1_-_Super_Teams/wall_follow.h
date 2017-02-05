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
#define KD 4.5     // dampening of oscillations

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
#define WALL_FOLLOW_DISTANCE 210  // when following a single wall (not both), will follow this far away
#define WALL_FOLLOW_STRENGTH 5 //Strength of lidar wall follow

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


void PID(float right, float left){
    log(VERBOSE,"PID running...");

    if(last_error > 100 || last_error < -100){
      turnRobot(3);
      last_error = 1;
    }

    
    // calculate all the values
    proportion = right - left;
    log(INFO, "Proportional error: %f", proportion);
    integral  += proportion;
    derivative = proportion - last_error;
    last_error = proportion;

    // calculate the turn
    float turn = KP*proportion + KI*integral + KD*derivative;



//wall turn 
    /*if(Lidar_Front_Right < WALL_FOLLOW_DISTANCE){
      turn -= 100;
    }
    if(Lidar_Front_Left < WALL_FOLLOW_DISTANCE){
      turn += 100;
    }*/
    int wallsCounter = 0;

    float turnDifference = 0;
    
    if(Lidar_Front_Right < WALL_FOLLOW_DISTANCE && Lidar_Back_Right < WALL_FOLLOW_DISTANCE){
      wallsCounter++;
      turnDifference -= (Lidar_Back_Right - Lidar_Front_Right) * WALL_FOLLOW_STRENGTH;
    }

    if(Lidar_Front_Left < WALL_FOLLOW_DISTANCE && Lidar_Back_Left < WALL_FOLLOW_DISTANCE){
      wallsCounter++;
      turnDifference += (Lidar_Back_Left - Lidar_Front_Left) * WALL_FOLLOW_STRENGTH;
    }

    //Correct if more on one side than the other
    if(Lidar_Left < WALL_FOLLOW_DISTANCE && Lidar_Right < WALL_FOLLOW_DISTANCE){
      turn -= (Lidar_Left - Lidar_Right) * WALL_FOLLOW_STRENGTH;
    }
    if(wallsCounter == 2){
      turn += (turnDifference / 2);
    }else{
      turn += turnDifference;
    }
    
    
    // calculate the motor powers
    left_motor_power  = BASE_POWER - turn;
    right_motor_power = BASE_POWER + turn;

    log(DEBUG, "Motor powers - Left:%f Right:%f || PID Values - Left:%d Right:%f",left_motor_power, right_motor_power, left, right);



//motors
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
}



#endif

