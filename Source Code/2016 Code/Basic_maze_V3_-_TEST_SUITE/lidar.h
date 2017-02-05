//  ------------------------------------------------------
// ----------             Movement             -----------
// ----------     Rescue Robot Code 2016       -----------
//  ---------                                  -----------
// ---------- Team: Rory W, Ines K & Joseph F  -----------
// ----------         Mentor:Alex C            -----------
// -------------------------------------------------------

#ifndef __LIDAR
#define __LIDAR

#include "pinout.h"
#include "debug_log.h"



//-------------------------------------
//---------  PrintLidar()    ----------
//-------------------------------------

void printLidarData(){

    log(DEBUG,"Lidar_Front: %.02f",Lidar_Front);
    log(DEBUG,"Lidar_Back: %.02f",Lidar_Back);
    log(DEBUG,"Lidar_Right: %.02f",Lidar_Right);
    log(DEBUG,"Lidar_Left: %.02f",Lidar_Left);

    log(DEBUG,"Lidar_Front_Right: %.02f",Lidar_Front_Right);
    log(DEBUG,"Lidar_Back_Right: %.02f",Lidar_Back_Right);
    log(DEBUG,"Lidar_Back_Right: %.02f",Lidar_Back_Right);
    log(DEBUG,"Lidar_Front_Left: %.02f",Lidar_Front_Left);
}



//-------------------------------------
//--------- calculateTiles() ----------
//-------------------------------------

void calculateTiles(){

  Tile_Forwards = 0;
  Tile_Backwards = 0;
  Tile_Right  = 0;
  Tile_Left  = 0;

  printLidarData();
  
   if(Lidar_Front != 0){
     Tile_Forwards = Lidar_Front / 300;
     Tile_Forwards++;
     
     if(Tile_Forwards > 9){
      Tile_Forwards = 9;
     }
  }
   if(Lidar_Back != 0){
     Tile_Backwards = Lidar_Back / 300;
     Tile_Backwards++;
     
     if(Tile_Backwards > 9){
      Tile_Backwards = 9;
     }
  }
    if(Lidar_Right != 0){
     Tile_Right = Lidar_Right / 300;
     Tile_Right++;
     
     if(Tile_Right > 9){
      Tile_Right = 9;
     }
  }
    if(Lidar_Left != 0){
    Tile_Left = Lidar_Left / 300;
    Tile_Left++;
    
    if(Tile_Left > 9){
      Tile_Left = 9;
     }
  }
  
  log(INFO, "Tile Values - Forwards:%d Backwards:%d Left:%d Right:%d",Tile_Forwards, Tile_Backwards, Tile_Left, Tile_Right);
}


//-------------------------------------
//---------   LidarRun()     ----------
//-------------------------------------

bool lidarRun(){

Lidar_Front = -1;                
Lidar_Back = -1;
Lidar_Right  = -1;
Lidar_Left  = -1;
Lidar_Front_Right  = -1; 
Lidar_Back_Right  = -1;
Lidar_Back_Left  = -1;
Lidar_Front_Left  = -1;

log(VERBOSE,"Lidar Data Dump Query");

bool returnValue = false; 

while(Lidar_Front == -1 || Lidar_Back == -1 || Lidar_Right == -1 || Lidar_Left == -1 || Lidar_Front_Right == -1 || Lidar_Back_Right == -1 || Lidar_Back_Left == -1 || Lidar_Front_Left == -1){  
  log(VERBOSE,"Lidar Query");
  
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
      log(INFO,"Starting Lidar");
       // start motor rotating at max allowed speed
       analogWrite(RPLIDAR_MOTOR, 250);
       delay(500);
       returnValue = false;
      }else{
        log(ERROR,"The Lidar isn't Working");
      }
    }
  }
  //calculateTiles();
  printLidarData();
  log(DEBUG,"LIDAR HAS VALUES");
  
  return returnValue;
}
#endif
