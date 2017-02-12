'''Records measurments to a given file. Usage example:

$ python3 record_measurments.py out.txt'''
import sys
from rplidar import RPLidar


PORT_NAME = '/dev/ttyUSB0'


def readLidar():
    '''Main function'''
    lidar = RPLidar(PORT_NAME)

    try:
        print('Recording measurments... Press Crl+C to stop.')

        for measurment in lidar.iter_measurments():
            print('measurment')
            #line = '\t'.join(str(v) for v in measurment)
            
    except KeyboardInterrupt:
        print('Stoping.')

    lidar.stop()
    lidar.disconnect()

if __name__ == '__main__':
    readLidar()
