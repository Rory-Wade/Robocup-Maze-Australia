import sys
import time
import threading
import sched

from rplidar import RPLidar

PORT_NAME_MAC = '/dev/tty.SLAB_USBtoUART'
PORT_NAME = '/dev/ttyUSB0'

AVGLOOP = 2 #amount of scans averaged before release
lidarBuffer = [None] * 360

class lidarCMD:
    def __init__(self, PORT):

        self.PORT_NAME = PORT
        self.scanData = None
        self.scan_in_progress = False
        
        self.lidar = RPLidar(PORT) # unique port if we want to connect two lidars?
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

    def push_scan(self,arr):
        #[loop, time of scan, run time, DATA (in array of 360)]
        #self.scanData.append(arr)

        self.scanData = arr
        
        #if len(self.scanData) > 3: #keep the stack relevant by popping oldest value
            #self.scanData.pop(0)

    def scan_avaliable(self):
        #returns true if there is data
        if self.scanData == None: #keep the stack relevant
            return False

        return True

    def pop_scan(self):
        #[loop, time of scan, run time, DATA (in array of 360)]
        return self.scanData #self.scanData.pop(-1)

    def startScan(self):
        if not self.scan_in_progress:
            try:
                self.scan_in_progress = True
                self.push_scan(self.LIDARSCAN())
                
                return True
            except:
                return False
        return False

    def stopScan(self):
        self.scan_in_progress = False

        self.lidar.stop_motor()
        self.lidar.stop()

    global lidarBuffer
    
    s = sched.scheduler(time.time, time.sleep)
    def LIDARSCAN(self):
        
   
        #print("Lidar Satus: {}\tCode: {} \n Recording measurments... Press Crl+C to stop.".format(self.health()[0], self.health()[1])) #find exception before function start

        #lidarReadingsAVG = [None] * 360
        currLoop = 0
        scanTime = 0
        startTime = time.time()
        beginScan = False
        lidarValues = [None] * 360
        global lidarBuffer
        
        for measurment in self.lidar.iter_measurments():
            
            
            currLoop += 1
            
            if currLoop > 360:
                break
                
            if measurment[3] > 1:
                #print(measurment[3])
                lidarValues[int(measurment[2]) % 360] = measurment[3]
                
        lidarBuffer = lidarValues
        s.enter(0.1, 1, LIDARSCAN,())

    s.enter(0.1, 1, LIDARSCAN,())
    s.run()
            

 
def getLidarValues():
    lidar.push_scan(lidar.LIDARSCAN())
    if lidar.scan_avaliable():
       return lidar.pop_scan()
    return False
    

if __name__ == '__main__':

    lidar = lidarCMD(PORT_NAME)

    print(lidar.port())
    print(lidar.health())
    
    #lidar.startScan()
    
    while True:
        lidar.LIDARSCAN()
        print(lidarBuffer)
        print("")
        time.sleep(1)
