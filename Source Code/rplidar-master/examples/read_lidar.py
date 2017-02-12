'''Records measurments to a given file. Usage example:

$ Averge Output Speed: 0.815s'''
import sys
import time
#import threading

from rplidar import RPLidar

PORT_NAME = '/dev/ttyUSB0'
AVGLOOP = 5 #amount of scans averaged before release


def scanLidar():
    '''LIDAR START SCAN'''
    lidar = RPLidar(PORT_NAME)

    try:
        print("Lidar Satus: {}\tCode: {} \n Recording measurments... Press Crl+C to stop.".format(lidar.get_health()[0], lidar.get_health()[1])) #find exception before function start

        lidarReadingsAVG = [None] * 360
        currLoop = 0
        scanTime = 0
        startTime = time.time()
        
        for measurment in lidar.iter_measurments():

            line = '\t'.join(str(v) for v in measurment)
            
            if measurment[0] == True:
                currLoop += 1
            
                if currLoop % AVGLOOP == 0:
                    scanTime = (scanTime + (time.time() - startTime))/2
                    startTime = time.time()
                    
                    print("\nLoop: {} scan time: {} timestamp: {} Readings: \n\n{}".format(currLoop, scanTime , time.time(),lidarReadingsAVG))
                   
                    lidarReadingsAVG = [None] * 360

            try:
                if lidarReadingsAVG[int(measurment[2]) % 360] != None:
                    lidarReadingsAVG[int(measurment[2]) % 360] = float(format((lidarReadingsAVG[int(measurment[2]) % 360] + measurment[3])/2, '.3f'))
                else:
                    lidarReadingsAVG[int(measurment[2]) % 360] = float(format(measurment[3], '.3f'))
                    
            except IndexError:  
                print("\nMeasurement out of range! -> {}".format(int(measurment[2])))
                
    except KeyboardInterrupt:
        t.stop() 
        print('\nStoping Scan!')
        
    lidar.stop_motor()
    lidar.stop()
    lidar.disconnect()

if __name__ == '__main__':
   

    #thread.start_new_thread(scanLidar,())
    try:
         #t=threading.Thread(target=scanLidar)
        scanLidar()
    except:
        scanLidar()
         #t=threading.Thread(target=scanLidar)
         
    #t.daemon = False  # set thread to daemon ('ok' won't be printed in this case)
    #t.run()  
    
