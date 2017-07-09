import serial
import time
import zmq

LeftCam = serial.Serial(
    '/dev/ttyO1',
    baudrate=19200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
    )

RightCam = serial.Serial(
    '/dev/ttyO4',
    baudrate=19200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
    )
    
#char return
# 3 = S 
# 2 = H
# 1 = U
# 0 = NOTHING

#side return
# 0 = L
# 1 = R

#data structure
#[side,char]

def readCamera(side,camPort):
    if camPort.inWaiting() > 0:
        camData = camPort.readline()
        camPort.reset_input_buffer()
        
        if "H" in camData:
            return [side,2]
        elif "S" in camData:
            return [side,3]
        elif "U" in camData:
            return [side,1]
        else:
            print("Data Received from Cam %i : %s"%(side,camData))
    return[side,0]

def dropRescueKit(drop,amount,side):
    if not drop:
        return False
    
    if side == 0:
        if amount > 1:
            LeftCam.write("D1")
            time.sleep(2)
        
        LeftCam.write("D1")
    else:
        if amount > 1:
            RightCam.write("D1")
            time.sleep(2)
        
        RightCam.write("D1")


if __name__ == "__main__":    
    while True:
        print(readCamera(0,LeftCam))
        time.sleep(1)
        
    
