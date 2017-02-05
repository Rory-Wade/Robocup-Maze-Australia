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
    log(DEBUG,"Lidar_Back_Left: %.02f",Lidar_Back_Left);
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
  
   if(Lidar_Front != 0 && Lidar_Front != -1){
     Tile_Forwards = Lidar_Front / 310;
     Tile_Forwards++;
     
     if(Tile_Forwards > 9){
      Tile_Forwards = 9;
     }
  } else{
    Tile_Forwards = 2;
  }
  
   if(Lidar_Back != 0 && Lidar_Back != -1){
     Tile_Backwards = Lidar_Back / 310;
     Tile_Backwards++;
     
     if(Tile_Backwards > 9){
      Tile_Backwards = 9;
     }
  }else{
    Tile_Backwards = 2;
  }
  
    if(Lidar_Right != 0 && Lidar_Right != -1){
     Tile_Right = Lidar_Right / 310;
     Tile_Right++;
     
     if(Tile_Right > 9){
      Tile_Right = 9;
     }
  }else{
    Tile_Right = 2;
  }
  
    if(Lidar_Left != 0 && Lidar_Left != -1){
    Tile_Left = Lidar_Left / 310;
    Tile_Left++;
    
    if(Tile_Left > 9){
      Tile_Left = 9;
     }
  }else{
    Tile_Left = 2;
  }
  
  log(ERROR, "Tile Values - Forwards:%d Backwards:%d Left:%d Right:%d",Tile_Forwards, Tile_Backwards, Tile_Left, Tile_Right);
}


//-------------------------------------
//---------   LidarRun()     ----------
//-------------------------------------

bool lidarRun(int loops){
log(ERROR,"Lidar Code Running");
digitalWrite(DATA_OUT_LED, HIGH);

int stopTimer = 0;

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

//

  log(DEBUG,"Lidar Query");
while( ( Lidar_Front == -1 || Lidar_Back == -1 || Lidar_Right == -1 || Lidar_Left == -1 || Lidar_Front_Right == -1 || Lidar_Back_Right == -1 || Lidar_Back_Left == -1 || Lidar_Front_Left == -1 ) && stopTimer < loops){  
  
  log(VERBOSE,"While Code Running");
  stopTimer++;
  log(VERBOSE,"STOP TIMER %d ", stopTimer);
  
  if (IS_OK(lidar.waitPoint())) {
    
    
    float distance = lidar.getCurrentPoint().distance; //distance value in mm unit
    float angle    = lidar.getCurrentPoint().angle; //anglue value in degree
    byte  quality  = lidar.getCurrentPoint().quality; //quality of the current measurement
//  bool  startBit = lidar.getCurrentPoint().startBit; //whether this point is belong to a new scan

   if((angle >= 359.0 || angle <= 1.0) && quality > requiredQuality){
      Last_Lidar_Front = Lidar_Front;
      Lidar_Front = distance;
      
   }else if(angle >= 87.0 && angle <= 92.0 && quality > requiredQuality){
      Last_Lidar_Left = Lidar_Left;
      Lidar_Left = distance;
      
   }else if(angle >= 177.0 && angle <= 182.0 && quality > requiredQuality){
    Last_Lidar_Back = Lidar_Back;
      Lidar_Back = distance;
      
   }else if(angle >= 267.0 && angle <= 272.0 && quality > requiredQuality){
    Last_Lidar_Right = Lidar_Right;
      Lidar_Right = distance;
      
   // side values are closer to left/right than front/back since when the robot rotates a higher degree angle's readings will swing wildly
   // making them less suitable for wall following.
   // front-left @ 75degrees
   
   }else if(angle >= 73.0 && angle <= 77.0 && quality > requiredQuality){
      Lidar_Front_Left = distance;
   // back-left @ 105degrees      
   
   }else if(angle >= 103.0 && angle <= 107.0 && quality > requiredQuality){
      Lidar_Back_Left = distance;
   // back-right @ 255degrees
   
   }else if(angle >= 253.0 && angle <= 257.0 && quality > requiredQuality){
      Lidar_Back_Right = distance;
   // front-right @ 285degrees
   
   }else if(angle >= 283.0 && angle <= 287.0 && quality > requiredQuality){
      Lidar_Front_Right = distance;
      
   }

     returnValue = true;
     
  } else {

    digitalWrite(RPLIDAR_MOTOR,LOW); //stop the rplidar motor
    
    // try to detect RPLIDAR... 
    rplidar_response_device_info_t info;
    if (IS_OK(lidar.getDeviceInfo(info, 100))) {
       // detected...
       lidar.startScan();
      log(INFO,"Starting Lidar");
       // start motor rotating at max allowed speed
       digitalWrite(RPLIDAR_MOTOR,HIGH);
       
       delay(500);
       returnValue = false;
      }else{
        log(ERROR,"The Lidar is broken - Check wires ");
      }
    }
  }

  if(Lidar_Front < 0.1){
    Lidar_Front = Last_Lidar_Front;
    log(ERROR,"The Lidar didn't get a value for Lidar_Front");
  }

  //Last_Lidar_Front = Last_Lidar_Back = Last_Lidar_Left = Last_Lidar_Right = Last_Lidar_Front_Left = Last_Lidar_Front_Right = Last_Lidar_Back_Right = Last_Lidar_Back_Left = 0;

  if(Lidar_Back < 0.1){
    Lidar_Back = Last_Lidar_Back;
    log(ERROR,"The Lidar didn't get a value for Lidar_Back");
  }

  if(Lidar_Left < 0.1){
    Lidar_Left = Last_Lidar_Left;
    log(ERROR,"The Lidar didn't get a value for Lidar_Left");
  }

  if(Lidar_Right < 0.1){
    Lidar_Right = Last_Lidar_Right;
    log(ERROR,"The Lidar didn't get a value for Lidar_Right");
  }

  if(Lidar_Front_Left < 0.1){
    Lidar_Front_Left = Last_Lidar_Front_Left;
    log(ERROR,"The Lidar didn't get a value for Lidar_Front_Left");
  }

  if(Lidar_Front_Right < 0.1){
    Lidar_Front_Right = Last_Lidar_Front_Right;
    log(ERROR,"The Lidar didn't get a value for Lidar_Front_Right");
  }

  if(Lidar_Back_Right < 0.1){
    Lidar_Back_Right = Last_Lidar_Back_Right;
    log(ERROR,"The Lidar didn't get a value for Lidar_Back_Right");
  }

  if(Lidar_Back_Left < 0.1){
    Lidar_Back_Left = Last_Lidar_Back_Left;
    log(ERROR,"The Lidar didn't get a value for Lidar_Back_Left");
  }

  //calculateTiles();
  printLidarData();
  log(DEBUG,"LIDAR HAS VALUES");
  digitalWrite(DATA_OUT_LED, LOW);
  return returnValue;
}
#endif
