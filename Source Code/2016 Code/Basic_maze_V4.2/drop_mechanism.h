//  ------------------------------------------------------
// ----------         Drop Mechanism           -----------
//  ------------------------------------------------------
// ----------  Rescue robot code 2015          -----------
// ----------  Team: Rory Wade and Ines Kusen  -----------
// ----------          Mentor:AleX C           -----------
// -------------------------------------------------------
 
 
#ifndef __DROP_MECH
#define __DROP_MECH

#include "pinout.h"

#define SERVO_DELAY 300
 
#define LEFT_LOAD_POSITION  65
#define RIGHT_LOAD_POSITION 55
#define LEFT_DROP_POSITION  LEFT_LOAD_POSITION - 35
#define RIGHT_DROP_POSITION LEFT_LOAD_POSITION - 35
#define LEFT_WIGGLE_1       LEFT_LOAD_POSITION + 4
#define LEFT_WIGGLE_2       LEFT_LOAD_POSITION - 4
#define RIGHT_WIGGLE_1      RIGHT_LOAD_POSITION + 4
#define RIGHT_WIGGLE_2      RIGHT_LOAD_POSITION - 4
 
#define LEFT_SIDE 0
#define RPMotor 1
#define INITIAL_COUNT 12 // how many markers each side starts with
 
int left_ammo = INITIAL_COUNT;
int right_ammo = INITIAL_COUNT;

#define LEFT_SERVO 6


PWMServo left_side;
 
void servoSetup(){
    
  left_side.attach(LEFT_SERVO);
  left_side.write(LEFT_LOAD_POSITION);


}

void drop(){

 if(left_ammo > 0){
          left_side.write(LEFT_LOAD_POSITION);
          delay(SERVO_DELAY);
          left_side.write(LEFT_WIGGLE_1);
          delay(SERVO_DELAY);
          left_side.write(LEFT_WIGGLE_2);
          delay(SERVO_DELAY);
          left_side.write(LEFT_DROP_POSITION);
          delay(SERVO_DELAY);
          left_side.write(LEFT_LOAD_POSITION);
          delay(SERVO_DELAY);
          left_ammo--;
          
  }

}
#endif

