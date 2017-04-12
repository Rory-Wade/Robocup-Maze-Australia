import time, sched
import math
import zmq
import json

from Accel import *
from MotorMovement import *

#X,Y
#Y goes up when the robot goes up
#X goes up when the robot goes right
#ALL COORDINATES ARE Y,X

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

'''KP = 0.5
KI = 0.5
KD = 0.5

readNum = 0

map = []
for width in range(0,99):
    map.append([])
    for height in range(0,99):
        map[width].append(0)
print("COMPLETED MAP CREATION")
coords = [50,50]
explored = []
backtraceArray = [[coords[0],coords[1]]]
tileSize = 300

movingForward = True

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
        turn(getCurrentAngle(),270)'''

#where maptile is 0, then it's unknown and unexplored. 9 is wall, and 1 is explored.
def useLidar(lidarArray):
    directionToGo = useLidarToCalculateNextMotion(lidarArray)
    '''if directionToGo is not None:
        #NEW INSTRUCTIONS MY DUDE
        callMotors(directionToGo)'''

'''def numberFitsEnvelope(number, desired, envelope):
    if abs(number - desired) < envelope:
        return True
    return False'''

def useLidarToCalculateNextMotion(lidarArray):
    global tileSize
    bestForwardsMeasurement = 0.0
    numOfForwards = 0
    bestRightMeasurement = 0.0
    numOfRights = 0
    bestDownMeasurement = 0.0
    numOfDowns = 0
    bestLeftMeasurement = 0.0
    numOfLefts = 0
    '''for i in range(0,(len(lidarArray) - 1)):
        if i == 0:
            #UP VALUES
            if lidarArray[i] is not None:
                numOfForwards += 1
                #length = abs(math.cos(i) * lidarArray[i])
                bestForwardsMeasurement = lidarArray[i]#+= length
        if i == 89:
            #RIGHT VALUES
            if lidarArray[i] is not None:
                numOfRights += 1
                #length = abs(math.cos(i) * lidarArray[i])
                #bestRightMeasurement += length
                bestRightMeasurement = lidarArray[i]
        if i == 179:
            #DOWN VALUES
            if lidarArray[i] is not None:
                numOfDowns += 1
                #length = abs(math.cos(i) * lidarArray[i])
                #bestDownMeasurement += length
                bestDownMeasurement = lidarArray[i]
        if i == 269:
            #LEFT VALUES
            if lidarArray[i] is not None:
                numOfLefts += 1
                #length = abs(math.cos(i) * lidarArray[i])
                #bestLeftMeasurement += length
                bestLeftMeasurement = lidarArray[i]'''


    #if numOfLefts == 0 or numOfRights == 0 or numOfForwards == 0 or numOfDowns == 0:
        #return
    #Make Averages
    #bestLeftMeasurement /= numOfLefts
    #bestRightMeasurement /= numOfRights
    #bestForwardsMeasurement /= numOfForwards
    #bestDownMeasurement /= numOfDowns
    
    #print("----LIDAR MEASUREMENTS----")
    #print("LEFT, RIGHT, FORWARD, BACK")
    #print(bestLeftMeasurement,bestRightMeasurement,bestForwardsMeasurement,bestDownMeasurement)
    #print("--------------------------")
    #movingForward = False
    bestLeftMeasurement, bestRightMeasurement, bestForwardsMeasurement, bestDownMeasurement = lidarArray[269], lidarArray[89], lidarArray[0], lidarArray[179]
    if bestDownMeasurement < 150:
        #global readNum
        MoveMotors(100,100)
    else:
        MoveMotors(10,10)
    '''
    if numberFitsEnvelope(bestForwardsMeasurement % tileSize, tileSize / 2, tileSize / 30) and False:
        #xd number fits what2donow?
        print("FITS THE ENVELOPE MY DUDE")
        StopMotors()
        #time.sleep(5)
        forwardsTiles = int(bestForwardsMeasurement / tileSize)
        backwardsTiles = int(bestDownMeasurement / tileSize)
        leftTiles = int(bestLeftMeasurement / tileSize)
        rightTiles = int(bestRightMeasurement / tileSize)
        return relativePositionCode(forwardsTiles,rightTiles,backwardsTiles,leftTiles)

    return None'''

#CurrentFacingDirection
'''currentFacingDirection = 0
lastSentCoords = []
def relativePositionCode(up,right,down,left):
    global currentFacingDirection
    directions = [up,right,down,left]
    if currentFacingDirection == 1:
        #FACING RIGHT SO, UP BECOMES RIGHT, RIGHT BECOMES DOWN, DOWN BECOMES LEFT AND LEFT BECOMES UP
        directions = [left,up,right,down]
    elif currentFacingDirection == 2:
        #EVERYTHING CHANGES Xdddddddddd
        directions = [down,left,up,right]
    elif currentFacingDirection == 3:
        directions = [right,down,left,up]
    if directions != lastSentCoords:
        #IF FACING 0, GO THE DIRECTION RETURNED, AND SET DIRECTION TO directions
        #SUBTRACT NEW DIRECTION FROM FACING DIRECTION % 4
        returnDirection = DFS(directions[0],directions[1],directions[2],directions[3])
        if returnDirection == -1:
            return
        sendDirection = (returnDirection - currentFacingDirection) % 4
        currentFacingDirection = returnDirection
        return sendDirection
    else:
        print("Orientation Change")
        return None


def changeMap(up,right,down,left):
    for x in range(0,up):
        if map[coords[0] + x][coords[1]] != 1:
            map[coords[0] + x][coords[1]] = 0
    map[coords[0] + up + 1][coords[1]] = 9
    for x in range(0,right):
        if map[coords[0]][coords[1] + x] != 1:
            map[coords[0]][coords[1] + x] = 0
    map[coords[0]][coords[1] + right + 1] = 9
    for x in range(0,down):
        if map[coords[0] - x][coords[1]] != 1:
            map[coords[0] - x][coords[1]] = 0
    map[coords[0] - down - 1][coords[1]] = 9
    for x in range(0,left):
        if map[coords[0]][coords[1] - x] != 1:
            map[coords[0]][coords[1] - x] = 0
    map[coords[0]][coords[1] - left - 1] = 9


def DFS(up,right,down,left):
    #print("------LIDARDATA------")
    #print(up,right,down,left)
    #print("---------------------")
    changeMap(up,right,down,left)
    decided = False
    directionToMove = -1
    map[coords[0]][coords[1]] = 1
    if up > 0 and decided == False:
        nextTile = map[coords[0] + 1][coords[1]]
        print(coords[0] + 1)
        print(coords[1])
        print(map[coords[0] + 1][coords[1]])
        if nextTile == 0:
            decided = True
            #Move up
            coords[0] += 1
            directionToMove = 0
    if right > 0 and decided == False:
        nextTile = map[coords[0]][coords[1] + 1]
        if nextTile == 0:
            decided = True
            #Move right
            coords[1] += 1
            directionToMove = 1
    if down > 0 and decided == False:
        nextTile = map[coords[0] - 1][coords[1]]
        if nextTile == 0:
            decided = True
            #Move down
            coords[0] -= 1
            directionToMove = 2
    if left > 0 and decided == False:
        nextTile = map[coords[0]][coords[1] - 1]
        if nextTile == 0:
            decided = True
            #Move left
            coords[1] -= 1
            directionToMove = 3
    if directionToMove != -1:
        print("Found a direction to move")
        #Exploration logic found a solution, should not backtrack
        backtraceArray.append([coords[0],coords[1]])
        return directionToMove
    elif len(backtraceArray) >= 1:
        print("Backtracing")
        #Exploration logic failed to find a solution, needs to backtrack
        backtracePoint = backtraceArray.pop()
        print(coords)
        print(backtracePoint)
        if coords[0] > backtracePoint[0]:
            #Needs to go DOWN
            directionToMove = 2
            coords[0] -= 1
            return directionToMove
        if coords[0] < backtracePoint[0]:
            #Needs to go UP
            directionToMove = 0
            coords[0] += 1
            return directionToMove
        if coords[1] > backtracePoint[1]:
            #Needs to go LEFT
            directionToMove = 3
            coords[1] -= 1
            return directionToMove
        if coords[1] < backtracePoint[1]:
            #Needs to go RIGHT
            directionToMove = 1
            coords[1] += 1
            return directionToMove
    print("There are no valid solutions")
    return -1
    
#s = sched.scheduler(time.time, time.sleep)


lastError = 0
integral = 0
derivative = 0
proportion = 0'''

def getLidarValues():
    global readNum
    readNum += 1
    #print("Sent Message")
    socket.send(b"" + str(readNum))
    #  Get the reply.
    while True:
        message = socket.recv().split(":")
        messageCheck = message[0]
        
        if messageCheck == str(readNum):
            #print("Matched")
            message = json.loads(message[1])
            return message
        #print("Didn't match")
        
    
    
def moveForward():
    #print("CALLED IT")
    lidarData = getLidarValues()
    useLidar(lidarData)
    '''global tileSize
    global KP, KI, KD
    if lidarData != None:
        
        #print(len(lidarData))
        #print(lidarData[0])
        #lidarData = list(lidarData)
        #print("___")
        #print(lidarData[2])
        
        #lidarData = lidarData[3]
        
        if movingForward:
            #print(lidarData)
            pidValOneOffset = 15
            pidValTwoOffset = 15
            leftOnePidVal = lidarData[270 + pidValOneOffset]
            rightOnePidVal = lidarData[90 - pidValOneOffset]
            leftTwoPidVal = lidarData[270]
            rightTwoPidVal = lidarData[90]
            leftThreePidVal = lidarData[270 - pidValTwoOffset]
            rightThreePidVal = lidarData[90 + pidValTwoOffset]
            #divide dist by cos(30) to get the trig value
            modOne = math.cos(pidValOneOffset)/tileSize
            modTwo = math.cos(pidValTwoOffset)/tileSize
    
            if leftTwoPidVal == None or rightTwoPidVal == None:
                #s.enter(0.5, 1, moveForward,(sc,))
                useLidar(lidarData)
                return
            #Modulo all the pid values
            #leftOnePidVal %= modOne
            leftTwoPidVal %= tileSize
            #leftThreePidVal %= modTwo
            #rightOnePidVal %= modOne
            rightTwoPidVal %= tileSize
            #rightThreePidVal %= modTwo
            
            global lastError
            global integral
            global derivative
            global proportion
            
            #actual PID
            proportion = rightTwoPidVal - leftTwoPidVal
            integral += proportion
            derivative = proportion - lastError
            lastError = proportion
    
            turn = KP * proportion + KI * integral + KD * derivative
    
            leftMotorSpeed = 20 #- turn
            rightMotorSpeed = 20# + turn
    
            #CALL MOTOR CODE
            #MoveMotors(leftMotorSpeed,rightMotorSpeed)
            useLidar(lidarData)
    #s.enter(0.7, 1, moveForward,(sc,))'''
    #moveForward()

while True:
    moveForward()

#s.enter(0.7, 1, moveForward,(s,))
#s.run()
#movingForward = True
#moveForward()
'''
while True:
    turn(getCurrentAngle(),90)
    print("DONE 90")
    time.sleep(5)
    turn(getCurrentAngle(),270)
    print("DONE 270")
    time.sleep(5)
    turn(getCurrentAngle(),0)
    print("DONE 0")
    time.sleep(5)
    turn(getCurrentAngle(),180)
    print("DONE 180")
    time.sleep(5)'''