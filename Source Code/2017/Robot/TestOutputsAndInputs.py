import time
import subprocess

#True - ALL READ OUT
#False - MAIN MESSEGES
Verbose = False

errors = 0

def clearTerminal():
    time.sleep(3)
    for i in range(10):
        print("\n")
        
print("------------INITIALISING-------------\n")
print("Testing All Vital Parts of the robot\n")

print("-->Checking Main Code Status")
status = subprocess.call("systemctl is-active mainrobot.service", shell=True)
if status == 0:
    print("STOPPING MAIN PROGRAM!")
    subprocess.call("systemctl stop mainrobot.service", shell=True)

time.sleep(1) 

print("-->Checking Lidar Status")    
status = subprocess.call("systemctl is-active lidar.service", shell=True)
if status > 0:
    print("STARTING LIDAR PROGRAM!")
    subprocess.call("systemctl start lidar.service", shell=True)
    
time.sleep(1)

print("-->Checking Morots Status")    
status = subprocess.call("systemctl is-active motors.service", shell=True)
if status > 0:
    print("STARTING MOTORS PROGRAM!")
    subprocess.call("systemctl start motors.service", shell=True)
    
print("\nDONE\n")
time.sleep(1)
print("-->Initialising the ZMQ")
import zmq
context = zmq.Context()

lidar = context.socket(zmq.SUB)
lidar.setsockopt(zmq.CONFLATE, 1)
lidar.connect("tcp://localhost:5556")

bluetooth = context.socket(zmq.PUB)
bluetooth.set_hwm(7)
bluetooth.bind("tcp://*:5558")

motors = context.socket(zmq.REQ)
motors.connect("tcp://localhost:5557")

filter = "[LIDAR]"
filter = filter.decode('ascii')
lidar.setsockopt_string(zmq.SUBSCRIBE, filter)
print("DONE\n")

print("-->Initialising the Touch")
from Touch import *
print("DONE\n")

print("-->Initialising the Light")
from Light import *
print("DONE\n")

print("-->Initialising the Victim")
from Victims import *
print("DONE\n")

print("-->Initialising the ACCEL")
from Accel import *
print("DONE\n")

print("-------------------------------------\n")
clearTerminal()

print("-------------TOUCH TESTS-------------\n")
print("-->Testing The Pause Button")
print(">Please Push The Pause Button")

PauseButton()
while not PauseButton():
    time.sleep(0.1)
    
    if Verbose:
        print(PauseButton())
    
print("GOOD\n")

print("-->Testing The Touch Sensors")
print(">Please Push All The Touch Sensors Simultaneous")

while not (TouchSensors()[0] and TouchSensors()[1] and TouchSensors()[2] and TouchSensors()[3]):
    time.sleep(0.1)
    
    if Verbose:
        print(TouchSensors())   
        
print("GOOD\n")

print("-------------------------------------\n")
clearTerminal()

print("-------------LIGHT TESTS-------------\n")
print("-->Testing The Left Light Sensor")
print(">Please Put Me On Something With A High Lux")
while valueColour()[0] < 100:
    time.sleep(1)
    
    if Verbose:
        print(valueColour()[0])
print("GOOD\n")

print("-->Testing The Right Light Sensor")
print(">Please Put Me On Something With A High Lux")
while valueColour()[1] < 100:
    time.sleep(1)
    
    if Verbose:
        print(valueColour()[1])
print("GOOD\n")

print("-------------------------------------\n")
clearTerminal()

print("-------------ACCEL TESTS-------------\n")
resetIMU()
print("-->Testing The Accelerometer")
print(">Please Turn The Robot 90deg")

while getCurrentAngle() < 85 or getCurrentAngle() > 265 :
    time.sleep(0.1)
    
    if Verbose:
        print(getCurrentAngle())
print("GOOD\n")

print("-------------------------------------\n")
clearTerminal()


print("-------------VICTM TESTS-------------\n")
print("-->Testing The Left Drop Mechanism and Cams")

if not dropRescueKit(True,2,0):
    print("ERROR ON LEFT SIDE")
    errors += 1
else:
    print("GOOD\n")
    
print("-->Testing The Right Drop Mechanism and Cams") 

if not dropRescueKit(True,2,1):
    print("ERROR ON RIGHT SIDE")
    errors += 1
else:
    print("GOOD\n")

print("-->Testing The Left Heat Sensor") 
print(">Please Place Your Hand In Front Of Left Heat Sensor")
while readHeat(0)[1] < 1:
    time.sleep(0.5)
    
    if Verbose:
        print(readHeat(0)[1])
print("GOOD\n")

print("-->Testing The Right Heat Sensor") 
print(">Please Place Your Hand In Front Of Right Heat Sensor")
while readHeat(1)[1] < 1:
    time.sleep(0.5)
    
    if Verbose:
        print(readHeat(1)[1])
print("GOOD\n")

print("-------------------------------------\n")
clearTerminal()

print("-------------LIDAR TESTS-------------\n")
print("-->Testing The Lidar")
print("->Error has occured when an array has not been printed")
lidarINPUT = lidar.recv_string().split(":")
lidarINPUT = json.loads(lidarINPUT[1])
print(lidarINPUT)    
print("GOOD\n")
print("-------------------------------------\n")
clearTerminal()

print("-------------MOTOR TESTS-------------\n")
print("-->Testing The Motors")
print("->Error has occured when an Good has not been printed")
motors.send(b"%i,%i" % (0,0))
message = motors.recv()
print(message)    
print("GOOD\n")
print("-------------------------------------\n")
print("Test Has Finsihed With %i Error(s)."%(errors))