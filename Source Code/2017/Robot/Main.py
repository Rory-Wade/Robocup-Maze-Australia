import zmq
import time
import json
import math
import atexit
from copy import copy, deepcopy

from Accel import *
from Touch import *
from Light import *

context = zmq.Context()

lidar = context.socket(zmq.SUB)
lidar.setsockopt(zmq.CONFLATE, 1)
lidar.connect("tcp://localhost:5556")

bluetooth = context.socket(zmq.PUB)
bluetooth.set_hwm(7)
bluetooth.bind("tcp://*:5558")

motors = context.socket(zmq.REQ)
motors.connect("tcp://localhost:5557")

integral = 0
derivative = 0
proportion = 0
last_error = 0

filter = "[LIDAR]"
filter = filter.decode('ascii')
lidar.setsockopt_string(zmq.SUBSCRIBE, filter)

global currentFacingDirection
currentFacingDirection = 0

global currentFacingDirectionLast
currentFacingDirectionLast = 0

global baseMotorSpeed
baseMotorSpeed = 20

tileSize = 300
nextTile = None
nextTileDir = None

global paused
paused = True 

global firstMove
firstMove = True

lastSilverTileCoords = []
lastSilverTileDirection = 0
silverBacktraceArray = []

robotZ = 2

map = []
for width in range(0,75):
    map.append([])
    for height in range(0,75):
        map[width].append(0)
print("COMPLETED MAP CREATION")
coords = [37,37]
explored = []
backtraceArray = [[coords[0],coords[1]]]

def exit_handler():
    print 'Program Shutting Down...'
    StopMotors()
    
atexit.register(exit_handler)

def turn(currentAngle,toAngle):
    global paused
    
    if PauseButton():
        paused = not paused
        
        while PauseButton():
                RandomNumberLoop = 1
                
    if not paused:
        bluetooth.send_string("%s %s" % ("[BLUE]:","CMP;%i"%int(getCurrentAngle())))
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

        return turn(getCurrentAngle(),toAngle)


def PID(lidarDistanceArray1):
    global proportion
    global integral
    global derivative
    global last_error
    global baseMotorSpeed
    
    lidarDistanceArray = []
    
    for i in lidarDistanceArray1:
        if i < 120:
            lidarDistanceArray.append(120)
        else:
            lidarDistanceArray.append(i)
        
    KP = 0.5
    KI = 0.01
    KD = 0.5
    
    offset = 2
    minLength = 180
    minSpeed = -15
    maxSpeed = 60
    angle = ((offset * 10) * math.pi / 180)
    DesiredDistance = 135
    Right = 0
    Left = 0
    
    FrontLeft = math.cos(angle) * lidarDistanceArray[9 - offset]
    BackLeft = math.cos(angle) * lidarDistanceArray[9 + offset]
    FrontRight = math.cos(angle) * lidarDistanceArray[27 + offset]
    BackRight = math.cos(angle) * lidarDistanceArray[27 - offset]
    
    # print("FrontLeft: %f  BackLeft: %f  FrontRight: %f  BackRight: %f"%(FrontLeft,BackLeft,FrontRight,BackRight))
    
    if FrontLeft < minLength and BackLeft < minLength and FrontRight < minLength and BackRight < minLength and False:
        differnece = (BackLeft - FrontLeft) + (FrontRight - BackRight)
        distDiffernece = DesiredDistance - min(FrontLeft,DesiredDistance + 21) + min(FrontRight,DesiredDistance + 21) - DesiredDistance
    
        # print("L = %f , R = %f"%(lidarDistanceArray[9] , lidarDistanceArray[27]))
        print("LR")
    elif FrontLeft < minLength and BackLeft < minLength:
        differnece = BackLeft - FrontLeft
        distDiffernece =  DesiredDistance - min(FrontLeft,DesiredDistance + 21)
        print("R")
    elif FrontRight < minLength and BackRight < minLength:
        differnece = FrontRight - BackRight
        distDiffernece = min(FrontRight,DesiredDistance + 21) - DesiredDistance
        print("L")
    else:
        distDiffernece = 0
        differnece = 0
        # differnece = 0()
        
        # if currentFacingDirection == 0:
        #     if differnece > 180:
        #         differnece = (360 - angle) * -1 
            
        # else:
        #     differnece = ((90 * currentFacingDirection)  - angle) * -1

    proportion = (differnece + distDiffernece/2)
    
    integral  += proportion
    derivative = proportion - last_error
    last_error = proportion
    
    turn = KP*proportion + KI*integral + KD*derivative
    
    if(integral > 60 and integral < -60 and lidarDistanceArray[18] > 200 and lidarDistanceArray[0] > 200):
        baseMotorSpeed = 10
    
    MoveMotors(baseMotorSpeed - turn,baseMotorSpeed + turn)  

lastSentCoords = []
      
def validTiles(LidarData):
    presetValue = 8
    offset = 2
    tileSize = 300
    
    returnArray = []
    
    angleDistance = 140
    minDirectLength = 100
    
    for i in range(4):
            returnArray.append(int(LidarData[i * 9] / tileSize))
        
    return returnArray
    
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
        finishTurn(lidarArray)
            
        currentFacingDirectionLast = currentFacingDirection
            
def readLidar():
    lidarINPUT = lidar.recv_string().split(":")
    lidarINPUT = json.loads(lidarINPUT[1])
    return lidarINPUT
    
def MoveMotors(Linput,Rinput):
    motors.send(b"%i,%i" % (Linput,Rinput))
    message = motors.recv()
    
def StopMotors():
    motors.send(b"%i,%i" % (0,0))
    message = motors.recv()

def MovingForward(lidarData):
    if numberFitsEnvelope(lidarData[0],lidarData[18], 15):
        return False
    return True
    
def finishTurn(lidarDistanceArray):
    proportion = 0
    derivative = 0
    last_error = 0
    integral = 0
    
    KP = 1
    KI = 0.01
    KD = 1.2
    
    offset = 1
    minLength = 160
    angle = ((offset * 10) * math.pi / 180)
    turnTileSize = 200

    lidarDistanceArray = readLidar()
    
    if(lidarDistanceArray[9] < turnTileSize and lidarDistanceArray[9] > 0):
        for i in range(2):  
            lidarDistanceArray = readLidar()
            Front = math.cos(angle) * lidarDistanceArray[9 - offset]
            Back = math.cos(angle) * lidarDistanceArray[9 + offset]
            
            while(abs(Back - Front) > 1):
                lidarDistanceArray = readLidar()
    
                Front = math.cos(angle) * lidarDistanceArray[9 - offset]
                Back = math.cos(angle) * lidarDistanceArray[9 + offset]
            
                proportion = Back - Front
                
                integral  += proportion
                derivative = proportion - last_error
                last_error = proportion
                
                turn = KP*proportion + KI*integral + KD*derivative
                
                if(abs(turn) < 7 and abs(turn) > 0):
                    turn = (turn / abs(turn)) * 7
                elif(abs(turn) < 7):
                    turn = 7
                    
                #print("prop: %f  Turn: %f  LastError: %f"%(proportion,turn,last_error))
                MoveMotors(-turn, turn)
            
    elif(lidarDistanceArray[27] < turnTileSize and lidarDistanceArray[27] > 0):
        for i in range(2):  
            lidarDistanceArray = readLidar()
            Front = math.cos(angle) * lidarDistanceArray[27 - offset]
            Back = math.cos(angle) * lidarDistanceArray[27 + offset]
            
            while(abs(Back - Front) > 1):
                lidarDistanceArray = readLidar()
    
                Front = math.cos(angle) * lidarDistanceArray[27 - offset]
                Back = math.cos(angle) * lidarDistanceArray[27 + offset]
            
                proportion = Back - Front
                
                integral  += proportion
                derivative = proportion - last_error
                last_error = proportion
                
                turn = KP*proportion + KI*integral + KD*derivative
                
                if(abs(turn) < 7 and abs(turn) > 0):
                    turn = (turn / abs(turn)) * 7
                elif(abs(turn) < 7):
                    turn = 7
                    
                #print("prop: %f  Turn: %f  LastError: %f"%(proportion,turn,last_error))
                MoveMotors(-turn, turn)

    else:
        print("FinishTurn:No wall to use")
        
    StopMotors()
    
def numberFitsEnvelope(front, back, envelope):
    global baseMotorSpeed
    global nextTile
    global nextTileDir
    global firstMove
    distance = 0
    TileMoved = False
    
    #decide on next tile distance
    if nextTile == None:
        if front < back and front > 150:
            nextTileDir = True
            distance = front
            nextTile = (int(distance / tileSize)) * tileSize - 200
            
            
        elif back > 150:
            nextTileDir = False
            distance = back
            nextTile = (int(distance / tileSize) + 1) * tileSize + 160
      
    else:        
        if nextTileDir and front > 0:
            distance = front
            baseMotorSpeed = (int(distance) - nextTile) / 4
            TileMoved = abs(distance - nextTile) < (tileSize / envelope)
        
        elif back > 0:
            distance = back
            baseMotorSpeed = -(int(distance) - nextTile) / 4
            TileMoved = abs(distance - nextTile) < (tileSize / envelope)
    
        lessThanTile = (front < 140 and front > 0 or TouchSensors()[0] or TouchSensors()[1])

        if (lessThanTile or TileMoved) or nextTile < 0 or firstMove: 
            firstMove = False
            nextTile = None
            nextTileDir = None
            return True
            
    return False


def changeMap(up,right,down,left):
    print(up, right, down, left)
    print(coords)
    for x in range(1,up * 2,2):
        if map[coords[0] + x][coords[1]] == 0:
            map[coords[0] + x][coords[1]] = 0
    map[coords[0] + (up * 2) + 1][coords[1]] = 9
    for x in range(1,right * 2,2):
        if map[coords[0]][coords[1] + x] == 0:
            map[coords[0]][coords[1] + x] = 0
    map[coords[0]][coords[1] + (right * 2) + 1] = 9
    for x in range(1,down * 2,2):
        if map[coords[0] - x][coords[1]] == 0:
            map[coords[0] - x][coords[1]] = 0
    map[coords[0] - (down * 2) - 1][coords[1]] = 9
    for x in range(1,left * 2,2):
        if map[coords[0]][coords[1] - x] == 0:
            map[coords[0]][coords[1] - x] = 0
    map[coords[0]][coords[1] - (left * 2) - 1] = 9

def adjacentUnexploredTile(at):
    x = at[0]
    y = at[1]
    
    if map[x + 1][y] == 0:
        if map[x + 2][y] == 0:
            return True
    if map[x - 1][y] == 0:
        if map[x - 2][y] == 0:
            return True
    if map[x][y + 1] == 0:
        if map[x][y + 2] == 0:
            return True
    if map[x][y - 1] == 0:
        if map[x][y - 2] == 0:
            return True
    return False
        

def lookForEasyConnectionToBackTraceRoute():
    compatibleIndex = len(backtraceArray) - 1
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
        if adjacentUnexploredTile(backtraceArray[i]):
            break
        print("-----------------")
    print(compatibleIndex)
    
    
    
    return compatibleIndex

def pointDelta(point, pointb):
    dx = abs(point[0] - pointb[0])
    dy = abs(point[1] - pointb[1])
    return dx + dy

def relativePositionCode(tileDist):
    
    up = tileDist[0]
    right = tileDist[1]
    down = tileDist[2]
    left = tileDist[3]
    
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
        return returnDirection
    else:
        print("Orientation Change")
        return None
  
  
lastDirection = 0
lastCoords = deepcopy(coords)

def DFS(up,right,down,left):
    global lastBacktracePoint
    global lastCoords
    changeMap(up,right,down,left)
    decided = False
    directionToMove = -1
    lastCoords = deepcopy(coords)
    if map[coords[0]][coords[1]] == 0:
        map[coords[0]][coords[1]] = 1
        
    if currentFacingDirection == 0:
        if up > 0 and decided == False:
            nextTile = map[coords[0] + 2][coords[1]]
            #print(coords[0] + 1)
            #print(coords[1])
            #print(map[coords[0] + 1][coords[1]])
            if nextTile == 0:
                decided = True
                print("FACING 0 MOVED 0")
                #Move up
                coords[0] += 2
                directionToMove = 0
        if right > 0 and decided == False:
            nextTile = map[coords[0]][coords[1] + 2]
            if nextTile == 0:
                decided = True
                print("FACING 0 MOVED 1")
                #Move right
                coords[1] += 2
                directionToMove = 1
        if down > 0 and decided == False:
            nextTile = map[coords[0] - 2][coords[1]]
            if nextTile == 0:
                decided = True
                print("FACING 0 MOVED 2")
                #Move down
                coords[0] -= 2
                directionToMove = 2
        if left > 0 and decided == False:
            nextTile = map[coords[0]][coords[1] - 2]
            if nextTile == 0:
                decided = True
                print("FACING 0 MOVED 3")
                #Move left
                coords[1] -= 2
                directionToMove = 3
    elif currentFacingDirection == 1:
        if right > 0 and decided == False:
            nextTile = map[coords[0]][coords[1] + 2]
            if nextTile == 0:
                decided = True
                print("FACING 1 MOVED 1")
                #Move right
                coords[1] += 2
                directionToMove = 1
        if down > 0 and decided == False:
            nextTile = map[coords[0] - 2][coords[1]]
            if nextTile == 0:
                decided = True
                print("FACING 1 MOVED 2")
                #Move down
                coords[0] -= 2
                directionToMove = 2
        if left > 0 and decided == False:
            nextTile = map[coords[0]][coords[1] - 2]
            if nextTile == 0:
                decided = True
                print("FACING 1 MOVED 3")
                #Move left
                coords[1] -= 2
                directionToMove = 3
        if up > 0 and decided == False:
            nextTile = map[coords[0] + 2][coords[1]]
            #print(coords[0] + 1)
            #print(coords[1])
            #print(map[coords[0] + 1][coords[1]])
            if nextTile == 0:
                decided = True
                print("FACING 1 MOVED 0")
                #Move up
                coords[0] += 2
                directionToMove = 0
    elif currentFacingDirection == 2:
        if down > 0 and decided == False:
            nextTile = map[coords[0] - 2][coords[1]]
            if nextTile == 0:
                decided = True
                #print("MOVED TO BLACK TILE")
                print("FACING 2 MOVED 2")
                print(lastCoords)
                print(nextTile)
                #Move down
                coords[0] -= 2
                directionToMove = 2
        if left > 0 and decided == False:
            nextTile = map[coords[0]][coords[1] - 2]
            if nextTile == 0:
                decided = True
                print("FACING 2 MOVED 3")
                #Move left
                coords[1] -= 2
                directionToMove = 3
        if up > 0 and decided == False:
            nextTile = map[coords[0] + 2][coords[1]]
            #print(coords[0] + 1)
            #print(coords[1])
            #print(map[coords[0] + 1][coords[1]])
            if nextTile == 0:
                decided = True
                print("FACING 2 MOVED 0")
                #Move up
                coords[0] += 2
                directionToMove = 0
        if right > 0 and decided == False:
            nextTile = map[coords[0]][coords[1] + 2]
            if nextTile == 0:
                decided = True
                print("FACING 2 MOVED 1")
                #Move right
                coords[1] += 2
                directionToMove = 1
    elif currentFacingDirection == 3:
        if left > 0 and decided == False:
            nextTile = map[coords[0]][coords[1] - 2]
            if nextTile == 0:
                decided = True
                print("FACING 3 MOVED 3")
                #Move left
                coords[1] -= 2
                directionToMove = 3
        if up > 0 and decided == False:
            nextTile = map[coords[0] + 2][coords[1]]
            #print(coords[0] + 1)
            #print(coords[1])
            #print(map[coords[0] + 1][coords[1]])
            if nextTile == 0:
                decided = True
                print("FACING 3 MOVED 0")
                #Move up
                coords[0] += 2
                directionToMove = 0
        if right > 0 and decided == False:
            nextTile = map[coords[0]][coords[1] + 2]
            if nextTile == 0:
                decided = True
                print("FACING 3 MOVED 1")
                #Move right
                coords[1] += 2
                directionToMove = 1
        if down > 0 and decided == False:
            nextTile = map[coords[0] - 2][coords[1]]
            if nextTile == 0:
                decided = True
                print("FACING 3 MOVED 2")
                #Move down
                coords[0] -= 2
                directionToMove = 2
    if directionToMove != -1:
        print("Found a direction to move")
        print(directionToMove)
        print("-------------------------")
        #Exploration logic found a solution, should not backtrack
        backtraceArray.append([coords[0],coords[1]])
        
        #ISSUE: THE CURRENT POSITION ISN"T APPENDED TO THE BACKTRACE ARRAY UPON FINISHING BACKTRACING
        
        return directionToMove
    elif len(backtraceArray) >= 2:
        print("Backtracing")
        backtraceArray.pop()
        #Exploration logic failed to find a solution, needs to backtrack
        
        #backtracing - check whether a thing can be legit'd
        backtraceindex = lookForEasyConnectionToBackTraceRoute()
        #chosen = False;
        
        counter = 0
        print(len(backtraceArray))
        print(backtraceindex)
        for i in range(len(backtraceArray), backtraceindex + 1, -1):
            popper = backtraceArray.pop() 
        
        #for i in range(backtraceindex - 1, len(backtraceArray) - 1):
            #backtoTile = backtraceArray.pop()
            #chosen = True;
        
        #if ((backtraceindex - 1) - (len(backtraceArray) - 1) == 0) and chosen == False:
            #backtoTile = backtraceArray.pop();
        #print(backtraceArray)
        backtracePoint = backtraceArray.pop();
        #backtracePoint = backtoTile
        #print(coords)
        #print(backtracePoint)
        
        #if pointDelta(coords, backtracePoint) >= 4 and pointDelta(coords, backtracePoint) >= 2:
        #    backtraceArray.append(backtracePoint)
        #    backtracePoint = lastBacktracePoint
        
        lastBacktracePoint = backtracePoint
        backtraceArray.append(lastBacktracePoint)
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
        else:
            return DFS(up,right,down,left)
    print("There are no valid solutions")
    return -1

    
def invalidLidarData(array):
    if array[0] > 0 and array[9] > 0 and array[18] > 0 and array[27] > 0:
        return False
    print("INVALID DATA")
    return True
        
        
print("ONLINE")

def blackTile():
    print("BLACK TILE")
    global coords
    global map
    global backtraceArray
    map[coords[0]][coords[1]] = 9
    map[coords[0]][coords[1] + 1] = 2
    map[coords[0]][coords[1] - 1] = 2
    map[coords[0] + 1][coords[1]] = 2
    map[coords[0] - 1][coords[1]] = 2
    print("BLACK TILE AT")
    print(coords)
    print("MOVING BACK TO")
    coords = deepcopy(lastCoords)
    print(coords)
    backtraceArray.pop()

def MoveBackFromBlack(lidarArray):
    envelope = 15
    front = lidarArray[0]
    back = lidarArray[18]
    # baseMotorSpeed
    # nextTile
    # nextTileDir
    # firstMove
    distance = 0
    TileMoved = False
    baseMotorSpeed = 20
    
    if front < back and front > 150:
        nextTileDir = True
        distance = front
        nextTile = (int(distance / tileSize) + 1) * tileSize + 160
    elif back > 150:
        nextTileDir = False
        distance = back
        nextTile = (int(distance / tileSize)) * tileSize - 200
    else:
        print("WELL HOW DO YOU EXPECT THIS FROM ME - MOVE BLACK")
    
    movingBack = True    
    
    while movingBack:    
        lidarArray = readLidar()
        
        front = lidarArray[0]
        back = lidarArray[18]
        
        if nextTileDir and front > 0:
            distance = front
            baseMotorSpeed = (int(distance) - nextTile) / 4
            TileMoved = abs(distance - nextTile) < (tileSize / envelope)
        
        elif back > 0:
            distance = back
            baseMotorSpeed = -(int(distance) - nextTile) / 4
            TileMoved = abs(distance - nextTile) < (tileSize / envelope)
    
        lessThanTile = (back < 140 and back > 0 or TouchSensors()[2] or TouchSensors()[3])

        if (lessThanTile or TileMoved) or nextTile < 0 or firstMove: 
            StopMotors()
            movingBack = False    
        else:
            MoveMotors(baseMotorSpeed,baseMotorSpeed)    
    
def setupForwardTraceArray():
    global silverBacktraceArray
    global backtraceArray
    
    forwardTraceArray = []
    print("LENGTHS:")
    print(len(silverBacktraceArray))
    print(len(backtraceArray))
    for i in range(len(silverBacktraceArray), len(backtraceArray)):
        forwardTraceArray.append(backtraceArray[i])
        print("APPENDED TO THE FORWARD TRACING ARRAY")
        
    return forwardTraceArray
    
def silverTile():
    print("SILVER TILE")
    global backtraceArray
    global silverBacktraceArray
    
    global coords
    global lastDirection
    global lastSilverTileCoords
    global lastSilverTileDirection
    lastSilverTileCoords = [coords[0],coords[1]]
    lastSilverTileDirection = int(str(lastDirection))
    silverBacktraceArray = deepcopy(backtraceArray)
    map[coords[0]][coords[1]] = 3
    
    
def revertToSilverTile():
    global backtraceArray
    global silverBacktraceArray
    global lastSilverTileDirection
    global lastSilverTileCoords
    global currentFacingDirection
    global currentFacingDirectionLast
    global coords
    
    forwardTraceArray = setupForwardTraceArray()
    
    if lastSilverTileCoords == []:
        return
    
    print("REVERTING TO SILVER TILE")
    print(lastSilverTileDirection)
    print(lastSilverTileCoords)
    print("------------------------")
    
    print(len(silverBacktraceArray))
    currentFacingDirection = deepcopy(lastSilverTileDirection)
    currentFacingDirectionLast = deepcopy(lastSilverTileDirection)
    coords = [lastSilverTileCoords[0],lastSilverTileCoords[1]]
    fta = deepcopy(forwardTraceArray)
    backtraceArray = silverBacktraceArray + fta
    print(len(fta))
    for element in reversed(fta):
        backtraceArray.append(element)
    backtraceArray.append(coords);
    print("TRIED TO REVERT TO SILVER TILE")
    print(len(backtraceArray))
    print(backtraceArray)
    print(currentFacingDirection)
    
    
wasPaused = False
initialPause = True

def updateBluetoothMaps(lidarArray):
    
    bluetooth.send_string("%s TIL;%i,%i,%i,%i" % ("[BLUE]:",lidarArray[0],lidarArray[9],lidarArray[18],lidarArray[27]))
    
    stringMap = ""
    
    for outside in reversed(map):
        for inside in outside:
            stringMap += "%i,"%(inside)
    stringMap = stringMap[:-1] 
    
    if lastSilverTileCoords != []:
        bluetooth.send_string("%s LST;%i,%i" % ("[BLUE]:",lastSilverTileCoords[1],74 - lastSilverTileCoords[0]))
        
    bluetooth.send_string("%s CRD;%i,%i" % ("[BLUE]:",coords[1],74-coords[0]))
    bluetooth.send_string("%s BTA;%s" % ("[BLUE]:", json.dumps(backtraceArray, ensure_ascii=True)))
    bluetooth.send_string("%s MAP;%s" % ("[BLUE]:",stringMap))
    
    
while True:
    
    if PauseButton():
        paused = not paused
        
        if not initialPause:
            wasPaused = True
            firstMove = True
            
        if not paused:
            initialPause = False
            bluetooth.send_string("%s PAU;FALSE")
        else:
            bluetooth.send_string("%s PAU;TRUE")
        
        while PauseButton():
            StopMotors()
            time.sleep(0.5)
            
    if not paused:
        
        if wasPaused:
            wasPaused = False
            revertToSilverTile()

        lidarArray = readLidar()
        
        if MovingForward(lidarArray):
            PID(lidarArray)
        else:
            
            StopMotors()
            lidarArray = readLidar()
            # response = raw_input("Silver Tile?")
            # if response == "y":
            #     silverTile()
              
            if tileColour() == 1:
                print("silver Tile")
                silverTile()
                
            if tileColour() == 0:
                print("Black Tile")
                blackTile()
                MoveBackFromBlack(lidarArray)
                
            lidarArray = readLidar()
            directionToGo = relativePositionCode(validTiles(lidarArray))
            lastDirection = directionToGo
            
            print("----LIDAR MEASUREMENTS REL----")
            print("  LEFT, RIGHT, FORWARD, BACK")
            print(lidarArray[27],lidarArray[9],lidarArray[0],lidarArray[18])
            print("-------------Tile-------------")
            print(validTiles(readLidar()))
            print("----------Direction-----------")
            print(directionToGo)
            print("------------------------------")
            
            if directionToGo is not None and directionToGo >= 0:
                moveDirection(directionToGo)
            else:
                paused = True
                
            updateBluetoothMaps(lidarArray)
            
            print("-------------------------------------------")
    else:
        StopMotors()

'''
while True:
    print("Getting Lidar Data and finishing turn")
    print(validTiles(readLidar()))
    print("Done")
    time.sleep(3)
'''  