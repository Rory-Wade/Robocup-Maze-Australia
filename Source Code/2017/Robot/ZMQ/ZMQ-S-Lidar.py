'''Records measurments to a given file. Usage example:

$ python3 record_measurments.py out.txt'''
import sys
import time
import zmq
import json
import atexit

from rplidar import RPLidar

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.hwm = 2
print(socket.get_hwm())

socket.bind("tcp://*:5556")

PORT_NAME_MAC = '/dev/tty.SLAB_USBtoUART'
PORT_NAME = '/dev/ttyUSB0'

lidar = RPLidar(PORT_NAME)
lidar.connect()

print(lidar.get_health())

lidarArray = [0] * 360

def exit_handler():
    print('Safe Shutdown... Stopping Lidar.')
    lidar.stop()
    print('Done')

atexit.register(exit_handler)

def readLidar():
    '''Main function'''
    
    global lidarArray
    
    count = 0
    
    for measurement in lidar.iter_measurments():
  
        lidarArray[int(measurement[2]) % 360] = measurement[3]
        
        if measurement[0]:
            randomVal = 1
            socket.send_string("[LIDAR]:%s" % (json.dumps(lidarArray, ensure_ascii=True)))
            
if __name__ == '__main__':
    readLidar()
    
    while True:
        i = 1 
        #print(lidarArray)
     

