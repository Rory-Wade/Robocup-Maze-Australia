import zmq
from random import randrange

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.set_hwm(1)


socket.bind("tcp://*:5556")

temperature = 0
while True:
    temperature = temperature + 1 # randrange(-80, 135)
    relhumidity = randrange(10, 60)

    socket.send_string("%s %i %i" % ("Accelerometer", temperature, relhumidity))