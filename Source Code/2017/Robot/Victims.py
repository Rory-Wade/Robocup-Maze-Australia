import serial
import time
import Adafruit_GPIO.I2C as I2C
I2C.require_repeated_start()

RescueKitsLeft = 6
RescueKitsRight = 6

class MLX90614:

    def __init__(self, address=0x5A):
        self._i2c = I2C.Device(address,busnum=2)

    def get_amb_temp(self):
        return self._readTemp(0x06)

    def get_obj_temp(self):
        return self._readTemp(0x07)

    def get_obj2_temp(self):
        return self._readTemp(0x08)

    def _readTemp(self, reg):
        temp = 1000
        while temp > 100 or temp < -100:
            try:
                temp = self._i2c.readS16(reg)
                temp = temp * .02 - 273.15
            except Exception, e:
                print(e)
        return temp
        
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

RightHeat =  MLX90614(address=0x5b)
LeftHeat = MLX90614(address=0x5a)

victimHeat = 27.7
MaxVictimHeat = 70

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

def readHeat(side):
    if side == 0:
        heat = LeftHeat
    else:
        heat = RightHeat
        
    if heat.get_obj_temp() > victimHeat and heat.get_obj_temp() < MaxVictimHeat:
        print(heat.get_obj_temp())
        return [side,2]
    return [side,0]
    

def readCamera(side,camPort):
    while camPort.inWaiting() > 0:
        camData = camPort.readline()
        
        
        if "H" in camData:
            camPort.reset_input_buffer()
            return [side,3]
        elif "S" in camData:
            camPort.reset_input_buffer()
            return [side,2]
        elif "U" in camData:
            camPort.reset_input_buffer()
            return [side,1]
        else:
            print("Data Received from Cam %i : %s"%(side,camData))
    camPort.reset_input_buffer()
    return[side,0]

def dropRescueKit(drop,amount,side):
    global RescueKitsRight
    global RescueKitsLeft
    
    if not drop:
        return False
    
    if side == 0:
        if amount > 1:
            if RescueKitsLeft > 0:
                RescueKitsLeft -= 1
                LeftCam.write("D1\n")
                time.sleep(1)
            else:
                LeftCam.write("D2\n")
                time.sleep(0.2)
                LeftCam.write("D2\n")
                time.sleep(0.2)
                LeftCam.write("D2\n")
                time.sleep(0.2)
                LeftCam.write("D2\n")
                time.sleep(0.2)
                LeftCam.write("D2\n")
                time.sleep(5)
            time.sleep(0.3)
            LeftCam.reset_input_buffer()
                

            if amount > 2:
                RescueKitsLeft -= 1
                LeftCam.write("D1\n")
                time.sleep(0.1)
                LeftCam.reset_input_buffer()
                time.sleep(1)
                
            if LeftCam.inWaiting() > 0:
                camData = LeftCam.readline()
                LeftCam.reset_input_buffer()
                
                if "OK" in camData:
                    return True
                else:
                    return False
            else:
                return False
        else:
            flashLEDs(0)
    else:
        if amount > 1:
            LeftCam.reset_input_buffer()
            if RescueKitsRight > 0:
                RightCam.write("D1\n")
                RescueKitsRight -= 1
                time.sleep(1)
            else:
                RightCam.write("D2\n")
                time.sleep(0.2)
                RightCam.write("D2\n")
                time.sleep(0.2)
                RightCam.write("D2\n")
                time.sleep(0.2)
                RightCam.write("D2\n")
                time.sleep(0.2)
                RightCam.write("D2\n")
                time.sleep(5)
            time.sleep(0.3)
            RightCam.reset_input_buffer()

            if amount > 2:
                RescueKitsRight -= 1
                RightCam.write("D1\n")
                time.sleep(0.1)
                RightCam.reset_input_buffer()
                time.sleep(1)
                
            if RightCam.inWaiting() > 0:
                camData = RightCam.readline()
                RightCam.reset_input_buffer()
                
                if "OK" in camData:
                    return True
                else:
                    return False
            else:
                return False
        else:
            flashLEDs(1)
            
            
def resetCamBuffer():
    LeftCam.reset_input_buffer()
    RightCam.reset_input_buffer()

def flashLEDs(side):
    if side == 0:
        LeftCam.write("D2\n")
        time.sleep(0.1)
        LeftCam.write("D2\n")
        time.sleep(0.1)
        LeftCam.write("D2\n")
        time.sleep(0.1)
        LeftCam.write("D2\n")
        time.sleep(0.1)
        LeftCam.write("D2\n")
        time.sleep(4.6)
        LeftCam.reset_input_buffer()
        
    elif side == 1:
        RightCam.write("D2\n")
        time.sleep(0.1)
        RightCam.write("D2\n")
        time.sleep(0.1)
        RightCam.write("D2\n")
        time.sleep(0.1)
        RightCam.write("D2\n")
        time.sleep(0.1)
        RightCam.write("D2\n")
        time.sleep(4.6)
        RightCam.reset_input_buffer()
    elif side == 3:
        LeftCam.write("D2\n")
        RightCam.write("D2\n")

        LeftCam.write("D2\n")
        RightCam.write("D2\n")
        
        LeftCam.write("D2\n")
        RightCam.write("D2\n")
        
        LeftCam.write("D2\n")
        RightCam.write("D2\n")
        
        LeftCam.write("D2\n")
        RightCam.write("D2\n")
        
        time.sleep(5)
        resetCamBuffer()
    else:
        LeftCam.write("D2\n")
        RightCam.write("D2\n")

        LeftCam.write("D2\n")
        RightCam.write("D2\n")
        time.sleep(2)
        resetCamBuffer()
        
if __name__ == "__main__":    
    while True:
        #print(readHeat(0))
        #print(readHeat(1))
        print(RightHeat.get_obj_temp())
        print(LeftHeat.get_obj_temp())
        time.sleep(1)
        
    
