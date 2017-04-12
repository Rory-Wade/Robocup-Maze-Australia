import zmq
import time
import json

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.CONFLATE, 1)
socket.connect("tcp://localhost:5556")

filter = "[LIDAR]"
filter = filter.decode('ascii')
socket.setsockopt_string(zmq.SUBSCRIBE, filter)

while True:
    lidarINPUT = socket.recv_string().split(":")
    lidarINPUT = json.loads(lidarINPUT[1])
    
    print("N: %s E: %s S: %s W: %s \n\n\n\n " % (lidarINPUT[0],lidarINPUT[9],lidarINPUT[18],lidarINPUT[27],))
