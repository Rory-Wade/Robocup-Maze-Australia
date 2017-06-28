import serial

port = serial.Serial(
    '/dev/ttyO1',
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
    )

value = 0
while True:
    print port.read()
    value += 1
    port.write("Hello from beaglebone! %i\n" % value)