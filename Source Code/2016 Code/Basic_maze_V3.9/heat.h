//  ------------------------------------------------------
// ----------   Contactless IR Thermometer     -----------
// ----------     Rescue Robot Code 2016       -----------
//  ---------                                  -----------
// ---------- Team: Rory W, Ines K & Joseph F  -----------
// ----------         Mentor:Alex C            -----------
// -------------------------------------------------------

#ifndef __HEAT
#define __HEAT

#include "debug_log.h"

// suppress warnings about unused variables despite pragmas being there
#define PEC_UNUSED(expr) do { (void)(expr); } while (0)

#define heatSensorD 0x5A // standard address for the MLX90614 IR thermometer
#define heatSensorB 0x5B
#define heatSensorC 0x5C
#define heatSensorA 0x5D // Incrementing address by 1 each time

#define HEAT_THRESH 2.5
#define SET_HEAT_THRESH 27.0

float ObjTempLeft1 = 0.0;
float ObjTempLeft2 = 0.0;
float ObjTempRight1 = 0.0;
float ObjTempRight2 = 0.0;

float AmbTempLeft1 = 0.0;
float AmbTempLeft2 = 0.0;
float AmbTempRight1 = 0.0;
float AmbTempRight2 = 0.0;

float Left1HeatThresh = 0.0;
float Left2HeatThresh = 0.0;
float Right1HeatThresh = 0.0;
float Right2HeatThresh = 0.0;

#define resolution 0.02 // resolution of the MLX90614 = 0.02 deg/LSB

// MLX90614 RAM addresses
#define MLX90614_RAWIR1 0x04 // Assuming raw IR ambient?
#define MLX90614_RAWIR2 0x05 // Assuming raw IR object?
#define MLX90614_TA 0x06     // Ambient temperature (degC)
#define MLX90614_TOBJ1 0x07  // Object temperature (degC)
#define MLX90614_TOBJ2 0x08  // Temperature offset (-value @ 0degC)

#define AMBIENT_TEMPERATURE MLX90614_TA
#define OBJECT_TEMPERATURE MLX90614_TOBJ1
// MLX90614 EEPROM addresses


// DO NOT EDIT THESE {
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
// } DO NOT EDIT THESE 

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

       // Ignore unused warning
        #pragma GCC diagnostic push
        #pragma GCC diagnostic ignored "-Wunused-variable"
        uint8_t pec = Wire.read(); // grab PEC data but discard (not error checking)
        PEC_UNUSED(pec);
        #pragma GCC diagnostic pop

        return ret;
    } else{
        log(ERROR,"Temperature sensor failed to read!");
        return 0;
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


void updateHeat(){
   ObjTempLeft1 = readTemp(heatSensorA,OBJECT_TEMPERATURE);
   ObjTempLeft2 = readTemp(heatSensorB,OBJECT_TEMPERATURE);
   ObjTempRight1 = readTemp(heatSensorC,OBJECT_TEMPERATURE);
   ObjTempRight2 = readTemp(heatSensorD,OBJECT_TEMPERATURE);

   AmbTempLeft1 = readTemp(heatSensorA,AMBIENT_TEMPERATURE);
   AmbTempLeft2 = readTemp(heatSensorB,AMBIENT_TEMPERATURE);
   AmbTempRight1 = readTemp(heatSensorC,AMBIENT_TEMPERATURE);
   AmbTempRight2 = readTemp(heatSensorD,AMBIENT_TEMPERATURE);

   
}

void printHeat(){
    updateHeat();
    
    log(INFO,"Heat Sensor Address: 0x%x | Ambient temperature: %f | Object temperature: %f " , heatSensorA, ObjTempLeft1, AmbTempLeft1);
    log(INFO,"Heat Sensor Address: 0x%x | Ambient temperature: %f | Object temperature: %f " , heatSensorB, ObjTempLeft2, AmbTempLeft2);
    log(INFO,"Heat Sensor Address: 0x%x | Ambient temperature: %f | Object temperature: %f " , heatSensorC, ObjTempRight1, AmbTempRight1);
    log(INFO,"Heat Sensor Address: 0x%x | Ambient temperature: %f | Object temperature: %f " , heatSensorD, ObjTempRight2, AmbTempRight2);
}

void updateHeatThresh(){
   updateHeat();
   
   Left1HeatThresh = AmbTempLeft1 + HEAT_THRESH;
   Left2HeatThresh = AmbTempLeft2 + HEAT_THRESH;
   Right1HeatThresh = AmbTempRight1 + HEAT_THRESH;
   Right2HeatThresh = AmbTempRight2 + HEAT_THRESH;
}

bool testHeat(){
  updateHeat();

  bool returnValue = false;
  
  bool leftHeat = (  (ObjTempLeft1 > Left1HeatThresh || ObjTempLeft2 > Left2HeatThresh) &&
                     (ObjTempLeft1 > SET_HEAT_THRESH || ObjTempLeft2 > SET_HEAT_THRESH) ); 

     log(DEBUG,"Heat Left | OBJ 1 temperature: %f | OBJ 2 temperature: %f | Thresh 1: %f  | Thresh 2: %f " , ObjTempLeft1, ObjTempLeft2, Left1HeatThresh, Left2HeatThresh);
     log(DEBUG,"Heat Right | OBJ 1 temperature: %f | OBJ 2 temperature: %f | Thresh 1: %f  | Thresh 2: %f " , ObjTempRight1, ObjTempRight2, Right1HeatThresh, Right2HeatThresh);
  
  bool rightHeat = ( (ObjTempRight1 > Right1HeatThresh || ObjTempRight2 > Right2HeatThresh) &&
                     (ObjTempRight1 > SET_HEAT_THRESH  || ObjTempRight2 > SET_HEAT_THRESH) ); 
//
  if(leftHeat && Lidar_Left < 250.0){
    HeatSeenLeft = true;
    returnValue = true;

  }
//
  if(rightHeat && Lidar_Right < 250.0){
    HeatSeenRight = true;
    returnValue = true;

  }
  
  return returnValue;

}

#endif
