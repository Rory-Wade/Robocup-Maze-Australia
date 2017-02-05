////  ------------------------------------------------------
//// ----------          Communications          -----------
//// ----------     Rescue Robot Code 2016       -----------
////  ---------                                  -----------
//// ---------- Team: Rory W, Ines K & Joseph F  -----------
//// ----------         Mentor:Alex C            -----------
//// -------------------------------------------------------

#ifndef __COMM
#define __COMM

#include "pinout.h"
#include "lidar.h"
#include "debug_log.h"
#include "wall_follow.h"
#include "heat.h"

#define delimiterCharacter ':'
#define delimiterValue ';'

#define HEAT 0
#define ACCEL 1
#define LIGHT 2
#define TILES 3

String readData() {
  int i = 0;
  String data = "";
  if (Serial3.available()) {
    delay(20); //allows all serial sent to be received together
    while (Serial3.available()) {
      char inChar = Serial3.read();
      data = data + inChar;
      i++;
    }
  }
  return data;
}

void clearBuffer(){
  String bufferString = readData();
  log(ERROR,"Buffer Had Data - CLEARING");  
}

String getValue(String data, char separator, int index)  {
  int found = 0;
  int strIndex[] = {
    0, -1
  };
  int maxIndex = data.length() - 1;
  for (int i = 0; i <= maxIndex && found <= index; i++) {
    digitalWrite(DATA_IN_LED, HIGH);
    if (data.charAt(i) == separator || i == maxIndex) {
      found++;
      strIndex[0] = strIndex[1] + 1;
      strIndex[1] = (i == maxIndex) ? i + 1 : i;
    }
    digitalWrite(DATA_IN_LED, LOW);
  }
  return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}


void receiveData() {
  String data = readData();
//  log(INFO, "Received: %s", data);

  String messageType = getValue(data, delimiterCharacter, 0); // Gets the expression
  String messageTypeVal = getValue(data, delimiterCharacter, 1); // gets the values from it

  switch (messageType.charAt(0)) {

    case 'D': {
        String shouldDrop = getValue(messageTypeVal, ';', 0);
        //
        //      if(shouldDrop == "T"){
        //        if(heatLeft){
        //          drop(LEFT_SIDE);
        //
        //        }else{
        //          drop(RIGHT_SIDE);
        //
        //        }
        //      }
      }

      break;
    case 'M': {
        String turnDirection = getValue(messageTypeVal, ';', 0);

        //      byte turnDirectionBytes[turnDirection.length() + 1];
        //      turnDirection.getBytes(turnDirectionBytes, turnDirection.length() + 1);

        //Serial.begin(turnDirectionBytes);
        log(INFO,"Move: %d", turnDirection.toInt());

        if (turnDirection.toInt() == 1) {
          log(INFO,"Turn Right");
          turnRobot(RIGHT);


        } else if (turnDirection.toInt() == 2) {
          log(INFO,"Turn Around");
          stopMotors();
          turnRobot(RIGHT);
          turnRobot(RIGHT);


        } else if (turnDirection.toInt() == 3) {
          log(INFO,"Turn Left");
          turnRobot(LEFT);


        } else if (turnDirection.toInt() >= 0) {
          log(INFO,"Go Forward");

        } else {
          log(ERROR,"Communication Error: Received Invailid Value When Unrapping String In Movement:( > 3 || < 0 ) ");
        }
      }
      break;
    case 'P': {
        String pauseRobot = getValue(messageTypeVal, ';', 0);

        if (pauseRobot == "T") {
          pause = !pause;
        }
      }

      break;
      // default:{


      // }

      // break;
  }

}

void sendData(int type) {
  String sendData = "";

  switch (type) {
    case HEAT: {
        sendData += "H:";

        if (heatLeft) {
          sendData += "T;";

        } else {
          sendData += "F;";

        } if (heatRight) {
          sendData += "T|";

        } else {
          sendData += "F|";

        }
      }
      break;
    case LIGHT: {
        sendData += "L:";

        if (heatLeft) {
          sendData += "T|";

        } else {
          sendData += "F|";

        }
      }
      break;
    case TILES: {

        Serial.print("T:");
        Serial.print(Tile_Forwards);
        Serial.print(";");
        Serial.print(Tile_Right);
        Serial.print(";");
        Serial.print(Tile_Backwards);
        Serial.print(";");
        Serial.println(Tile_Left);
        delay(20);
        Serial3.print("T:");
        Serial3.print(Tile_Forwards);
        Serial3.print(";");
        Serial3.print(Tile_Right);
        Serial3.print(";");
        Serial3.print(Tile_Backwards);
        Serial3.print(";");
        Serial3.print(Tile_Left);


      }
      break;
    case ACCEL: {
        //      if(blackTile){
        //        sendData += "A:T|";
        //      }
        Serial3.print(sendData);
        Serial.print(sendData);
      }
      break;
  }

}
#endif
