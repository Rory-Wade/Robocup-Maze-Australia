// Arduino I2C code for MLX90614 Contactless IR Thermometer
// Uses Repeated start with PEC

#include<Arduino.h>
#include<Wire.h>
#include <PWMServo.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include "Adafruit_TCS34725.h"
#include <RPLidar.h>

RPLidar lidar;

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


#define BNO055_SAMPLERATE_DELAY_MS (100)
Adafruit_BNO055 bno = Adafruit_BNO055();

Adafruit_TCS34725 tcs = Adafruit_TCS34725(TCS34725_INTEGRATIONTIME_700MS, TCS34725_GAIN_1X);

#define sen0addr 0x5A // standard address for the MLX90614 IR thermometer
#define sen1addr 0x5B
#define sen2addr 0x5C
#define sen3addr 0x5D // Incrementing address by 1 each time

#define resolution 0.02 // resolution of the MLX90614 = 0.02 deg/LSB

// MLX90614 RAM addresses
#define MLX90614_RAWIR1 0x04 // Assuming raw IR ambient?
#define MLX90614_RAWIR2 0x05 // Assuming raw IR object?
#define MLX90614_TA 0x06     // Ambient temperature (degC)
#define MLX90614_TOBJ1 0x07  // Object temperature (degC)
#define MLX90614_TOBJ2 0x08  // Temperature offset (-value @ 0degC)

// MLX90614 EEPROM addresses
// DO NOT USE THESE IF YOU DON'T KNOW WHAT YOU ARE DOING!
#define MLX90614_TOMAX 0x20
#define MLX90614_TOMIN 0x21
#define MLX90614_PWMCTRL 0x22
#define MLX90614_TARANGE 0x23
#define MLX90614_EMISS 0x24
#define MLX90614_CONFIG 0x25
#define MLX90614_ADDR 0x2E
#define MLX90614_ID1 0x3C
#define MLX90614_ID2 0x3D
#define MLX90614_ID3 0x3E
#define MLX90614_ID4 0x3F

bool lidarRun(){

Lidar_Front = -1;                
Lidar_Back = -1;
Lidar_Right  = -1;
Lidar_Left  = -1;
Lidar_Front_Right  = -1; 
Lidar_Back_Right  = -1;
Lidar_Back_Left  = -1;
Lidar_Front_Left  = -1;



bool returnValue = false; 

while(Lidar_Front == -1 || Lidar_Back == -1 || Lidar_Right == -1 || Lidar_Left == -1 || Lidar_Front_Right == -1 || Lidar_Back_Right == -1 || Lidar_Back_Left == -1 || Lidar_Front_Left == -1){  

  
  //Serial.print(".");
  if (IS_OK(lidar.waitPoint())) {
      
    float distance = lidar.getCurrentPoint().distance; //distance value in mm unit
    float angle    = lidar.getCurrentPoint().angle; //anglue value in degree
    byte  quality  = lidar.getCurrentPoint().quality; //quality of the current measurement
//  bool  startBit = lidar.getCurrentPoint().startBit; //whether this point is belong to a new scan

   if((angle >= 359.0 || angle <= 1.0) && quality > requiredQuality){
      Lidar_Front = distance;
      
   }else if(angle >= 87.0 && angle <= 92.0 && quality > requiredQuality){
      Lidar_Left = distance;
      
   }else if(angle >= 177.0 && angle <= 182.0 && quality > requiredQuality){
      Lidar_Back = distance;
      
   }else if(angle >= 267.0 && angle <= 272.0 && quality > requiredQuality){
      Lidar_Right = distance;
      
   
   
   }else if(angle >= 57.0 && angle <= 62.0 && quality > requiredQuality){
      Lidar_Front_Left = distance;
      
   }else if(angle >= 117.0 && angle <= 122.0 && quality > requiredQuality){
      Lidar_Back_Left = distance;
      
    }else if(angle >= 237.0 && angle <= 242.0 && quality > requiredQuality){
      Lidar_Back_Right = distance;
      
   }else if(angle >= 297.0 && angle <= 302.0 && quality > requiredQuality){
      Lidar_Front_Right = distance;
      
   }
     returnValue = true;
     
  } else {

    analogWrite(RPLIDAR_MOTOR, 0); //stop the rplidar motor
    
    // try to detect RPLIDAR... 
    rplidar_response_device_info_t info;
    if (IS_OK(lidar.getDeviceInfo(info, 100))) {
       // detected...
       lidar.startScan();
       // start motor rotating at max allowed speed
       analogWrite(RPLIDAR_MOTOR, 250);
       delay(500);
       returnValue = false;
      }else{
      }
    }
  }
  //calculateTiles();

  
  return returnValue;
}


// read 16 bits (2 bytes) from a register --------------------------------------
uint16_t read16(uint8_t addr, uint8_t reg) {

  uint16_t ret;

    // Send register address to read from
    Wire.beginTransmission(addr);
    Wire.write(reg);
    Wire.endTransmission(false);

    // Request 3 bytes back (2 bytes info, 1 byte PEC error checking)
    Wire.requestFrom((uint8_t)addr, (uint8_t)3); // send data n-bytes read
    if (3 <= Wire.available()){
        ret = Wire.read(); // receive DATA
        ret |= Wire.read() << 8; // receive DATA

        uint8_t pec = Wire.read(); // grab PEC data but discard (not error checking)

        return ret;
    } else{
        Serial.print("ERR");
    }
}

// Read temperature from a register --------------------------------------------
float readTemp(uint8_t addr, uint8_t reg) {

  float temp;

  temp =  read16(addr, reg);
  temp *= resolution;
  temp -= 273.15;
  return temp;
}

// Setup -----------------------------------------------------------------------
void setup(){
    //Initialise Serial and I2C connections
    Serial.begin(9600);
    lidar.begin(Serial1);

  
    // set pin modes
     pinMode(RPLIDAR_MOTOR, OUTPUT);
  
    while(!Serial){ // Leonardo: wait for serial port to connect
        tone(11,500);
        delay(10);
        noTone(11);
        delay(100);
    }
    Wire.begin();

     /* Initialise the sensor */
  if(!bno.begin())
  {
    /* There was a problem detecting the BNO055 ... check your connections */
    Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    while(1);
  }

  delay(1000);

  bno.setExtCrystalUse(true);

  if (tcs.begin()) {
    Serial.println("Found sensor");
  } else {
    Serial.println("No TCS34725 found ... check your connections");
    while (1);
  }

}

// Loop ------------------------------------------------------------------------
void loop(){

  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  
  uint16_t r, g, b, c, colorTemp, lux;
  tcs.getRawData(&r, &g, &b, &c);
  colorTemp = tcs.calculateColorTemperature(r, g, b);
  lux = tcs.calculateLux(r, g, b);

  lidarRun();
//    Serial.print("Raw IR 1: ");
//    Serial.println( read16(MLX90614_RAWIR1) );
//    Serial.print("Raw IR 2: ");
//    Serial.println( read16(MLX90614_RAWIR2) );
    Serial.println("---------------------------------------------------------");
    Serial.print("Ambient temperature: ");
    Serial.println( readTemp(sen0addr,MLX90614_TA) );
    Serial.print("Object temperature: ");
    Serial.println( readTemp(sen0addr,MLX90614_TOBJ1) );
    Serial.print("Temperature offset (-value @ 0degC): ");
    Serial.println( read16(sen0addr,MLX90614_TOBJ2) );
    Serial.print("Sensor address: 0x");
    Serial.println(sen0addr, HEX);
    Serial.println("~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ");
    Serial.print("Ambient temperature: ");
    Serial.println( readTemp(sen1addr,MLX90614_TA) );
    Serial.print("Object temperature: ");
    Serial.println( readTemp(sen1addr,MLX90614_TOBJ1) );
    Serial.print("Temperature offset (-value @ 0degC): ");
    Serial.println( read16(sen1addr,MLX90614_TOBJ2) );
    Serial.print("Sensor address: 0x");
    Serial.println(sen1addr, HEX);
    Serial.println("~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ");
    Serial.print("Ambient temperature: ");
    Serial.println( readTemp(sen2addr,MLX90614_TA) );
    Serial.print("Object temperature: ");
    Serial.println( readTemp(sen2addr,MLX90614_TOBJ1) );
    Serial.print("Temperature offset (-value @ 0degC): ");
    Serial.println( read16(sen2addr,MLX90614_TOBJ2) );
    Serial.print("Sensor address: 0x");
    Serial.println(sen2addr, HEX);
    Serial.println("~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ~~ ");
    Serial.print("Ambient temperature: ");
    Serial.println( readTemp(sen3addr,MLX90614_TA) );
    Serial.print("Object temperature: ");
    Serial.println( readTemp(sen3addr,MLX90614_TOBJ1) );
    Serial.print("Temperature offset (-value @ 0degC): ");
    Serial.println( read16(sen3addr,MLX90614_TOBJ2) );
    Serial.print("Sensor address: 0x");
    Serial.println(sen3addr, HEX);
    Serial.println("---------------------------------------------------------");
    Serial.println("ACCELEORMETER");
    Serial.print("X: ");
    Serial.print(euler.x());
    Serial.print(" Y: ");
    Serial.print(euler.y());
    Serial.print(" Z: ");
    Serial.print(euler.z());
    Serial.println("\t\t");
    Serial.println("---------------------------------------------------------");
    Serial.println("COLOUR SENSOR");
    Serial.print("Color Temp: "); Serial.print(colorTemp, DEC); Serial.print(" K - ");
    Serial.print("Lux: "); Serial.print(lux, DEC); Serial.print(" - ");
    Serial.print("R: "); Serial.print(r, DEC); Serial.print(" ");
    Serial.print("G: "); Serial.print(g, DEC); Serial.print(" ");
    Serial.print("B: "); Serial.print(b, DEC); Serial.print(" ");
    Serial.print("C: "); Serial.print(c, DEC); Serial.print(" ");
    Serial.println(" ");
    Serial.println("---------------------------------------------------------");
    Serial.print("Lidar_Front: "); Serial.print(Lidar_Front); Serial.println(" ");
    Serial.print("Lidar_Back: "); Serial.print(Lidar_Back); Serial.println(" ");
    Serial.print("Lidar_Right: "); Serial.print(Lidar_Right); Serial.println(" ");
    Serial.print("Lidar_Left: "); Serial.print(Lidar_Left); Serial.println(" ");
    Serial.print("Lidar_Front_Right: "); Serial.print(Lidar_Front_Right); Serial.println(" ");
    Serial.print("Lidar_Back_Right: "); Serial.print(Lidar_Back_Right); Serial.println(" ");
    Serial.print("Lidar_Back_Right: "); Serial.print(Lidar_Back_Right); Serial.println(" ");
    Serial.print("Lidar_Front_Left: "); Serial.print(Lidar_Front_Left); Serial.println(" ");
    Serial.println("---------------------------------------------------------");
    Serial.println(" ");Serial.println(" ");Serial.println(" ");Serial.println(" ");


    delay(100); // Sensors Refresh @ 2Hz
}
