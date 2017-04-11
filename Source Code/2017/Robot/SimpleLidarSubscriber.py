import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.CONFLATE, 1)
socket.connect("tcp://localhost:5556")

filter = "[LIDAR]"
filter = filter.decode('ascii')
socket.setsockopt_string(zmq.SUBSCRIBE, filter)

while True:
    string = socket.recv_string()
    print("Got: %s\n\n\n\n " % (string))
