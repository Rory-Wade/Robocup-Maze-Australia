#
#   Weather update client
#   Connects SUB socket to tcp://localhost:5556
#   Collects weather updates and finds avg temp in zipcode
#

import sys
import zmq
import time

#  Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.hwm = 2
socket.connect("tcp://localhost:5556")

# Subscribe to zipcode, default is NYC, 10001
socket_filter = "[LIDAR]"

# Python 2 - ascii bytes to unicode str
if isinstance(socket_filter, bytes):
    socket_filter = socket_filter.decode('ascii')
socket.setsockopt_string(zmq.SUBSCRIBE, socket_filter)

# Process 5 updates
total_temp = 0
while True:
    string = socket.recv_string()
    socketID, array = string.split(":")
    print("Received: %s" % (array))
    time.sleep(1)