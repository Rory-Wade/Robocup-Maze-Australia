import zmq
from bluetooth import *
import sys
import time
import struct
import threading
import string
import psutil
import subprocess
connected = False

def ManagePrograms():
    while True:
        status = subprocess.call("systemctl is-active mainrobot.service >/dev/null", shell=True)
        if status != 0:
            subprocess.call("systemctl start mainrobot.service", shell=True)
            
            if connected:
                sendMessage("MSG;Main Robot Code Has Stopped! Code Has Been Restarted.")
            else:
                print(">Main Robot Code Has Stopped! Code Has Been Restarted.")
        
        status = subprocess.call("systemctl is-active lidar.service >/dev/null", shell=True)
        if status != 0:
            subprocess.call("systemctl start lidar.service", shell=True)
            
            if connected:
                sendMessage("MSG;Lidar Code Has Stopped! Code Has Been Restarted.")
            else:
                print(">Lidar Code Has Stopped! Code Has Been Restarted.")
        
        
        status = subprocess.call("systemctl is-active motors.service >/dev/null", shell=True)
        if status != 0:
            subprocess.call("systemctl start motors.service", shell=True)
            
            if connected:
                sendMessage("MSG;Motor Code Has Stopped! Code Has Been Restarted.")
            else:
                print(">Motor Code Has Stopped! Code Has Been Restarted.")
                
        time.sleep(3)
        
def SndSytmDiag():
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


print("------------Bluetooth Communication-------------\n")
context = zmq.Context()
BluetoothZMQ = context.socket(zmq.SUB)
BluetoothZMQ.connect("tcp://localhost:5558")

filter = "[BLUE]"
filter = filter.decode('ascii')
BluetoothZMQ.setsockopt_string(zmq.SUBSCRIBE, filter)
        
diagnostics = threading.Thread(target=ManagePrograms)
diagnostics.daemon = True
diagnostics.start()

addr = None

# search for the SampleServer service
uuid = "34B1CF4D-1069-4AD6-89B6-E161D79BE4D8"

# Connect to the Surface or fail and just manage programs
TimeoutCount = 0
while not connected:
    service_matches = find_service( uuid = uuid, address = addr )
    TimeoutCount += 1
    if len(service_matches) == 0:
        print(">Could Not Find MicroSoft Surface. Try #%i."%(TimeoutCount))
        time.sleep(1)
    else:
        connected = True
        print(">Connected To The Surface")
    

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

diagnostics = threading.Thread(target=SndSytmDiag)
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