print("----------------Initialising----------------\n")

print(">Beging Imports")
import zmq
import sys
import time
import struct
import threading
import string
import psutil
import subprocess
print(">DONE\n")

print(">Beging Bluetooth Import")
from bluetooth import *
print(">DONE\n")

#superteams
'''
debugMode = False  #Will stop the automatic restart of programs and any blutooth services active
connected = False

addr = "30:59:B7:0F:C6:B9"
sock = None


# search for the SampleServer service
uuid = "34B1CF4D-1069-4AD6-89B6-E161D79BE4D8"
serviceName = "Australia Robocup"
macAddress = "30:59:B7:0F:C6:B9"


status = subprocess.call("systemctl is-active robotbluetooth.service >/dev/null", shell=True)
if status == 0 and debugMode:
    print(">Stopping Bluetooth Code")
    subprocess.call("systemctl stop robotbluetooth.service", shell=True)
            
def ManagePrograms():
    global debugMode
    
    while not debugMode:
        status = subprocess.call("systemctl is-active mainrobot.service >/dev/null", shell=True)
        if status != 0:
            subprocess.call("systemctl start mainrobot.service", shell=True)
            
            if connected:
                sendMessage("MSG;Main Robot Code Has Stopped! Code Has Been Restarted.")
            else:
                print("\n>Main Robot Code Has Stopped! Code Has Been Restarted.\n")
        
        status = subprocess.call("systemctl is-active lidar.service >/dev/null", shell=True)
        if status != 0:
            subprocess.call("systemctl start lidar.service", shell=True)
            
            if connected:
                sendMessage("MSG;Lidar Code Has Stopped! Code Has Been Restarted.")
            else:
                print("\n>Lidar Code Has Stopped! Code Has Been Restarted.\n")
        
        
        status = subprocess.call("systemctl is-active motors.service >/dev/null", shell=True)
        if status != 0:
            subprocess.call("systemctl start motors.service", shell=True)
            
            if connected:
                sendMessage("MSG;Motor Code Has Stopped! Code Has Been Restarted.")
            else:
                print("\n>Motor Code Has Stopped! Code Has Been Restarted.\n")
                
        time.sleep(3)
        
def SndSytmDiag():
    global connected
    while True:
        if connected:
            sendMessage("CPU;"+str(psutil.cpu_percent()))
            sendMessage("MEM;"+str(psutil.virtual_memory().percent))
        else:
            sock.close()
            connect()
        time.sleep(0.5)

def sendMessage(theMessage):
    global connected
    
    try:
        theMessage = str(theMessage)
        theTuple = struct.unpack("4b", struct.pack("I", len(theMessage)))
        message = chr(theTuple[3] % 256) + chr(theTuple[2] % 256) + chr(theTuple[1] % 256) + chr(theTuple[0] % 256) + theMessage.encode('ascii')
        print(message)
        
        sock.send(message)
    except Exception, e:
        print(e)
        print(connected)
        connected = False
        
def connect():
    global sock
    global connected
    
    print(">Ready To Conect")
    # Connect to the Surface or fail and just manage programs
    TimeoutCount = 0
    while not connected:
        service_matches = find_service( uuid = uuid, address = addr )
        TimeoutCount += 1
        if len(service_matches) == 0:
            print(">Could Not Find Microsoft Surface. Try #%i."%(TimeoutCount))
            time.sleep(1)
        else:
            connected = True
            print(">Found A Surface")
        
    
    first_match = service_matches[0]
    port = first_match["port"]
    name = first_match["name"]
    host = first_match["host"]
    print(">Connected To \"%s\" on %s" % (name, host))

    
    # Create the client socket
    sock=BluetoothSocket( RFCOMM )
    sock.connect((host, port))    

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

connect()

diagnostics = threading.Thread(target=SndSytmDiag)
diagnostics.daemon = True
diagnostics.start()

while True:
    global connected
    
    if connected:
        sendMessage(BluetoothZMQ.recv_string().split(":")[1])
    time.sleep(0.1)
'''

def sendMessage(messageToSend):
    server_sock=BluetoothSocket( RFCOMM )
    server_sock.bind(("",PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]

    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

    advertise_service( server_sock, messageToSend,
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ], 
                    )

print("------------Bluetooth Communication-------------\n")
context = zmq.Context()
BluetoothZMQ = context.socket(zmq.SUB)
BluetoothZMQ.connect("tcp://localhost:5558")

filter = "[SUPER]"
filter = filter.decode('ascii')
BluetoothZMQ.setsockopt_string(zmq.SUBSCRIBE, filter)
    
sendMessage(BluetoothZMQ.recv_string())


'''
stringMap = BluetoothZMQ.recv_string().split(":")

    theTuple = struct.unpack("4b", struct.pack("I", len(stringMap[1])))
    
    print(theTuple)
    
    message = chr(theTuple[3] % 256) + chr(theTuple[2] % 256) + chr(theTuple[1] % 256) + chr(theTuple[0] % 256) + stringMap[1].encode('ascii')
    print(message)
    
    sock.send(message)
'''