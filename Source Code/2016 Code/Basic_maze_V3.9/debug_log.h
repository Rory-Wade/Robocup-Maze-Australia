////  ------------------------------------------------------
//// ----------            Debug Log             -----------
//// ----------     Rescue Robot Code 2016       -----------
////  ---------                                  -----------
//// ---------- Team: Rory W, Ines K & Joseph F  -----------
//// ----------         Mentor:Alex C            -----------
//// -------------------------------------------------------

#ifndef __DEBUG_LOG
#define __DEBUG_LOG

#include <Arduino.h>
#include <stdarg.h>
#include <stdio.h>
#include <avr/io.h>


bool debug_mode = true;

// 0: NONE, 1: High Priority, 2: Medium Priority, 3 Low Priority
// different logging levels
#define ERROR 0
#define WARN 1
#define INFO 2
#define DEBUG 3
#define VERBOSE 4
static uint8_t logging_level = ERROR;

#define DEBUG_UART_SPEED 115200 // change this as required

void log(int level,const char* fmt, ...){
    if (debug_mode && level <= logging_level){ // only log if required to!
        char string[1024];
        sprintf(string,"%09lu", (uint32_t) millis());
        Serial.write(string);
        switch(level){
            case ERROR: Serial.write(" ERROR: "); break;
            case WARN:  Serial.write(" WARN: ");  break;
            case INFO:  Serial.write(" INFO: ");  break;
            case DEBUG: Serial.write(" DEBUG: "); break;
        }
        va_list logdata;
        va_start(logdata,fmt); // start the stack pointer after fmt string
        vsprintf(string,fmt,logdata); // write out the data
        va_end(logdata); // free the stack pointer   
        Serial.write(string);
        Serial.write("\n");
    }
}

void setup_logging(int level){
    logging_level = level;
    // start the serial monitor
    Serial.begin(DEBUG_UART_SPEED);
    // fill in the UART file descriptor with pointer to writer
    log(level,"Logging level: %d",logging_level);
}


#endif

