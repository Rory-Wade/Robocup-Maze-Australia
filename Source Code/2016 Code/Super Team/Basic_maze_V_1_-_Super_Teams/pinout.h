//  ------------------------------------------------------
// ----------              Pinout              -----------
// ----------     Rescue Robot Code 2016       -----------
//  ---------                                  -----------
// ---------- Team: Rory W, Ines K & Joseph F  -----------
// ----------         Mentor:Alex C            -----------
// -------------------------------------------------------

#ifndef __PINOUT
#define __PINOUT

#include "debug_log.h"
#include "drop_mechanism.h"
#include <Arduino.h>

#include <DynamixelSerial2.h>
#include <RPLidar.h>
RPLidar lidar;

//-------------------------------------
//---------   Light Sensor   ----------
//-------------------------------------

#define LightSensorLED 13
#define BlackValue 100
#define SilverValue 500
#define colourThresh 100

Adafruit_TCS34725 tcs = Adafruit_TCS34725(TCS34725_INTEGRATIONTIME_700MS, TCS34725_GAIN_1X);


//-------------------------------------
//---------   BNO055 ACCEL   ----------
//-------------------------------------

#define BNO055_SAMPLERATE_DELAY_MS (30)
Adafruit_BNO055 bno = Adafruit_BNO055();

#define rampYValue 8.00
#define AccelReset 29
bool RampSeen = false;
bool RampUp = false;
bool RampDown = false;

float accelX = 0;
float accelY = 0;
float accelZ = 0;

int currentDirection = 0;

#define softLoop 1000
#define harshLoop 2500

//-------------------------------------
//---------    Heat Sensor   ----------
//-------------------------------------

bool HeatSeenLeft = false;
bool HeatSeenRight = false;

bool TileSide = false;

//-------------------------------------
//---------   Touch Sensor   ----------
//-------------------------------------

#define touchFront 23
#define touchFrontLeft 22
#define touchFrontRight 21

#define touchBack 16
#define touchBackLeft 17
#define touchBackRight 20

bool touchF  = false;
bool touchFL = false;
bool touchFR = false;

bool touchB  = false;
bool touchBL = false;
bool touchBR = false;


//-------------------------------------
//---------   Sensor Setup   ----------
//-------------------------------------


void sensorSetup() {
    pinMode(AccelReset, OUTPUT);
    
    digitalWrite(AccelReset, LOW);
    delay(500);
    digitalWrite(AccelReset, HIGH);
    
  /* Initialise the sensor */
    while (!bno.begin()){
    
    /* There was a problem detecting the BNO055 ... check your connections */
      log(ERROR,"no BNO055 detected ... Check your wiring or I2C ADDR! Please restart Program!");
      delay(2000);

  }
  
    log(INFO,"Found Accel Sensor");
    
    pinMode(LightSensorLED, OUTPUT);
    digitalWrite(LightSensorLED, HIGH);

  if (tcs.begin()) {
    log(INFO,"Found Light Sensor");
  } else {
    while (!tcs.begin()){
     log(ERROR,"No TCS34725 found ... check your connections");
      }
    }
  

  bno.setExtCrystalUse(true);


}

//-------------------------------------
//---------   Pause Button   ----------
//-------------------------------------

#define pause_button 12
bool pause = false;

//-------------------------------------
//---------        LED       ----------
//-------------------------------------
//13 - ORANGE SATUES LIGHT
//28 - BLUE UNDER FACE
//11 - BLUE UNDER KID
//31 - BLUE UNDER USB
//33 - ORANGE
//32 - RED


#define DATA_IN_LED 33
#define DATA_OUT_LED 32
#define SATUES_LED 31

#define BLUE_LED_1 28
#define BLUE_LED_2 31
#define BLUE_LED_3 11


void flashLED(int Tdelay) {


  digitalWrite(BLUE_LED_1, LOW);
  digitalWrite(BLUE_LED_2, LOW);
  digitalWrite(BLUE_LED_3, LOW);
  delay(Tdelay);

  digitalWrite(BLUE_LED_1, HIGH);
  digitalWrite(BLUE_LED_2, HIGH);
  digitalWrite(BLUE_LED_3, HIGH);
  delay(Tdelay);

  digitalWrite(BLUE_LED_1, LOW);
  digitalWrite(BLUE_LED_2, LOW);
  digitalWrite(BLUE_LED_3, LOW);
  delay(Tdelay);

  digitalWrite(BLUE_LED_1, HIGH);
  digitalWrite(BLUE_LED_2, HIGH);
  digitalWrite(BLUE_LED_3, HIGH);
  delay(Tdelay);

  digitalWrite(BLUE_LED_1, LOW);
  digitalWrite(BLUE_LED_2, LOW);
  digitalWrite(BLUE_LED_3, LOW);
  delay(Tdelay);

  digitalWrite(BLUE_LED_1, HIGH);
  digitalWrite(BLUE_LED_2, HIGH);
  digitalWrite(BLUE_LED_3, HIGH);
  delay(Tdelay);

  digitalWrite(BLUE_LED_1, LOW);
  digitalWrite(BLUE_LED_2, LOW);
  digitalWrite(BLUE_LED_3, LOW);
  delay(Tdelay);

  digitalWrite(BLUE_LED_1, HIGH);
  digitalWrite(BLUE_LED_2, HIGH);
  digitalWrite(BLUE_LED_3, HIGH);
}
//-------------------------------------
//---------  MOTOR MOVEMENT  ----------
//-------------------------------------

//Generic Speeds
int speedVal1 = 0;
int speedVal2 = 100;
int speedVal3 = 200;
int speedVal4 = 255;

#define FMotor 2
#define BMotor 4
#define LMotor 3
#define RMotor 1

#define LEFT 0
#define RIGHT 1
#define BACKWARDS 2
#define HEAT_TURN 4

#define START_BASE_POWER 500
#define START_MAX_POWER 1000



int BASE_POWER = START_BASE_POWER; // base power (going straight ahead)
int MAX_POWER = START_MAX_POWER; // maximum speed of the motors
//-------------------------------------
//---------      Lidar       ----------
//-------------------------------------

#define RPLIDAR_MOTOR 3 // 23

// tile movement
float forwardTile = 0;
bool moveTilefinished = true;

#define requiredQuality 5

//Amount of tiles
int Tile_Forwards = 0;
int Tile_Backwards = 0;
int Tile_Right  = 0;
int Tile_Left  = 0;

//Distance to wall in MM
float Lidar_Front = -0;
float Lidar_Back  = -0;
float Lidar_Right = -0;
float Lidar_Left  = -0;
float Lidar_Front_Right = -0;
float Lidar_Front_Left  = -0;
float Lidar_Back_Right  = -0;
float Lidar_Back_Left   = -0;

float Last_Lidar_Front = -0;
float Last_Lidar_Back  = -0;
float Last_Lidar_Right = -0;
float Last_Lidar_Left  = -0;
float Last_Lidar_Front_Right = -0;
float Last_Lidar_Front_Left  = -0;
float Last_Lidar_Back_Right  = -0;
float Last_Lidar_Back_Left   = -0;


//-------------------------------------
//---------      Setup       ----------
//-------------------------------------


void pinSetup() {

  pinMode(DATA_IN_LED, OUTPUT);
  pinMode(DATA_OUT_LED, OUTPUT);
  pinMode(SATUES_LED, OUTPUT);

  pinMode(BLUE_LED_1, OUTPUT);
  pinMode(BLUE_LED_2, OUTPUT);
  pinMode(BLUE_LED_3, OUTPUT);

  digitalWrite(DATA_IN_LED, HIGH);
  digitalWrite(DATA_OUT_LED, HIGH);
  digitalWrite(SATUES_LED, HIGH);

  digitalWrite(BLUE_LED_1, HIGH);
  digitalWrite(BLUE_LED_2, HIGH);
  digitalWrite(BLUE_LED_3, HIGH);
  
  pinMode(RPLIDAR_MOTOR, OUTPUT);
  servoSetup();
  
  sensorSetup();

  // Connect motors and lidar
  Dynamixel.begin(1000000, 2);
  lidar.begin(Serial1);
  Serial3.begin(9600);
  //Pinmode setups

  pinMode(touchFront, INPUT_PULLUP);
  pinMode(touchFrontLeft, INPUT_PULLUP);
  pinMode(touchFrontRight, INPUT_PULLUP);

  pinMode(touchBack, INPUT_PULLUP);
  pinMode(touchBackLeft, INPUT_PULLUP);
  pinMode(touchBackRight, INPUT_PULLUP);

  pinMode(pause_button, INPUT_PULLUP);
  


}


#endif
