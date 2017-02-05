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
#include "drop_mechanism.h"

#define delimiterCharacter ':'
#define delimiterValue ';'

#define HEAT 0
#define ACCEL 1
#define LIGHT 2
#define TILES 3
#define PAUSE 4
#define DIRECTION 5

int traceArray[255][3];


unsigned long checkSum;

void readData() {
  int i = 0;
  checkSum = 0;

    log(ERROR,"READING DATA");

  while (!Serial3.available());
  delay(5); //allows all serial sent to be received together

  log(ERROR,"Serial 3 is available");
  while (Serial3.available()) {

    int x = Serial3.read();
    int y = Serial3.read();
    int c = Serial3.read();

    i++;
    log(ERROR,"READING VALUE %d",i);
    if (x == 255 && y == (checkSum % 256) && c == 255) {
      log(ERROR,"Broke out of the loop");
      break;

    } else if (x == 255 || c == 255) {
      log(ERROR,"Invalid.");
      Serial3.write(checkSum % 256);
      readData();

    } else {

      traceArray[i][0] = x;
      traceArray[i][1] = y;
      traceArray[i][2] = c;

      log(ERROR,"X is %d", x);
      log(ERROR,"Y is %d", y);
      log(ERROR,"C is %d", c);

    }

    checkSum += ((int)x + (int)y + (int)c);

    delay(3);
  }
}

void clearBuffer() {
  //readData(traceArray);
  log(ERROR, "Buffer Had Data - CLEARING");
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
  //String data = readData();
  // log(VERBOSE, "Received: %c", data);

  // byte messageType = getValue(data, delimiterCharacter, 0); // Gets the expression
  // String messageTypeVal = getValue(data, delimiterCharacter, 1); // gets the values from it

  //  switch (messageType(0)) {
  //
  //    case 69: {
  //
  //        if (pauseRobot.toInt() == 1) {
  //          pause = !pause;
  //        }
  //      }
  //
  //      break;
  //       default:{
  //          log(ERROR,"NOTHING VALID RECEIVED");
  //
  //          Serial.println(data);
  //
  //      }
  //
  //      break;
  //  }
  //
}

void sendData(int type) {
  String sendData = "";

  switch (type) {
    case HEAT: {

        if (HeatSeenLeft || HeatSeenRight) {
          Serial3.print("H:");

          if (HeatSeenLeft) {
            Serial3.print("1");
          }
          else {
            Serial3.print("0");
          }


          if (HeatSeenRight) {
            Serial3.print("1");
          }
          else {
            Serial3.print("0");
          }

          if (TileSide) {
            Serial3.print("1");
          }
          else {
            Serial3.print("0");
          }

        }
      }
      break;
    case DIRECTION: {
        Serial3.print("C:");
        Serial3.print(currentDirection / 10);
      }
      break;
    case LIGHT: {

        if (BlackTileFound()) {
          Serial3.print("L:0");
        } else {
          Serial3.print("L:1");
        }

        log(WARN, "L:B%d S%d", BlackTileFound() , SilverTileFound());


      }
      break;
    case TILES: {

        log(WARN, "T:%d ;%d ;%d ;%d;", Tile_Forwards, Tile_Right, Tile_Backwards, Tile_Left);

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
        Serial3.print("A:"); // up 1 down 0 - only when going up or down
        if (RampUp) {
          Serial3.print("1");
        } else {
          Serial3.print("0");
        }
      }
      break;

    case PAUSE: {
        Serial3.print("P"); // up 1 down 0 - only when going up or down
      }
      break;
  }

  delay(20);

}

void waitForData(int type) {
  int i = 0;

  while (!Serial3.available()) {
    if (i >= 10000) {
      log(ERROR, "NO REPLY FROM EDISON - SENDING AGAIN");

      sendData(type);
      i = 0;
    }
    i++;
  }

  receiveData();
  clearBuffer();
}

#endif
