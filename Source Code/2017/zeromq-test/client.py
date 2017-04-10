#
#   Weather update client that drops older messages
#   Connects SUB socket to tcp://localhost:5556
#   Collects weather updates and finds avg temp in zipcode
#

import zmq
import time

#  Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.CONFLATE, 1)

print("Collecting updates from weather server...")
socket.connect("tcp://localhost:5556")

zip_filter = "0" 

# Python 2 - ascii bytes to unicode str
if isinstance(zip_filter, bytes):
    zip_filter = zip_filter.decode('ascii')
socket.setsockopt_string(zmq.SUBSCRIBE, zip_filter)

# Process 5 updates
total_temp = 0
for update_nbr in range(5):
    string = socket.recv_string()
    zipcode, temperature, relhumidity = string.split()
    total_temp += int(temperature)
    print("got temp", (temperature))
    time.sleep(1)
