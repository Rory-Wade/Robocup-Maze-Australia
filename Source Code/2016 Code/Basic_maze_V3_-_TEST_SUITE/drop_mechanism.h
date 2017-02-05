//  ------------------------------------------------------
// ----------         Drop Mechanism           -----------
//  ------------------------------------------------------
// ----------  Rescue robot code 2015          -----------
// ----------  Team: Rory Wade and Ines Kusen  -----------
// ----------          Mentor:AleX C           -----------
// -------------------------------------------------------
 
 
#ifndef __DROP_MECH
#define __DROP_MECH
 
//#include "debug_logging.h"
 
#define SERVO_DELAY 200
 
#define LEFT_LOAD_POSITION  65
#define RIGHT_LOAD_POSITION 55
#define LEFT_DROP_POSITION  LEFT_LOAD_POSITION - 35
#define RIGHT_DROP_POSITION LEFT_LOAD_POSITION - 35
#define LEFT_WIGGLE_1       LEFT_LOAD_POSITION + 4
#define LEFT_WIGGLE_2       LEFT_LOAD_POSITION - 4
#define RIGHT_WIGGLE_1      RIGHT_LOAD_POSITION + 4
#define RIGHT_WIGGLE_2      RIGHT_LOAD_POSITION - 4
 
#define LEFT_SIDE 0
#define RIGHT_SIDE 1
#define INITIAL_COUNT 5 // how many markers each side starts with
 
int left_ammo = INITIAL_COUNT;
int right_ammo = INITIAL_COUNT;
 
Servo left_side, right_side;
 
void servo_setup(){
    log(DEBUG,"Attaching servo pins...\n");
  left_side.attach(LEFT_SERVO);
  right_side.attach(RIGHT_SERVO);
  left_side.write(LEFT_LOAD_POSITION);
  right_side.write(RIGHT_LOAD_POSITION);
}
 
void drop(int side){
  switch(side){
    case LEFT_SIDE:
            log(INFO,"Drop marker on left side\n");
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
            } else {
                log(ERROR,"Out of markers on LHS\n");
            }
      break;
    case RIGHT_SIDE:
            log(INFO,"Drop marker on RHS\n");
            if(right_ammo > 0){
          right_side.write(RIGHT_LOAD_POSITION);
          delay(SERVO_DELAY);
          right_side.write(RIGHT_WIGGLE_1);
          delay(SERVO_DELAY);
          right_side.write(RIGHT_WIGGLE_2);
          delay(SERVO_DELAY);
          right_side.write(RIGHT_DROP_POSITION);
          delay(SERVO_DELAY);
          right_side.write(RIGHT_LOAD_POSITION);
          delay(SERVO_DELAY);
          right_ammo--;
            } else {
                log(ERROR,"Out of markers on RHS\n");
            }
      break;
  }
}
 
 
#endif
