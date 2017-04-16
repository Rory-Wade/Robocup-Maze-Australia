import zmq
import time
import json
import atexit
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

KP = 0.5
KI = 0.01
KD = 0.1

integral = 0
derivative = 0
proportion = 0

last_error = 0

baseMotorSpeed = 45

tileSize = 320

def exit_handler():
    print 'Program Shutting Down...'
    StopMotors()
    
atexit.register(exit_handler)

def turn(currentAngle,toAngle):
    
    if currentAngle == None:
        time.sleep(0.05)
        return turn(getCurrentAngle(),toAngle)
    movingForward = False
    
    if abs((currentAngle - toAngle) % 360) < 3:
        StopMotors()
        movingForward = True
        return True
    elif abs((currentAngle - toAngle) % 360) < 180:

        rightMotorSpeed = (abs(abs(currentAngle - toAngle) % 360) / 180) * 70 + 5
        leftMotorSpeed = -((abs(abs(currentAngle - toAngle) % 360) / 180) * 70) - 5

        MoveMotors(leftMotorSpeed,rightMotorSpeed)
    else:

        leftMotorSpeed = (abs(abs(currentAngle - toAngle) % 360) / 180) * 70 + 5
        rightMotorSpeed = -((abs(abs(currentAngle - toAngle) % 360) / 180) * 70) - 5

        MoveMotors(leftMotorSpeed,rightMotorSpeed)
    time.sleep(0.05)
    return turn(getCurrentAngle(),toAngle)

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

def relativeTurn(direction):
    global currentDirection
    
    direction = (currentDirection + direction) % 4
    moveDirection(direction)

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

def MovingForward(lidarData):
    if numberFitsEnvelope(lidarData[0], 15):
        print("FITS THE ENVELOPE MY DUDE")
        return False
    return True
    
def numberFitsEnvelope(number, envelope):
    if number < (150) or abs((number % tileSize) - (tileSize / 2)) < (tileSize / envelope):
        return True
    return False
    
def PID():
    global proportion
    global integral
    global derivative
    global last_error
    
    angle = getCurrentAngle()
    
    if currentDirection == 0:
        if angle > 180:
            angle = (360 - angle) * -1 
        
    else:
        angle = ((90 * currentDirection)  - angle) * -1
    
    proportion = angle
    
    integral  += proportion
    derivative = proportion - last_error
    last_error = proportion
    
    turn = KP*proportion + KI*integral + KD*derivative
    
    #print("Motor speed indifferent: %f %f" % (turn,angle))
    MoveMotors(baseMotorSpeed - turn,baseMotorSpeed + turn)  
    
print("ONLINE")

while True:
    lidarArray = readLidar()

    if MovingForward(lidarArray):
        
        #MoveMotors(40,40)
        PID()
    else:
        StopMotors()
        
        print("----LIDAR MEASUREMENTS REL----")
        print("  LEFT, RIGHT, FORWARD, BACK")
        print(lidarArray[9],lidarArray[27],lidarArray[0],lidarArray[18])
        print("------------------------------")

        
        if lidarArray[0] > 350:
            relativeTurn(0)
        elif lidarArray[9] > 350:
            relativeTurn(1)
        elif lidarArray[27] > 350:
            relativeTurn(3)
        elif lidarArray[18] > 350:
            relativeTurn(2)
            
            
        
    