'''Records measurments to a given file. Usage example:

$ python3 record_measurments.py out.txt'''
import sys
import time
from rplidar import RPLidar
import time, sched

PORT_NAME = '/dev/ttyUSB0'
lidar = RPLidar(PORT_NAME)
lidar.stop()
lidarArray = [None] * 360

s = sched.scheduler(time.time, time.sleep)

def readLidar():
    '''Main function'''
    
    global lidarArray
    
    count = 0
    
    for measurement in lidar.iter_measurments():
        count += 1
        measurementTwo = measurement
        angle = measurementTwo[2]
        distance = measurementTwo[3]

        lidarArray[int(angle) % 360] = distance
        
        #lidar.stop()
        #break
        
        if count % 10 == 0:
            print(count)
            
    #lidar.stop()
    #lidar.disconnect()

if __name__ == '__main__':
    while True:
        print("Start")
        readLidar()
        #print(lidarArray)
        val = 1+ 1

