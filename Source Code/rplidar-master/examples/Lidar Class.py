'''Records measurments to a given file. Usage example:

$ Averge Output Speed: 0.815s'''
import sys
import time
import threading

from rplidar import RPLidar

#PORT_NAME = '/dev/ttyUSB0'
AVGLOOP = 5 #amount of scans averaged before release

class lidarCMD:
    def __init__(self, PORT):
        self.PORT_NAME = PORT
        self.scanData = [None]
        self.scan_in_progress = False
        
        self.lidar = RPLidar(PORT) # unique port if we want to connect two lidars? :P 
        self.lidar.connect()
        
        try: #Protection Against Previous Force Shutdown Errors
            self.lidar.get_health() #Works, No Reset Needed
        except:
            self.lidar.disconnect() #Error, Reset Needed (lidar.reset() doesn't fix issue)
            self.lidar.connect()
            
    def port(self):
        return self.PORT_NAME
        
    def health(self):
        return self.lidar.get_health()
    
    def push_readings(self,arr):
        #[loop, time of scan, run time, DATA (in array of 360)]
        self.scanData = arr
        
    def pull_readings(self):
        #[loop, time of scan, run time, DATA (in array of 360)]
        return self.scanData
    
    def startScan(self):
        if not self.scan_in_progress:
            try:
                
                self.scanThread = threading.Thread(target=self.LIDARSCAN)
                
                self.scanThread.daemon = False
                self.scanThread.start()

                self.scan_in_progress = True
                return True
            except:
                return False
        return False

    def stopScan(self):
        self.scan_in_progress = False

        self.lidar.stop_motor()
        self.lidar.stop()

    
    def LIDARSCAN(self):
        try:
            print("Lidar Satus: {}\tCode: {} \n Recording measurments... Press Crl+C to stop.".format(self.health()[0], self.health()[1])) #find exception before function start
    
            lidarReadingsAVG = [None] * 360
            currLoop = 0
            scanTime = 0
            startTime = time.time()

            while self.scan_in_progress:
                for measurment in self.lidar.iter_measurments():
                    
                    if self.scan_in_progress == False:
                        break

                    if measurment[0] == True:
                        currLoop += 1
                    
                        if currLoop % AVGLOOP == 0:
                            scanTime = (scanTime + (time.time() - startTime))/2
                            startTime = time.time()
                            
                            #print("\nLoop: {} scan time: {} timestamp: {} Readings: \n\n{}".format(currLoop, scanTime , time.time(),lidarReadingsAVG))
                            self.push_readings([currLoop, scanTime, time.time(), lidarReadingsAVG])
                            lidarReadingsAVG = [None] * 360
        
                    try:
                        if lidarReadingsAVG[int(measurment[2]) % 360] != None:
                            lidarReadingsAVG[int(measurment[2]) % 360] = float(format((lidarReadingsAVG[int(measurment[2]) % 360] + measurment[3])/2, '.3f'))
                        else:
                            lidarReadingsAVG[int(measurment[2]) % 360] = float(format(measurment[3], '.3f'))
                            
                    except IndexError:  
                        print("\nMeasurement out of range! -> {}".format(int(measurment[2])))
                    
        except Exception as e:
            print("An Error Has occured: {}".format(e))
            
    
if __name__ == '__main__':
   
   lidar = lidarCMD('/dev/ttyUSB0')
   print(lidar.port())
   print(lidar.health())
   
   lidar.startScan()
   
   time.sleep(5)
   print(lidar.pull_readings())

