import zmq
from bluetooth import *
import sys
import time
import struct
import threading
import string
import psutil
from subprocess import call


context = zmq.Context()
BluetoothZMQ = context.socket(zmq.SUB)
BluetoothZMQ.connect("tcp://localhost:5558")

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

def sendSystemDiagnostics():
    while True:
        sendMessage("CPU;"+str(psutil.cpu_percent()))
        sendMessage("MEM;"+str(psutil.virtual_memory().percent))
        time.sleep(1)

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
        print(data)
        time.sleep(0.2)
        
bluetoothRecieve = threading.Thread(target=recieveLoop)

bluetoothRecieve.daemon = True

bluetoothRecieve.start()

diagnostics = threading.Thread(target=sendSystemDiagnostics)

diagnostics.daemon = True

diagnostics.start()

while True:
    #data = sock.recv(1024)
    #print(data)
    
    stringMap = BluetoothZMQ.recv_string().split(":")
    #print([ord(c) for c in data])

    theTuple = struct.unpack("4b", struct.pack("I", len(stringMap[1])))
    
    print(theTuple)
    
    message = chr(theTuple[3] % 256) + chr(theTuple[2] % 256) + chr(theTuple[1] % 256) + chr(theTuple[0] % 256) + stringMap[1].encode('ascii')
    print(message)
    
    sock.send(message)
    
    time.sleep(0.1)
    
    #sock.send(data)
    
    

sock.close()