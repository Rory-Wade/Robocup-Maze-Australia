//  ------------------------------------------------------
// ----------   Contactless IR Thermometer     -----------
// ----------     Rescue Robot Code 2016       -----------
//  ---------                                  -----------
// ---------- Team: Rory W, Ines K & Joseph F  -----------
// ----------         Mentor:Alex C            -----------
// -------------------------------------------------------

#ifndef __HEAT
#define __HEAT

// the places to plug the wires in to the heat sensors are:
// 5V - 

#include <Arduino.h>
#include <Wire.h>
#include "debug_log.h"

// suppress warnings about unused variables despite pragmas being there
#define PEC_UNUSED(expr) do { (void)(expr); } while (0)

#define resolution 0.02 // resolution of the MLX90614 = 0.02 deg/LSB
#define temperature_threshold 25 // object temperature threshold above ambient

// MLX90614 RAM addresses
#define MLX90614_RAWIR1 0x04 // Raw IR ambient
#define MLX90614_RAWIR2 0x05 // Raw IR object
#define MLX90614_TA 0x06     // Ambient temperature (degC) in binary
#define MLX90614_TOBJ1 0x07  // Object temperature (degC) in binary
#define MLX90614_TOBJ2 0x08  // Temperature offset (-value @ 0degC)

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

// Read temperature from a register in degC --------------------------------------------
float readTemp(uint8_t addr, uint8_t reg) { // takes an address (which sensor) & register (value)
    log(DEBUG,"Reading temperature from sensor 0x%x",addr);
    float temp;

    temp =  read16(addr, reg);
    temp *= resolution;
    temp -= 273.15;
    return temp;
}

#endif
