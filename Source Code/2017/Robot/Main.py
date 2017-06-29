import zmq
import time
import json
import math
import atexit

from Accel import *
from Touch import *
from Light import *

context = zmq.Context()

lidar = context.socket(zmq.SUB)
lidar.setsockopt(zmq.CONFLATE, 1)
lidar.connect("tcp://localhost:5556")

bluetooth = context.socket(zmq.PUB)
bluetooth.set_hwm(1)
bluetooth.bind("tcp://*:5558")

motors = context.socket(zmq.REQ)
motors.connect("tcp://localhost:5557")

filter = "[LIDAR]"
filter = filter.decode('ascii')
lidar.setsockopt_string(zmq.SUBSCRIBE, filter)

global currentFacingDirection
currentFacingDirection = 0

global currentFacingDirectionLast
currentFacingDirectionLast = 0

integral = 0
derivative = 0
proportion = 0

last_error = 0

baseMotorSpeed = 10

tileSize = 300
nextTile = None
nextTileDir = None

global paused
paused = True 

global firstMove
firstMove = True
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
        bluetooth.send_string("%s %s" % ("[BLUE]:","C;%i"%int(getCurrentAngle())))
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
    
    time.sleep(2)
    
    lidarDistanceArray = readLidar()
    
    if(lidarDistanceArray[9] < turnTileSize):
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
                    
                print("prop: %f  Turn: %f  LastError: %f"%(proportion,turn,last_error))
                MoveMotors(-turn, turn)
            
    elif(lidarDistanceArray[27] < turnTileSize):
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
                    
                print("prop: %f  Turn: %f  LastError: %f"%(proportion,turn,last_error))
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
            nextTile = (int(distance / tileSize)) * tileSize - 170
            
            
        elif back > 150:
            nextTileDir = False
            distance = back
            nextTile = (int(distance / tileSize) + 1) * tileSize + 160
      
    else:        
        if nextTileDir and front > 0:
            distance = front
            baseMotorSpeed = (int(distance) - nextTile) / 3.5
            TileMoved = abs(distance - nextTile) < (tileSize / envelope)
        
        elif back > 0:
            distance = back
            baseMotorSpeed = -(int(distance) - nextTile) / 3.5
            TileMoved = abs(distance - nextTile) < (tileSize / envelope)
    
        lessThanTile = (front < 140 and front > 0)

        if (lessThanTile or TileMoved) or nextTile < 0 or firstMove: 
            firstMove = False
            nextTile = None
            nextTileDir = None
            return True
            
    return False
    
def PID(lidarDistanceArray):
    global proportion
    global integral
    global derivative
    global last_error
    
    Ku = 2.8
    # Hacky Ziegler-Nicholls method
    KP = Ku #* 0.6
    KI = 0 #Ku * 0.5
    KD = 0 #Ku * 0.125
    # Hacky Pessen Integral Rule
    # KP = Ku * 0.7
    # KI = Ku * 0.4
    # KD = Ku * 0.15

    offset = 1
    minLength = 200
    minSpeed = -10
    maxSpeed = 50
    angle = ((offset * 10) * math.pi / 180)
    DesiredDistance = 135
    Right = 0
    Left = 0
    
    FrontLeft = math.cos(angle) * lidarDistanceArray[9 - offset]
    BackLeft = math.cos(angle) * lidarDistanceArray[9 + offset]
    FrontRight = math.cos(angle) * lidarDistanceArray[27 + offset]
    BackRight = math.cos(angle) * lidarDistanceArray[27 - offset]
    
    
    
    # print("FrontLeft: %f  BackLeft: %f  FrontRight: %f  BackRight: %f"%(FrontLeft,BackLeft,FrontRight,BackRight))
    
    if FrontLeft < minLength and BackLeft < minLength and FrontRight < minLength and BackRight < minLength:
        proportion = (BackLeft - FrontLeft) + (FrontRight - BackRight)
        distProportion = FrontRight - FrontLeft # - abs((BackLeft + FrontLeft)/2) + abs((BackRight + FrontRight)/2)
    
        # print("L = %f , R = %f"%(lidarDistanceArray[9] , lidarDistanceArray[27]))
        # print("LR")
    elif FrontLeft < minLength and BackLeft < minLength:
        proportion = BackLeft - FrontLeft
        distProportion =  abs((BackLeft + FrontLeft)/2) - DesiredDistance
        # print("L")
    elif FrontRight < minLength and BackRight < minLength:
        proportion = FrontRight - BackRight
        distProportion = DesiredDistance - abs((BackRight + FrontRight)/2)
        # print("R")
    else:
        proportion = 0
        distProportion = 0
    
    integral  += proportion #+ 2 * distProportion
    derivative = proportion - last_error
    last_error = proportion
    
    turn = KP*proportion + KI*integral + KD*derivative
    
    lturn = max(baseMotorSpeed - turn, minSpeed)
    lturn = min(lturn, maxSpeed)
    rturn = max(baseMotorSpeed + turn, minSpeed)
    rturn = min(rturn, maxSpeed)
    # print("Proportion: %f, Integral: %f, Derivative: %f, L %f, R %f" % (proportion, integral, derivative, lturn, rturn))

    MoveMotors(lturn,rturn)  

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
        return returnDirection
    else:
        print("Orientation Change")
        return None


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

def pointDelta(point, pointb):
    dx = abs(point[0] - pointb[0])
    dy = abs(point[1] - pointb[1])
    return dx + dy

lastDirection = 0

def DFS(up,right,down,left):
    global lastBacktracePoint
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
        
        #ISSUE: THE CURRENT POSITION ISN"T APPENDED TO THE BACKTRACE ARRAY UPON FINISHING BACKTRACING
        
        return directionToMove
    elif len(backtraceArray) >= 2:
        print("Backtracing")
        backtraceArray.pop()
        #Exploration logic failed to find a solution, needs to backtrack
        
        #backtracing - check whether a thing can be legit'd
        #backtraceindex = lookForEasyConnectionToBackTraceRoute()
        #chosen = False;
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
    print("There are no valid solutions")
    return -1

    
def invalidLidarData(array):
    if array[0] > 0 and array[9] > 0 and array[18] > 0 and array[27] > 0:
        return False
    print("INVALID DATA")
    return True
        
        
print("ONLINE")

lastSilverTileCoords = []
lastSilverTileDirection = 0
silverBacktraceArray = []

def blackTile():
    print("BLACK TILE")
    
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
    silverBacktraceArray = backtraceArray
    
def revertToSilverTile():
    global backtraceArray
    global silverBacktraceArray
    global lastSilverTileDirection
    global lastSilverTileCoords
    global currentFacingDirection
    global coords
    
    print("REVERTING TO SILVER TILE")
    print(lastSilverTileDirection)
    print(lastSilverTileCoords)
    print("------------------------")
    
    currentFacingDirection = lastSilverTileDirection
    coords = [lastSilverTileCoords[0],lastSilverTileCoords[1]]
    backtraceArray = silverBacktraceArray
    print("TRIED TO REVERT TO SILVER TILE")
    
wasPaused = False
initialPause = True

while True:
    
    if PauseButton():
        paused = not paused
        
        if not initialPause:
            wasPaused = True
            firstMove = True
        if not paused:
            initialPause = False
        
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
            
            upTiles = int(lidarArray[0] / tileSize)
            rightTiles = int(lidarArray[9] / tileSize)
            downTiles = int(lidarArray[18] / tileSize)
            leftTiles = int(lidarArray[27] / tileSize)
            
            print("----LIDAR MEASUREMENTS REL----")
            print("  LEFT, RIGHT, FORWARD, BACK")
            print(lidarArray[27],lidarArray[9],lidarArray[0],lidarArray[18])
            print("-------------Tile-------------")
            print(leftTiles,rightTiles,upTiles,downTiles)
            
            
            '''
            response = raw_input("Silver Tile?")
            if response == "y":
                silverTile()
            '''  
            
            
            if tileColour() == 1:
                print("silver Tile")
                silverTile()
                
            if tileColour() == 0:
                print("Black Tile")
                blackTile()
            else:
                directionToGo = 0#relativePositionCode(upTiles,rightTiles,downTiles,leftTiles)
                lastDirection = directionToGo
            
            print("----LIDAR MEASUREMENTS REL----")
            print("  LEFT, RIGHT, FORWARD, BACK")
            print(lidarArray[27],lidarArray[9],lidarArray[0],lidarArray[18])
            print("-------------Tile-------------")
            print(leftTiles,rightTiles,upTiles,downTiles)
            print("----------Direction-----------")
            print(directionToGo)
            print("------------------------------")
            
            
            
            
            if directionToGo is not None:
                
                moveDirection(directionToGo)
            stringMap = "M;"
            
            for outside in reversed(map):
                for inside in reversed(outside):
                    stringMap += "%i,"%(inside)
            stringMap = stringMap[:-1] 
            
            bluetooth.send_string("%s %s" % ("[BLUE]:",stringMap))
            # time.sleep(2)
            print("-------------------------------------------")
            print("")
    else:
        StopMotors()
        #print(PauseButton())
    
'''
while True:
    print("Getting Lidar Data and finishing turn")
    lidarArray = readLidar()
    finishTurn(lidarArray)
    print("Done")
    time.sleep(3)
    '''