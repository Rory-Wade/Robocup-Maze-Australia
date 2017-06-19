#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#
import json
import zmq

context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

#  Do 10 requests, waiting each time for a response
for request in range(10):
    print("Sending request %s" % request)
    socket.send("Hello")

    #  Get the reply.
    message = json.loads(socket.recv())
    print("Received reply %s \n [ %s ] \n" % (request, message))