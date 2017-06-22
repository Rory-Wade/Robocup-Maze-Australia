import zmq
import time
import json
import math
import atexit

from Accel import *
from Touch import *

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.CONFLATE, 1)
socket.connect("tcp://localhost:5556")

motors = context.socket(zmq.REQ)
motors.connect("tcp://localhost:5557")

filter = "[LIDAR]"
filter = filter.decode('ascii')
socket.setsockopt_string(zmq.SUBSCRIBE, filter)

global currentFacingDirection
currentFacingDirection = 0
global currentFacingDirectionLast
currentFacingDirectionLast = 0

KP = 0.5
KI = 0.01
KD = 0.1

integral = 0
derivative = 0
proportion = 0

last_error = 0

baseMotorSpeed = 40

tileSize = 300
nextTile = None
nextTileDir = None

map = []
for width in range(0,25):
    map.append([])
    for height in range(0,25):
        map[width].append(0)
print("COMPLETED MAP CREATION")
coords = [12,12]
explored = []
backtraceArray = [[coords[0],coords[1]]]

def exit_handler():
    print 'Program Shutting Down...'
    StopMotors()
    
atexit.register(exit_handler)

def turn(currentAngle,toAngle):
    
    paused = PauseButton()
    
    if not paused:
        if currentAngle == None:
            time.sleep(0.05)
            return turn(getCurrentAngle(),toAngle)
        movingForward = False
        
        if abs((currentAngle - toAngle) % 360) < 3:
    
            StopMotors()
            movingForward = True
            return True
        elif abs((currentAngle - toAngle) % 360) < 180:
    
            rightMotorSpeed = (abs(abs(currentAngle - toAngle) % 360) / 180) * 90 + 20
            leftMotorSpeed = -((abs(abs(currentAngle - toAngle) % 360) / 180) * 90) - 20
    
            MoveMotors(leftMotorSpeed,rightMotorSpeed)
        elif abs((currentAngle - toAngle) % 360) < 180:
    
            rightMotorSpeed = (abs(abs(currentAngle - toAngle) % 360) / 180) * 90 + 20
            leftMotorSpeed = -((abs(abs(currentAngle - toAngle) % 360) / 180) * 90) - 20
    
            MoveMotors(leftMotorSpeed,rightMotorSpeed)
        elif currentAngle > 269 and toAngle == 0:
        
            MoveMotors((int(380 - currentAngle) % 360),-(int(380 - currentAngle) % 360))
        else:
    
            leftMotorSpeed = (abs(abs(currentAngle - toAngle) % 360) / 180) * 90 + 20
            rightMotorSpeed = -((abs(abs(currentAngle - toAngle) % 360) / 180) * 90) - 20
    
            MoveMotors(leftMotorSpeed,rightMotorSpeed)
        time.sleep(0.05)
        return turn(getCurrentAngle(),toAngle)

def moveDirection(direction):
    global currentFacingDirectionLast
    
    if currentFacingDirectionLast != direction:
        if direction == 0:
            print("TURN NORTH")
            turn(getCurrentAngle(),0)
        elif direction == 1:
            print("TURN EAST")
            turn(getCurrentAngle(),90)
        elif direction == 2:
            print("TURN SOUTH")
            turn(getCurrentAngle(),180)
        elif direction == 3:
            print("TURN WEST")
            turn(getCurrentAngle(),270)
            
        currentFacingDirectionLast = currentFacingDirection
            
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
    if numberFitsEnvelope(lidarData[0],lidarData[18], 15) or TouchSensors()[0] or TouchSensors()[0]:
        return False
    return True
    
def numberFitsEnvelope(front, back, envelope):
    global baseMotorSpeed
    global nextTile
    global nextTileDir
    distance = 0
    TileMoved = False
    
    if nextTile == None:
        if front < back and front > 0:
            nextTileDir = True
            distance = front
            nextTile = ( int(distance / tileSize)) * tileSize - 150
            
        elif back > 0:
            nextTileDir = False
            distance = back
            nextTile = (int(distance / tileSize) + 1) * tileSize + 150
    else:        
            
        if nextTileDir and front > 0:
            distance = front
            baseMotorSpeed = (int(distance) - nextTile) / 2.8
            TileMoved = abs(distance - nextTile) < (tileSize / envelope)
        elif back > 0:
            distance = back
            baseMotorSpeed = -(int(distance) - nextTile) / 2.8
            TileMoved = abs(distance - nextTile) < (tileSize / envelope)
    
        lessThanTile = (front < 150 and front > 0)

        if (lessThanTile or TileMoved) or nextTile < 0: 
            
            nextTile = None
            nextTileDir = None
            return True
            
    return False
    
def PID(lidarDistanceArray):
    global proportion
    global integral
    global derivative
    global last_error
    
    angle = 0
    proportion = angle
    
    integral  += proportion
    derivative = proportion - last_error
    last_error = proportion
    
    turn = KP*proportion + KI*integral + KD*derivative

    MoveMotors(baseMotorSpeed,baseMotorSpeed)  

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
    for x in range(1,up * 2,2):
        if map[coords[0] + x][coords[1]] != 1:
            map[coords[0] + x][coords[1]] = 0
    map[coords[0] + (up * 2) + 1][coords[1]] = 9
    for x in range(1,right * 2,2):
        if map[coords[0]][coords[1] + x] != 1:
            map[coords[0]][coords[1] + x] = 0
    map[coords[0]][coords[1] + (right * 2) + 1] = 9
    for x in range(1,down * 2,2):
        if map[coords[0] - x][coords[1]] != 1:
            map[coords[0] - x][coords[1]] = 0
    map[coords[0] - (down * 2) - 1][coords[1]] = 9
    for x in range(1,left * 2,2):
        if map[coords[0]][coords[1] - x] != 1:
            map[coords[0]][coords[1] - x] = 0
    map[coords[0]][coords[1] - (left * 2) - 1] = 9

def lookForEasyConnectionToBackTraceRoute():
    compatibleIndex = len(backtraceArray)
    print(backtraceArray)
    print("ROBOT AT:",coords)
    for i in range(len(backtraceArray) - 1,-1,-1):
        dx = coords[1] - backtraceArray[i][1]
        dy = coords[0] - backtraceArray[i][0]

        print("DX:", dx, "DY:", dy)


        print(backtraceArray[i])

        if coords[0] == backtraceArray[i][0] and coords[1] == backtraceArray[i][1]:
            compatibleIndex = i
        elif coords[0] == backtraceArray[i][0] or coords[1] == backtraceArray[i][1]:
            #This means an adjacent tile
            print(dx,dy)
            if math.pow(dy,2) + math.pow(dx,2) == 4:
                #Are is there anything 1 tile away
                print("1 tile away from the backtrace array")
                if dx > 0:
                    #dx > 0 therefore robot is further to the right than the tile it's aiming at
                    if map[coords[0]][coords[1] - 1] == 0:
                        # there is no wall to the left
                        print("No wall to the left. Valid.")
                        compatibleIndex = i
                elif dx < 0:
                    #dx < 0 therefore robot is further to the left than the tile it's aiming at
                    if map[coords[0]][coords[1] + 1] == 0:
                        # there is no wall to the left
                        print("No wall to the right. Valid.")
                        compatibleIndex = i
                elif dy > 0:
                    #dy > 0 therefore the robot's location is higher up than the tile location. The tile is below.
                    if map[coords[0] - 1][coords[1]] == 0:
                        # there is no wall below
                        print("No wall underneath. Valid.")
                        compatibleIndex = i
                elif dy < 0:
                    #dy < 0 therefore the robot's location is lower down than the tile location. The tile is above.
                    if map[coords[0] + 1][coords[1]] == 0:
                        # there is no wall below
                        print("No wall above. Valid.")
                        compatibleIndex = i
        print("-----------------")
    print(compatibleIndex)
    return compatibleIndex


def DFS(up,right,down,left):
    changeMap(up,right,down,left)
    decided = False
    directionToMove = -1
    map[coords[0]][coords[1]] = 1
    if up > 0 and decided == False:
        nextTile = map[coords[0] + 2][coords[1]]
        #print(coords[0] + 1)
        #print(coords[1])
        #print(map[coords[0] + 1][coords[1]])
        if nextTile == 0:
            decided = True
            #Move up
            coords[0] += 2
            directionToMove = 0
    if right > 0 and decided == False:
        nextTile = map[coords[0]][coords[1] + 2]
        if nextTile == 0:
            decided = True
            #Move right
            coords[1] += 2
            directionToMove = 1
    if down > 0 and decided == False:
        nextTile = map[coords[0] - 2][coords[1]]
        if nextTile == 0:
            decided = True
            #Move down
            coords[0] -= 2
            directionToMove = 2
    if left > 0 and decided == False:
        nextTile = map[coords[0]][coords[1] - 2]
        if nextTile == 0:
            decided = True
            #Move left
            coords[1] -= 2
            directionToMove = 3
    if directionToMove != -1:
        print("Found a direction to move")
        #Exploration logic found a solution, should not backtrack
        backtraceArray.append([coords[0],coords[1]])
        return directionToMove
    elif len(backtraceArray) >= 1:
        print("Backtracing")
        #Exploration logic failed to find a solution, needs to backtrack
        
        #backtracing - check whether a thing can be legit'd
        backtraceindex = lookForEasyConnectionToBackTraceRoute()
        for i in range(backtraceindex - 1, len(backtraceArray) - 1):
            backtoTile = backtraceArray.pop()

        backtracePoint = backtoTile
        print(coords)
        print(backtracePoint)
        if coords[0] > backtracePoint[0]:
            #Needs to go DOWN
            directionToMove = 2
            coords[0] -= 2
            return directionToMove
        if coords[0] < backtracePoint[0]:
            #Needs to go UP
            directionToMove = 0
            coords[0] += 2
            return directionToMove
        if coords[1] > backtracePoint[1]:
            #Needs to go LEFT
            directionToMove = 3
            coords[1] -= 2
            return directionToMove
        if coords[1] < backtracePoint[1]:
            #Needs to go RIGHT
            directionToMove = 1
            coords[1] += 2
            return directionToMove
    print("There are no valid solutions")
    return -1

    
def invalidLidarData(array):
    if array[0] > 0 and array[9] > 0 and array[18] > 0 and array[27] > 0:
        return False
    print("INVALID DATA")
    return True
        
        
print("ONLINE")

while True:
    paused = PauseButton()
    
    if not paused:
        lidarArray = readLidar()
        
        if MovingForward(lidarArray):
            PID(lidarArray)
        else:
            StopMotors()
            
            upTiles = int(lidarArray[0] / tileSize)
            rightTiles = int(lidarArray[9] / tileSize)
            downTiles = int(lidarArray[18] / tileSize)
            leftTiles = int(lidarArray[27] / tileSize)
            
            directionToGo = relativePositionCode(upTiles,rightTiles,downTiles,leftTiles)
            
            print("----LIDAR MEASUREMENTS REL----")
            print("  LEFT, RIGHT, FORWARD, BACK")
            print(lidarArray[27],lidarArray[9],lidarArray[0],lidarArray[18])
            print("-------------Tile-------------")
            print(leftTiles,rightTiles,upTiles,downTiles)
            print("----------Direction-----------")
            print(directionToGo)
            print("------------------------------")
            
            response = raw_input("Do you want the map?")
            if response == "y":
                print(map)
            
            
            if directionToGo is not None:
                moveDirection(directionToGo)
            
            print("-------------------------------------------")
            print("")
            
    
