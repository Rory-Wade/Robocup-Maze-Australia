import serial
import time
# O1 = left
# O4 = right

port = serial.Serial(
    '/dev/ttyS1',
    baudrate=19200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
    )

value = 0

while True:
    port.write("D1\n")
    time.sleep(1)
    cameraData = port.readline() 
    print(cameraData)
    time.sleep(1)
    

        
