//  ------------------------------------------------------
// ----------            Main Loop             -----------
// ----------     Rescue Robot Code 2016       -----------
// ----------                                  -----------
// ---------- Team: Rory W, Ines K & Joseph F  -----------
// ----------         Mentor:Alex C            -----------
// -------------------------------------------------------

// HardWare: Teensy 3.2

#include "pinout.h"
#include "movement.h"
#include "lidar.h"
#include "communication.h"
#include "debug_log.h"
#include "wall_follow.h"
#include "heat.h"
#include "sensors.h"
//#include "drop_mechanism"

void setup() {
  
  setup_logging(INFO);
  log(DEBUG, "Setup Void - RUNNGING\n");
  pinSetup();
  
  digitalWrite(DATA_IN_LED, LOW);
  lidarRun();
  
  digitalWrite(DATA_OUT_LED, LOW);
  flashLED(200);
  flashLED(100);
  
  digitalWrite(SATUES_LED, LOW);
  log(WARN, "Setup Void - DONE \n");
}

void loop() {

  log(VERBOSE, "loop");
  pauseButton();

  if(pause){
      turnRobot(LEFT);
      delay(250);
      turnRobot(RIGHT);
     
  }else{
    stopMotors();
    log(VERBOSE,"Robot Paused");
    analogWrite(RPLIDAR_MOTOR, 0); // Should stop after ten seconds!!!
  }


}


//-------------------------------------
//---------   Pause Button   ----------
//-------------------------------------

void pauseButton(){
  
  if(digitalRead(pause_button) == LOW){
        log(INFO,"Pause button pressed");
        pause = !pause;
        
        stopMotors();
        
        while(digitalRead(pause_button) == LOW){ // busy loop waiting for button to be released
        }
        log(INFO,"Pause button released");
        
       delay(200);
     
  }
}


