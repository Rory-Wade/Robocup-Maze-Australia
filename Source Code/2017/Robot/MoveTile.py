import zmq
import time
import json
from Accel import *

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.CONFLATE, 1)
socket.connect("tcp://localhost:5556")

motors = context.socket(zmq.REQ)
motors.connect("tcp://localhost:5557")

filter = "[LIDAR]"
filter = filter.decode('ascii')
socket.setsockopt_string(zmq.SUBSCRIBE, filter)

global currentDirection
currentDirection = 0

def turn(currentAngle,toAngle):
    
    if currentAngle == None:
        time.sleep(0.05)
        return turn(getCurrentAngle(),toAngle)
    movingForward = False
    
    #MoveMotors
    #LEFT SIDE RIGHT SIDE
    if abs((currentAngle - toAngle) % 360) < 3:
        StopMotors()
        movingForward = True
        return True
    elif abs((currentAngle - toAngle) % 360) < 180:
        #LEFT
        #WHERE THE CODE GOES
        rightMotorSpeed = (abs(abs(currentAngle - toAngle) % 360) / 180) * 70 + 5
        leftMotorSpeed = -((abs(abs(currentAngle - toAngle) % 360) / 180) * 70) - 5
        #print(leftMotorSpeed)
        #print(rightMotorSpeed)
        MoveMotors(leftMotorSpeed,rightMotorSpeed)
    else:
        #RIGHT
        #WHERE THE CODE GOES
        leftMotorSpeed = (abs(abs(currentAngle - toAngle) % 360) / 180) * 70 + 5
        rightMotorSpeed = -((abs(abs(currentAngle - toAngle) % 360) / 180) * 70) - 5
        #print(leftMotorSpeed)
        #print(rightMotorSpeed)
        #print(currentAngle, toAngle)
        MoveMotors(leftMotorSpeed,rightMotorSpeed)
    time.sleep(0.05)
    return turn(getCurrentAngle(),toAngle)

def callMotors(direction):
    #do something here?
    print("DIRECTION TO MOVE")
    print(direction)
    if direction == 1:
        #TURN RIGHT
        turn(getCurrentAngle(),90)
    elif direction == 3:
        #TURN LEFT
        turn(getCurrentAngle(),270)
        
def moveDirection(direction):
    global currentDirection
    
    print("DIRECTION TO MOVE %i" % (direction))
    currentDirection = direction
    print("Current DIRECTION TO MOVE %i" % (currentDirection))
    
    
    if direction == 0:
        turn(getCurrentAngle(),0)
    elif direction == 1:
        turn(getCurrentAngle(),90)
    elif direction == 2:
        turn(getCurrentAngle(),180)
    elif direction == 3:
        turn(getCurrentAngle(),270)
    

def readLidar():
    lidarINPUT = socket.recv_string().split(":")
    lidarINPUT = json.loads(lidarINPUT[1])
    return lidarINPUT
    
def MoveMotors(Linput,Rinput):
    motors.send(b"%i,%i" % (Linput,Rinput))
    message = motors.recv()
    
def StopMotors():
    motors.send(b"%i,%i" % (0,0))
    message = motors.recv()
    
print("ONLINE")

while True:
    lidarArray = readLidar()

    if lidarArray[0] > 200:
        #print("N: %s E: %s S: %s W: %s \n\n\n\n " % (lidarINPUT[0],lidarINPUT[9],lidarINPUT[18],lidarINPUT[27],))
        MoveMotors(40,40)
    else:
        MoveMotors(0,0)
        if currentDirection == 0:
            print("Turn 2 current: %i" % (currentDirection))
            moveDirection(2)
        else:
            print("Turn 0 current: %i" % (currentDirection))
            moveDirection(0)
        
    