//#include "debug_logging.h"
#include <PWMServo.h>
 
#define SERVO_DELAY 200
 int led = 13;
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
#define INITIAL_COUNT 12 // how many markers each side starts with
 
int left_ammo = INITIAL_COUNT;
int right_ammo = INITIAL_COUNT;

#define LEFT_SERVO 6
#define RIGHT_SERVO 5

PWMServo left_side, right_side;
 
void setup(){
    pinMode(led, OUTPUT);    
  left_side.attach(LEFT_SERVO);
  right_side.attach(RIGHT_SERVO);
  left_side.write(LEFT_LOAD_POSITION);
  right_side.write(RIGHT_LOAD_POSITION);
}

void loop(){
  drop(LEFT_SIDE);
    digitalWrite(led, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(1000);               // wait for a second
  digitalWrite(led, LOW);    // turn the LED off by making the voltage LOW
  delay(1000); 
}
void drop(int side){
  switch(side){
    case LEFT_SIDE:
            
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
                
            }
      break;
    case RIGHT_SIDE:
            
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
               
            }
      break;
  }
}
 
