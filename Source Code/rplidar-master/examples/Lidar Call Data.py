'''

LIDAR MANAGEMENT FILE BY RORY WADE
Handels the reading and the health of the lidar in a classed based system that enables multiple lidars

Averge Output Speed: 0.815s @ 5 rotations
Averge Output Speed: 0.452s @ 3 rotations

-- Goals --

1.Make a smart AVG LOOP that gets more accurate with the more elements in the Scans Queue
2.
'''

import sys
import time
import threading

from rplidar import RPLidar

PORT_NAME_WIN = '/dev/tty.SLAB_USBtoUART'
PORT_NAME_MAC = '/dev/tty.SLAB_USBtoUART'
PORT_NAME = '/dev/ttyUSB0'

AVGLOOP = 1 #amount of scans averaged before release

class lidarCMD:
    def __init__(self, PORT):

        self.PORT_NAME = PORT
        self.scanData = [None]
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
        self.scanData.append(arr)

        if len(self.scanData) > 3: #keep the stack relevant by popping oldest value
            self.scanData.pop(0)

    def peak_scan(self):
        #[loop, time of scan, run time, DATA (in array of 360)]
        return self.scanData[0]

    def scan_avaliable(self):
        #returns true if there is data
        if len(self.scanData) > 0: #keep the stack relevant
            return True

        return False

    def pop_scan(self):
        #[loop, time of scan, run time, DATA (in array of 360)]
        return self.scanData.pop(0)

    def startScan(self):
        if not self.scan_in_progress:
            try:
                self.scan_in_progress = True
                self.LIDARSCAN()

                '''
                self.scanThread = threading.Thread(target=self.LIDARSCAN)

                self.scanThread.daemon = True
                self.scanThread.start()


                '''

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
            beginScan = False

            while self.scan_in_progress:
                for measurment in self.lidar.iter_measurments():

                    if self.scan_in_progress == False:
                        break

                    if measurment[0] == True:
                        currLoop += 1


                        if currLoop % AVGLOOP == 0 and beginScan:
                            scanTime = (scanTime + (time.time() - startTime))/2
                            startTime = time.time()

                            self.push_scan([currLoop, scanTime, time.time(), lidarReadingsAVG])
                            lidarReadingsAVG = [None] * 360
                            self.scan_in_progress = False
                            break
                        beginScan = True

                    try:
                        if measurment[3] > 1:
                            if lidarReadingsAVG[int(measurment[2]) % 360] != None:
                                lidarReadingsAVG[int(measurment[2]) % 360] = float(format((lidarReadingsAVG[int(measurment[2]) % 360] + measurment[3])/2, '.3f'))
                            else:
                                lidarReadingsAVG[int(measurment[2]) % 360] = float(format(measurment[3], '.3f'))

                    except IndexError:
                        print("\nMeasurement out of range! -> {}".format(int(measurment[2])))

        except Exception as e:
            print("An Error Has occured: {}".format(e))

lidar = lidarCMD(PORT_NAME_MAC)
lidar.startScan()

def getLidarValues():
    lidar.startScan()

    if lidar.scan_avaliable():
        lidar.stopScan()

        return lidar.pop_scan()
    return None

if __name__ == '__main__':

   #lidar = lidarCMD(PORT_NAME_MAC)

   print(lidar.port())
   print(lidar.health())

   #lidar.startScan()

   print("HEY")

   while true:
       print(getLidarValues())
       time.sleep(1)
