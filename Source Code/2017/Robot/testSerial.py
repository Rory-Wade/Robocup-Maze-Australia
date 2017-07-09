import serial
import time
# O1 = left
# O4 = right

port = serial.Serial(
    '/dev/ttyO1',
    baudrate=19200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
    )

value = 0
while True:
    cameraData = port.readline() 
    print(cameraData)
    if "H" in cameraData:
        print("FOUND AN H")
        port.reset_input_buffer()
        port.write("D1")
        time.sleep(4)
        print(port.readline())
        
