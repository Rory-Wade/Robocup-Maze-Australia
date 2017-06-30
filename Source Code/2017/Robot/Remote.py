import zmq
from bluetooth import *
import sys
import time
import struct
import threading
import string
import psutil
from subprocess import call

import unicodedata, re

all_chars = (unichr(i) for i in xrange(0x110000))
control_chars = ''.join(c for c in all_chars if unicodedata.category(c) == 'Cc')
# or equivalently and much more efficiently
control_chars = ''.join(map(unichr, range(0,32) + range(127,160)))

control_char_re = re.compile('[%s]' % re.escape(control_chars))

def remove_control_chars(s):
    return control_char_re.sub('', s)

context = zmq.Context()
BluetoothZMQ = context.socket(zmq.SUB)
BluetoothZMQ.connect("tcp://localhost:5558")

motors = context.socket(zmq.REQ)
motors.connect("tcp://localhost:5557")

filter = "[BLUE]"
filter = filter.decode('ascii')
BluetoothZMQ.setsockopt_string(zmq.SUBSCRIBE, filter)

if sys.version < '3':
    input = raw_input

addr = None

if len(sys.argv) < 2:
    print("no device specified.  Searching all nearby bluetooth devices for")
    print("the SampleServer service")

else:
    addr = sys.argv[1]
    print("Searching for SampleServer on %s" % addr)

# search for the SampleServer service
uuid = "34B1CF4D-1069-4AD6-89B6-E161D79BE4D8"
service_matches = find_service( uuid = uuid, address = addr )


if len(service_matches) == 0:
    print("couldn't find the SampleServer service =(")
    sys.exit(0)

first_match = service_matches[0]
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]

print("connecting to \"%s\" on %s" % (name, host))

# Create the client socket
sock=BluetoothSocket( RFCOMM )
sock.connect((host, port))

print("connected.  type stuff")
#client_sock, client_info = sock.accept()

"""def sendSystemDiagnostics():
    while True:
        sendMessage("CPU;"+str(psutil.cpu_percent()))
        sendMessage("MEM;"+str(psutil.virtual_memory().percent))
        time.sleep(1)"""
        
        
def MoveMotors(Linput,Rinput):
    motors.send(b"%i,%i" % (Linput,Rinput))
    message = motors.recv()

def sendMessage(theMessage):
    theMessage = str(theMessage)
    theTuple = struct.unpack("4b", struct.pack("I", len(theMessage)))
    message = chr(theTuple[3] % 256) + chr(theTuple[2] % 256) + chr(theTuple[1] % 256) + chr(theTuple[0] % 256) + theMessage.encode('ascii')
    print(message)
    
    sock.send(message)

def recieveLoop():
    while True:
        data = sock.recv(1024)
        if 'B:' in data:
            command = data.split("B:")[1]
            stringCall = call(command.split(" "))
            #sendMessage(stringCall)
        elif 'M:' in data:
            command = data.split("M:")[1]
            motorCommands = command.split(",")
            motorCommands = [remove_control_chars(motorCommands[0]),remove_control_chars(motorCommands[1])]
            if motorCommands[0] > -200 and motorCommands[1] > -200:
                MoveMotors(int(motorCommands[0]),int(motorCommands[1]))
        print(data)

bluetoothRecieve = threading.Thread(target=recieveLoop)



bluetoothRecieve.daemon = True

bluetoothRecieve.start()

#diagnostics = threading.Thread(target=sendSystemDiagnostics)



#diagnostics.daemon = True

#diagnostics.start()

while True:
    #data = sock.recv(1024)
    #print(data)
    
    #stringMap = BluetoothZMQ.recv_string().split(":")
    #print([ord(c) for c in data])

    #theTuple = struct.unpack("4b", struct.pack("I", len(stringMap[1])))
    
    #print(theTuple)
    
    #message = chr(theTuple[3] % 256) + chr(theTuple[2] % 256) + chr(theTuple[1] % 256) + chr(theTuple[0] % 256) + stringMap[1].encode('ascii')
    #print(message)
    
    #sock.send(message)
    
    time.sleep(0.1)
    
    #sock.send(data)
    
    

sock.close()