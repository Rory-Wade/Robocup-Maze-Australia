import time, sched
import math
import zmq
import json

#from MotorMovement import *

#X,Y
#Y goes up when the robot goes up
#X goes up when the robot goes right
#ALL COORDINATES ARE Y,X

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

motors = context.socket(zmq.REQ)
motors.connect("tcp://localhost:5556")

tileSize = 300
readNum = 0

def MoveMotors(Linput,Rinput):
    motors.send(b"%i,%i" % (Linput,Rinput))
    message = motors.recv()
    #print(message)
    
def numberFitsEnvelope(number, desired, envelope):
    if abs(number - desired) < envelope:
        return True
    return False

def getLidarValues():
    global readNum
    readNum += 1
    #print("------------------------")
    tsOne = time.time()
    socket.send(b"" + str(readNum))
    while True:
        message = socket.recv().split(":")
        messageCheck = message[0]
        
        if messageCheck == str(readNum):

            message = json.loads(message[1])
            var = message[180]
            print(tsOne - time.time())
            return message

'''while True:
    lidarData = getLidarValues()
    front = lidarData[0]
    if numberFitsEnvelope(front % tileSize,tileSize / 2,tileSize / 10):
        #print("TILE'D")
        print(front)
        MoveMotors(0,0)
    else:
        print("NOT TILE'D")
        MoveMotors(5,5)
    time.sleep(0.5)
   '''
while True:
    lidar = getLidarValues()
    time.sleep(0.1)
    '''for i in range(0,198):
        if i <= 99:
            print(i)
            MoveMotors(i,i)
        else:
            print(198 - i)
            MoveMotors(198 - i,198 - i)
        time.sleep(0.1)'''


