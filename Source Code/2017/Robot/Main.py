print("----------------Initialising----------------\n")
#valid ramp
#flash on boot
#Valid tile movement - (Time?)
#crash button Combo
print(">Beging Imports")
import zmq
import time
import json
import math
import atexit
import subprocess
from copy import copy, deepcopy
print(">DONE\n")

print(">Begining Importing Seperate Code Blocks\n")
from Touch import *
from Light import *
from Victims import *
from Accel import *
#-30 UP || 20 DOWN
print(">DONE\n")
context = zmq.Context()

print(">Creating ZMQ Sockets")

lidar = context.socket(zmq.SUB)
lidar.setsockopt(zmq.CONFLATE, 1)
lidar.connect("tcp://localhost:5556")

bluetooth = context.socket(zmq.PUB)
bluetooth.set_hwm(10)
bluetooth.bind("tcp://*:5558")

motors = context.socket(zmq.REQ)
motors.connect("tcp://localhost:5557")
print(">DONE\n")

integral = 0
derivative = 0
proportion = 0
last_error = 0

RampIntegral = 0
RampDerivative = 0
RampProportion = 0
RampLast_error = 0

filter = "[LIDAR]"
filter = filter.decode('ascii')
lidar.setsockopt_string(zmq.SUBSCRIBE, filter)

global currentFacingDirection
currentFacingDirection = 0

global currentFacingDirectionLast
currentFacingDirectionLast = 0

startBaseMotorSpeed = 37
FarBaseMotorSpeed = 20
TilePlacementThresh = 10

DirectionChange = 0
lastTileMovementDir = 0

TileTouchSensorRecorrections = 0

global baseMotorSpeed
baseMotorSpeed = startBaseMotorSpeed

global robotOnRamp
robotOnRamp = False

global robotWasOnRamp
robotWasOnRamp = False

global robotRampDirection
robotRampDirection = None

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

TicksOnRamp = 0
robotZ = 1

startTileTime = 0

RAMP_UP_ANGLE = 18.5
RAMP_DOWN_ANGLE = -18

print(">Creating DFS Map")
map = []
for depth in range(0,5):
    map.append([])
    for width in range(0,75):
        map[depth].append([])
        for height in range(0,75):
            map[depth][width].append(0)
print(">DONE\n")

coords = [37,37]
explored = []
backtraceArray = [[coords[0],coords[1],robotZ]]

def exit_handler():
    print 'Program Shutting Down...'
    StopMotors()
    
atexit.register(exit_handler)
print("--------------------------------------------\n\n\n")
#
#
def turn(currentAngle,toAngle,counter,lidarArray = []):
    global paused
    stuckOnSpin = 110
    
    if PauseButton():
        paused = not paused
        StopMotors()
        time.sleep(2)
        
        while PauseButton():
                time.sleep(0.5)
                
    if not paused:
        if counter % 2 == 0:
            lidarArray = readLidar()
        
        checkVictims(lidarArray)
            
        if currentAngle == None:
            time.sleep(0.05)
            return turn(getCurrentAngle(),toAngle,(counter + 1),lidarArray)
        
        if counter % 50 == 0:
            fixTurnOnObstacle(counter / 100)
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
            
        angle = getCurrentAngle()  
        bluetooth.send_string("%s %s" % ("[BLUE]:","CMP;%i"%int(angle)))
        return turn(angle,toAngle,(counter + 1),lidarArray)

def PID(lidarDistanceArray):
    global proportion
    global integral
    global derivative
    global last_error
    global baseMotorSpeed
    global TileTouchSensorRecorrections
    KP = 0.5
    KI = 0.04
    KD = 0.45
    
    offset = 2
    minLength = 200
    
    angle = ((offset * 10) * math.pi / 180)
    DesiredDistance = 135
    
    Right = 0
    Left = 0
    
    FrontLeft = math.cos(angle) * lidarDistanceArray[9 - offset]
    BackLeft = math.cos(angle) * lidarDistanceArray[9 + offset]
    FrontRight = math.cos(angle) * lidarDistanceArray[27 + offset]
    BackRight = math.cos(angle) * lidarDistanceArray[27 - offset]
    
    if FrontLeft < minLength and BackLeft < minLength and FrontRight < minLength and BackRight < minLength:
        differnece = ((BackLeft - FrontLeft) + (FrontRight - BackRight)) / 2
        distDiffernece = (DesiredDistance - FrontLeft + FrontRight - DesiredDistance) / 2
    
    elif FrontLeft < minLength and BackLeft < minLength:
        differnece = BackLeft - FrontLeft
        distDiffernece = DesiredDistance - FrontLeft

    elif FrontRight < minLength and BackRight < minLength:
        differnece = FrontRight - BackRight
        distDiffernece = FrontRight - DesiredDistance

    else:
        distDiffernece = 0
        differnece = 0
        angle = getCurrentAngle()
        if currentFacingDirection == 0:
            if angle > 180:
                
                differnece = (angle - 360)
            else:
                
                differnece = angle
        else:

            differnece = (angle - (90 * currentFacingDirection))
            
        if lidarDistanceArray[0] > 200: 
            if lidarDistanceArray[2] < 200:
                distDiffernece = 40
                print("NOT A GOOD WALL 1")
            elif lidarDistanceArray[33] < 200:
                distDiffernece = -40
                print("NOT A GOOD WALL 2")
               
    TouchSensorValues = TouchSensors()
    if TouchSensorValues[0]:
        print("Touch Sensor Right Pressed")
        fixForwardWithSideObstacle(0)
        TileTouchSensorRecorrections += 1
    elif TouchSensorValues[3]:
        print("Touch Sensor Right Pressed")
        fixForwardWithSideObstacle(1)
        TileTouchSensorRecorrections += 1
                
    proportion = (differnece + distDiffernece / 1)
    
    integral  += proportion
    derivative = proportion - last_error
    last_error = proportion
    
    turn = KP*proportion + KI*integral + KD*derivative
    
    MoveMotors(baseMotorSpeed - turn,baseMotorSpeed + turn)  

def RampPID(lidarDistanceArray,pitch):
    global RampProportion
    global RampIntegral
    global RampDerivative
    global RampLast_error
    
    KP = 0.3
    KI = 0.01
    KD = 0.3
    
    offset = 2
    minLength = 240
    
    angle = ((offset * 10) * math.pi / 180)
    DesiredDistance = 140
    
    Right = 0
    Left = 0
    
    if pitch > 0:
        baseRampSpeed = 60
    else:
        baseRampSpeed = 40
        KP = 0.2
        KI = 0.01
        KD = 0.2
    
    FrontLeft = math.cos(angle) * lidarDistanceArray[9 - offset]
    BackLeft = math.cos(angle) * lidarDistanceArray[9 + offset]
    FrontRight = math.cos(angle) * lidarDistanceArray[27 + offset]
    BackRight = math.cos(angle) * lidarDistanceArray[27 - offset]
    
    if(FrontLeft < minLength and BackLeft < minLength and FrontRight < minLength and BackRight < minLength):
        differnece = (BackLeft - FrontLeft) + (FrontRight - BackRight)
        distDiffernece = DesiredDistance - min(FrontLeft,DesiredDistance + 21) + min(FrontRight,DesiredDistance + 21) - DesiredDistance
        
    else:
        distDiffernece = 0
        differnece = 0
        angle = getCurrentAngle()
        
        if currentFacingDirection == 0:
            if angle > 180:
                
                differnece = (angle - 360)
            else:
                
                differnece = angle
        else:

            differnece = (angle - (90 * currentFacingDirection))
        
    RampProportion = differnece + distDiffernece / 2
    
    RampIntegral  += RampProportion
    RampDerivative = RampProportion - RampLast_error
    RampLast_error = RampProportion
    
    turn = KP*RampProportion + KI*RampIntegral + KD*RampDerivative

    MoveMotors(baseRampSpeed-turn,baseRampSpeed + turn)

lastSentCoords = []
      
def validTiles(LidarData):
    presetValue = 8
    offset = 3
    tileSize = 300
    
    returnArray = []
    
    angleDistance = 140
    minDirectLength = 100
    for i in range(4):
        if i == 0:
            if LidarData[i * 9] > 230 and LidarData[i * 9 + 3] < 250 and LidarData[33] < 250 :
                returnArray.append(0)  
            else:
                returnArray.append(int(LidarData[i * 9] / tileSize))
        else:
            if LidarData[i * 9] > 230 and LidarData[i * 9 + 3] < 250 and LidarData[i * 9 - 3] < 250:
                returnArray.append(0)  
            else:
                returnArray.append(int(LidarData[i * 9] / tileSize))
        
    return returnArray
    
def moveDirection(direction):
    global currentFacingDirectionLast
    
    if currentFacingDirectionLast != direction:
        currentAngle = getCurrentAngle()
        turns = [0, 90, 180, 270]
        #if direction == 0:
        #    print("TURN NORTH")
        #    turn(currentAngle,0,0)
        #elif direction == 1:
        #    print("TURN EAST")
        #    turn(currentAngle,90,0)
        #elif direction == 2:
        #    print("TURN SOUTH")
        #    turn(currentAngle,180,0)
        #elif direction == 3:
        #    print("TURN WEST")
        #    turn(currentAngle,270,0)
        if abs(currentAngle - turns[direction]) > 135 and abs(currentAngle - turns[direction]) < 225:
            dt = turns[direction] - ((turns[direction] - currentAngle) / 2)
            turn(currentAngle, dt, 0)
            time.sleep(0.5)
            checkVictims(readLidar())
            turn(currentAngle, turns[direction], 0)
            checkVictims(readLidar())
        else:
            turn(currentAngle, turns[direction], 0)
            
        finishTurn(lidarArray)
            
        currentFacingDirectionLast = currentFacingDirection
            
def readLidar():
    lidarINPUT = lidar.recv_string().split(":")
    lidarINPUT = json.loads(lidarINPUT[1])
    return lidarINPUT

            
def checkVictims(lidarTiles):
    validateVictimDetection(readCamera(0,LeftCam),lidarTiles)
    validateVictimDetection(readCamera(1,RightCam),lidarTiles)
    validateVictimDetection(readHeat(0),lidarTiles)
    validateVictimDetection(readHeat(1),lidarTiles)


#side return
# 0 = L
# 1 = R

#data structure
#[side,char]

def validateVictimDetection(sensorData,lidarData):
    lidarTiles = validTiles(lidarData)
    if sensorData[1] == 0:
        return 0
        
    if (sensorData[0] == 0 and lidarTiles[3] == 0) or (sensorData[0] == 1 and lidarTiles[1] == 0): #Left - Right
        
        bluetooth.send_string("[BLUE]:VIC;Victim Detected")
        print(">victimDetected")
        
        if nextTileDir:
            distance = lidarData[0]
        else:
            distance = lidarData[18]
            
        if nextTile != None:
            HalfWay = abs(distance - nextTile) > (tileSize / 2)
    
            if victimOn(True,False):
                StopMotors()
                time.sleep(1)
                dropRescueKit(True,sensorData[1],sensorData[0])
        else:
            print(">Next Tile was equal to None!")
            
            if victimOn(True,False):
                StopMotors()
                time.sleep(1)
                dropRescueKit(True,sensorData[1],sensorData[0])
    else:
        print(">Detected possible victim but it didnt work out")
        return 0

def MoveMotors(Linput,Rinput):
    motors.send(b"%i,%i" % (Linput,Rinput))
    message = motors.recv()
    
def StopMotors():
    motors.send(b"%i,%i" % (0,0))
    message = motors.recv()

def MoveForward(lidarData,pitch):
    global robotRampDirection
    
    if pitch > RAMP_UP_ANGLE:
        
        robotRampDirection = True
        
    elif pitch < RAMP_DOWN_ANGLE:
        robotRampDirection = False
        
        
    elif numberFitsEnvelope(lidarData[0],lidarData[18], TilePlacementThresh):
        return False
    return True
    
def finishTurn(lidarDistanceArray):
    global paused
    
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
    turnTileSize = 220
    obstacleThresh = 10
    lidarDistanceArray = readLidar()
    LoopCountFinTurn = 0
    
    if(lidarDistanceArray[8] < turnTileSize and lidarDistanceArray[8] > 0 and lidarDistanceArray[10] < turnTileSize and lidarDistanceArray[10] > 0 and abs((lidarDistanceArray[8] + lidarDistanceArray[10]) / 2 - lidarDistanceArray[9]) < obstacleThresh):

        for i in range(2):  
            lidarDistanceArray = readLidar()
            Front = math.cos(angle) * lidarDistanceArray[9 - offset]
            Back = math.cos(angle) * lidarDistanceArray[9 + offset]
            
            while(abs(Back - Front) > 1 and not paused and LoopCountFinTurn < 20):

                if PauseButton():
                    paused = not paused
                    StopMotors()
                    
                    while PauseButton():
                        time.sleep(0.5)

                lidarDistanceArray = readLidar()
    
                Front = math.cos(angle) * lidarDistanceArray[9 - offset]
                Back = math.cos(angle) * lidarDistanceArray[9 + offset]
            
                proportion = Back - Front
                
                integral  += proportion
                derivative = proportion - last_error
                last_error = proportion
                
                turn = KP*proportion + KI*integral + KD*derivative
                
                if(abs(turn) < 10 and abs(turn) > 0):
                    turn = (turn / abs(turn)) * 10
                elif(abs(turn) < 10):
                    turn = 10
                    
                MoveMotors(-turn, turn)
                LoopCountFinTurn += 1
                
    elif(lidarDistanceArray[26] < turnTileSize and lidarDistanceArray[26] > 0 and lidarDistanceArray[28] < turnTileSize and lidarDistanceArray[28] > 0 and abs((lidarDistanceArray[26] + lidarDistanceArray[28]) / 2 - lidarDistanceArray[27]) < obstacleThresh):
        for i in range(2):  
            lidarDistanceArray = readLidar()
            Front = math.cos(angle) * lidarDistanceArray[27 - offset]
            Back = math.cos(angle) * lidarDistanceArray[27 + offset]
            
            while(abs(Back - Front) > 1 and not paused and LoopCountFinTurn < 20):

                if PauseButton():
                    paused = not paused
                    StopMotors()
                    
                    while PauseButton():
                        time.sleep(0.5)
                            
                lidarDistanceArray = readLidar()
    
                Front = math.cos(angle) * lidarDistanceArray[27 - offset]
                Back = math.cos(angle) * lidarDistanceArray[27 + offset]
            
                proportion = Back - Front
                
                integral  += proportion
                derivative = proportion - last_error
                last_error = proportion
                
                turn = KP*proportion + KI*integral + KD*derivative
                
                if(abs(turn) < 10 and abs(turn) > 0):
                    turn = (turn / abs(turn)) * 10
                elif(abs(turn) < 10):
                    turn = 10

                MoveMotors(-turn, turn)
                LoopCountFinTurn += 1
    else:
        LoopCountFinTurn = 0
        print("FinishTurn:No wall to use")
        return False
    LoopCountFinTurn = 0   
    StopMotors()
    return True

def fixForwardWithSideObstacle(side):
    if side == 0:
        MoveMotors(-60, -10)
        time.sleep(0.4)
        MoveMotors(-10, -60)
        time.sleep(0.4)
        MoveMotors(40, 30)
    else:
        MoveMotors(-10, -60)
        time.sleep(0.4)
        MoveMotors(-60, -10)
        time.sleep(0.4)
        MoveMotors(30, 40)

    time.sleep(0.8)
    MoveMotors(0, 0)
    
def fixTurnOnObstacle(attempt):
    StopMotors()
    print("Begining Builtin Movements - turn")
    if attempt == 1:
        print("1")
        MoveMotors(100, 100)
        time.sleep(0.6)
        MoveMotors(0, 0)

    elif attempt == 1.5:
        print("2")
        MoveMotors(-100, -100)
        time.sleep(0.6)
        MoveMotors(0, 0)
    elif attempt == 2:
        print("2")
        MoveMotors(-50, -100)
        time.sleep(0.6)
        MoveMotors(0, 0)
    elif attempt == 2.5:
        print("2")
        MoveMotors(100, 50)
        time.sleep(0.6)
        MoveMotors(0, 0)
    elif attempt == 3:
        print("3")
        MoveMotors(0, -100)
        time.sleep(0.6)
        MoveMotors(0, 0)
    elif attempt == 3.5:
        print("3")
        MoveMotors(-100, 0)
        time.sleep(0.6)
        MoveMotors(0, 0)

def wentUpRamp():
    global robotZ
    global backtracing
    map[robotZ][coords[0]][coords[1]] = 7
    backtraceArray[len(backtraceArray) - 1][2] = deepcopy(robotZ) + 1
    #if backtracing:
    #    robotZ -= 1
    #else:
    robotZ += 1
    
    ramp = returnTileAtDeltaDirection(2,(currentFacingDirection + 2) % 4, coords)
    map[robotZ][ramp[0]][ramp[1]] = 1
    

def wentDownRamp():
    global robotZ
    global backtracing
    map[robotZ][coords[0]][coords[1]] = 7
    backtraceArray[len(backtraceArray) - 1][2] = deepcopy(robotZ) - 1
    #if backtracing:
    robotZ -= 1
    #else:
    #    robotZ += 1
    ramp = returnTileAtDeltaDirection(2,(currentFacingDirection + 2) % 4, coords)
    map[robotZ][ramp[0]][ramp[1]] = 1
    
def numberFitsEnvelope(front, back, envelope):
    global baseMotorSpeed
    global nextTile
    global nextTileDir
    global firstMove
    global robotWasOnRamp
    global DirectionChange
    global lastTileMovementDir
    global startTileTime
    
    distance = 0
    TileMoved = False
    
    TileFineMovement = (tileSize / envelope) * 2
    speedDivider = 3
    #decide on next tile distance
    if not robotOnRamp and not robotWasOnRamp:
        if nextTile == None:
            if front < back and front > 150:
                nextTileDir = True
                distance = front
                nextTile = (int(distance / tileSize)) * tileSize - 185
                baseMotorSpeed = startBaseMotorSpeed
                
            elif back > 150:
                nextTileDir = False
                distance = back
                nextTile = (int(distance / tileSize) + 1) * tileSize + 160
                baseMotorSpeed = startBaseMotorSpeed
            
            startTileTime = time.time()
            
        else:        
            if nextTileDir and front > 0:
                distance = front
                #baseMotorSpeed = (int(distance) - nextTile) / 5
                if distance < 800:
                    if (int(distance) - nextTile) > TileFineMovement:
                        baseMotorSpeed = startBaseMotorSpeed
                    else:
                        baseMotorSpeed = startBaseMotorSpeed / 2
                else:
                    baseMotorSpeed = FarBaseMotorSpeed
                    
                TileMoved = distance - nextTile < (tileSize / envelope)
                
            elif back > 0:
                distance = back
                if distance < 800:
                    if -(int(distance) - nextTile) > TileFineMovement:
                        baseMotorSpeed = startBaseMotorSpeed
                    else:
                        baseMotorSpeed = startBaseMotorSpeed / 2
                else:
                    baseMotorSpeed = FarBaseMotorSpeed
                 
                TileMoved = nextTile - distance < (tileSize / envelope)
            
            TouchSensorValues = TouchSensors()    
            lessThanTile = (front < 150 and front > 0 or TouchSensorValues[1] or TouchSensorValues[2])
            
            currentTime = time.time()
            if lessThanTile or (TileMoved and (currentTime - startTileTime) > 2) or nextTile < 0 or firstMove or TileTouchSensorRecorrections >= 3:
                #print("Finished Tile Movements:")
                #print((currentTime - startTileTime))
                #print([lessThanTile,TileMoved,nextTile < 0])
                startTileTime = 0
                DirectionChange = 0
                TicksOnRamp = 0
                firstMove = False
                nextTile = None
                nextTileDir = None
                return True
                
    elif(robotWasOnRamp == True and not robotOnRamp):
        MoveMotors(baseMotorSpeed/2,baseMotorSpeed/2)
        time.sleep(1.8)
        
        nextTile = (int(readLidar()[0] / tileSize) + 1) * tileSize 
        
        print("OKAY POSITION IN TILE COMMENCE")
        print(nextTile)
        print(front)
        
        if robotRampDirection != None:
            if robotRampDirection:
                wentUpRamp()
                print("Going Up Ramp")
            else:
                wentDownRamp()
                print("Going Down Ramp")
                    
        nextTileDir = True
        distance = front
        robotWasOnRamp = False
            
    else:
        firstMove = False
        nextTile = None
        nextTileDir = None

    return False

def positionForwardTile(front):
    
    print("positionForwardTile")
    while front > 135:
        front = readLidar()[0]
        MoveMotors(baseMotorSpeed/2,baseMotorSpeed/2)
        time.sleep(0.1)
        
def changeMap(up,right,down,left):
    
    if coords[0] + (up * 2) > len(map[robotZ]):
        up = 0
        print("Index out of range exception should have happened here")
        bluetooth.send_string("[BLUE]:MES;Index out of range error should have occured! Invalidated value (up) in question.")
    
    if coords[0] - (down * 2) < 0:
        down = 0
        print("Index out of range exception should have happened here")
        bluetooth.send_string("[BLUE]:MES;Index out of range error should have occured! Invalidated value (down) in question.")
    
    if coords[1] + (right * 2) > len(map[robotZ][coords[0]]):
        right = 0
        print("Index out of range exception should have happened here")
        bluetooth.send_string("[BLUE]:MES;Index out of range error should have occured! Invalidated value (right) in question.")
    
    if coords[1] - (left * 2) < 0:
        left = 0
        print("Index out of range exception should have happened here")
        bluetooth.send_string("[BLUE]:MES;Index out of range error should have occured! Invalidated value (left) in question.")
    
    #coords[0] - (down * 2) < 0 or coords[1] + (right * 2) > len(map[robotZ][coords[0]]) or coords[1] - (left * 2) < 0
    
    
    print(up, right, down, left)
    print(coords)
    for x in range(1,up * 2,2):
        if map[robotZ][coords[0] + x][coords[1]] == 0:
            map[robotZ][coords[0] + x][coords[1]] = 0
            
    if map[robotZ][coords[0] + (up * 2) + 1][coords[1]] == 0:
        map[robotZ][coords[0] + (up * 2) + 1][coords[1]] = 9
    for x in range(1,right * 2,2):
        if map[robotZ][coords[0]][coords[1] + x] == 0:
            map[robotZ][coords[0]][coords[1] + x] = 0
            
    if map[robotZ][coords[0]][coords[1] + (right * 2) + 1] == 0:
        map[robotZ][coords[0]][coords[1] + (right * 2) + 1] = 9
    for x in range(1,down * 2,2):
        if map[robotZ][coords[0] - x][coords[1]] == 0:
            map[robotZ][coords[0] - x][coords[1]] = 0
    if map[robotZ][coords[0] - (down * 2) - 1][coords[1]] == 0:
        map[robotZ][coords[0] - (down * 2) - 1][coords[1]] = 9
    for x in range(1,left * 2,2):
        if map[robotZ][coords[0]][coords[1] - x] == 0:
            map[robotZ][coords[0]][coords[1] - x] = 0
    if map[robotZ][coords[0]][coords[1] - (left * 2) - 1] == 0:
        map[robotZ][coords[0]][coords[1] - (left * 2) - 1] = 9

def adjacentUnexploredTile(at):
    x = at[0]
    y = at[1]
    
    if map[robotZ][x + 1][y] == 0:
        if map[robotZ][x + 2][y] == 0:
            return True
    if map[robotZ][x - 1][y] == 0:
        if map[robotZ][x - 2][y] == 0:
            return True
    if map[robotZ][x][y + 1] == 0:
        if map[robotZ][x][y + 2] == 0:
            return True
    if map[robotZ][x][y - 1] == 0:
        if map[robotZ][x][y - 2] == 0:
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
        
        if coords[0] == backtraceArray[i][0] and coords[1] == backtraceArray[i][1] and robotZ == backtraceArray[i][2]:
            compatibleIndex = i
        elif coords[0] == backtraceArray[i][0] or coords[1] == backtraceArray[i][1]:
            #This means an adjacent tile
            print(dx,dy)
            if math.pow(dy,2) + math.pow(dx,2) == 4 and backtraceArray[i][2] == robotZ:
                #Are is there anything 1 tile away
                print("1 tile away from the backtrace array")
                if dx > 0:
                    #dx > 0 therefore robot is further to the right than the tile it's aiming at
                    if map[robotZ][coords[0]][coords[1] - 1] == 0:
                        # there is no wall to the left
                        print("No wall to the left. Valid.")
                        compatibleIndex = i
                elif dx < 0:
                    #dx < 0 therefore robot is further to the left than the tile it's aiming at
                    if map[robotZ][coords[0]][coords[1] + 1] == 0:
                        # there is no wall to the left
                        print("No wall to the right. Valid.")
                        compatibleIndex = i
                elif dy > 0:
                    #dy > 0 therefore the robot's location is higher up than the tile location. The tile is below.
                    if map[robotZ][coords[0] - 1][coords[1]] == 0:
                        # there is no wall below
                        print("No wall underneath. Valid.")
                        compatibleIndex = i
                elif dy < 0:
                    #dy < 0 therefore the robot's location is lower down than the tile location. The tile is above.
                    if map[robotZ][coords[0] + 1][coords[1]] == 0:
                        # there is no wall below
                        print("No wall above. Valid.")
                        compatibleIndex = i
        if adjacentUnexploredTile(backtraceArray[i]):
            break
        print("-----------------")
    print(compatibleIndex)
    
    print(backtraceArray[compatibleIndex])
    
    
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
lastLastCoords = deepcopy(lastCoords)

backtracing = False

def DFS(up,right,down,left):
    global lastBacktracePoint
    global lastCoords
    global backtracing
    changeMap(up,right,down,left)
    decided = False
    directionToMove = -1
    lastLastCoords = deepcopy(lastCoords)
    lastCoords = deepcopy(coords)
    if map[robotZ][coords[0]][coords[1]] == 0:
        map[robotZ][coords[0]][coords[1]] = 1
        
    if currentFacingDirection == 0:
        if up > 0 and decided == False:
            nextTile = map[robotZ][coords[0] + 2][coords[1]]
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
            nextTile = map[robotZ][coords[0]][coords[1] + 2]
            if nextTile == 0:
                decided = True
                print("FACING 0 MOVED 1")
                #Move right
                coords[1] += 2
                directionToMove = 1
        if down > 0 and decided == False:
            nextTile = map[robotZ][coords[0] - 2][coords[1]]
            if nextTile == 0:
                decided = True
                print("FACING 0 MOVED 2")
                #Move down
                coords[0] -= 2
                directionToMove = 2
        if left > 0 and decided == False:
            nextTile = map[robotZ][coords[0]][coords[1] - 2]
            if nextTile == 0:
                decided = True
                print("FACING 0 MOVED 3")
                #Move left
                coords[1] -= 2
                directionToMove = 3
    elif currentFacingDirection == 1:
        if right > 0 and decided == False:
            nextTile = map[robotZ][coords[0]][coords[1] + 2]
            if nextTile == 0:
                decided = True
                print("FACING 1 MOVED 1")
                #Move right
                coords[1] += 2
                directionToMove = 1
        if down > 0 and decided == False:
            nextTile = map[robotZ][coords[0] - 2][coords[1]]
            if nextTile == 0:
                decided = True
                print("FACING 1 MOVED 2")
                #Move down
                coords[0] -= 2
                directionToMove = 2
        if left > 0 and decided == False:
            nextTile = map[robotZ][coords[0]][coords[1] - 2]
            if nextTile == 0:
                decided = True
                print("FACING 1 MOVED 3")
                #Move left
                coords[1] -= 2
                directionToMove = 3
        if up > 0 and decided == False:
            nextTile = map[robotZ][coords[0] + 2][coords[1]]
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
            nextTile = map[robotZ][coords[0] - 2][coords[1]]
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
            nextTile = map[robotZ][coords[0]][coords[1] - 2]
            if nextTile == 0:
                decided = True
                print("FACING 2 MOVED 3")
                #Move left
                coords[1] -= 2
                directionToMove = 3
        if up > 0 and decided == False:
            nextTile = map[robotZ][coords[0] + 2][coords[1]]
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
            nextTile = map[robotZ][coords[0]][coords[1] + 2]
            if nextTile == 0:
                decided = True
                print("FACING 2 MOVED 1")
                #Move right
                coords[1] += 2
                directionToMove = 1
    elif currentFacingDirection == 3:
        if left > 0 and decided == False:
            nextTile = map[robotZ][coords[0]][coords[1] - 2]
            if nextTile == 0:
                decided = True
                print("FACING 3 MOVED 3")
                #Move left
                coords[1] -= 2
                directionToMove = 3
        if up > 0 and decided == False:
            nextTile = map[robotZ][coords[0] + 2][coords[1]]
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
            nextTile = map[robotZ][coords[0]][coords[1] + 2]
            if nextTile == 0:
                decided = True
                print("FACING 3 MOVED 1")
                #Move right
                coords[1] += 2
                directionToMove = 1
        if down > 0 and decided == False:
            nextTile = map[robotZ][coords[0] - 2][coords[1]]
            if nextTile == 0:
                decided = True
                print("FACING 3 MOVED 2")
                #Move down
                coords[0] -= 2
                directionToMove = 2
    if directionToMove != -1:
        backtracing = False
        print("Found a direction to move")
        print(directionToMove)
        print("-------------------------")
        #Exploration logic found a solution, should not backtrack
        backtraceArray.append([coords[0],coords[1],robotZ])
        
        #ISSUE: THE CURRENT POSITION ISN"T APPENDED TO THE BACKTRACE ARRAY UPON FINISHING BACKTRACING
        
        return directionToMove
    elif len(backtraceArray) >= 2:
        backtracing = True
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
        #if lastLastCoords[0] == backtracePoint[0] and lastLastCoords[1] == backtracePoint[1] and backtracePoint[2] != robotZ:
        #    print("DID A THING")
        #    return DFS(up,right,down,left)
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
        

def returnTileAtDeltaDirection(distance,direction,basecoords):
    if direction == 0:
        return [basecoords[0] + distance, basecoords[1]]
    elif direction == 1:
        return [basecoords[0],basecoords[1] + distance]
    elif direction == 2:
        return [basecoords[0] - distance, basecoords[1]]
    elif direction == 3:
        return [basecoords[0], basecoords[1] - distance]

#HEAT TYPES
#4, 5, 6 are different heat types.
#4 means that there is heat to the lower side of the axis that the wall sits on (the left of the x axis, the top of the y axis)
#5 means the reverse, there is heat on the upper side of the axis
#6 means heat has been seen on both sides of the wall

lastDrop = [0,0]

def victimOn(leftSide,nextTile):
    
    global lastDrop
    
    print("VictimOn code runs")
    
    if pointDelta(coords, lastDrop) <= 2:
        return False
    
    if leftSide:
        #VICTIM is on the LEFT side of the robot
        direction = (currentFacingDirection - 1) % 4
        wallCoord = []
        
        if map[robotZ][coords[0]][coords[1]] == 1:
            return False
        
        if nextTile:
            wallCoord = returnTileAtDeltaDirection(1,direction,coords)
        else:
            wallCoord = returnTileAtDeltaDirection(1,direction, lastCoords)
        if direction == 1 or direction == 0:
            #DEAL WITH MOVING POSITIVE CASES
            if map[robotZ][wallCoord[0]][wallCoord[1]] == 9 or map[robotZ][wallCoord[0]][wallCoord[1]] == 0:
                print("Robot Should Drop!")
                map[robotZ][wallCoord[0]][wallCoord[1]] = 5
                lastDrop = deepcopy(coords)
                return True
            elif map[robotZ][wallCoord[0]][wallCoord[1]] == 4:
                print("Robot Should Drop!")
                map[robotZ][wallCoord[0]][wallCoord[1]] = 6
                lastDrop = deepcopy(coords)
                return True
        else:
            #DEAL WITH MOVING NEGATIVE CASES
            if map[robotZ][wallCoord[0]][wallCoord[1]] == 9 or map[robotZ][wallCoord[0]][wallCoord[1]] == 0:
                print("Robot Should Drop!")
                map[robotZ][wallCoord[0]][wallCoord[1]] = 4
                lastDrop = deepcopy(coords)
                return True
            elif map[robotZ][wallCoord[0]][wallCoord[1]] == 5:
                print("Robot Should Drop!")
                map[robotZ][wallCoord[0]][wallCoord[1]] = 6
                lastDrop = deepcopy(coords)
                return True
    else:
        #VICTIM is on the RIGHT side of the robot
        if map[robotZ][coords[0]][coords[1]] == 1:
            return False
        
        direction = (currentFacingDirection + 1) % 4
        wallCoord = []
        if nextTile:
            wallCoord = returnTileAtDeltaDirection(1,direction,coords)
        else:
            wallCoord = returnTileAtDeltaDirection(1,direction, lastCoords)
        if direction == 1 or direction == 0:
            #DEAL WITH MOVING POSITIVE CASES
            if map[robotZ][wallCoord[0]][wallCoord[1]] == 9 or map[robotZ][wallCoord[0]][wallCoord[1]] == 0:
                map[robotZ][wallCoord[0]][wallCoord[1]] = 5
                print("Robot Should Drop!")
                lastDrop = deepcopy(coords)
                return True
            elif map[robotZ][wallCoord[0]][wallCoord[1]] == 4:
                map[robotZ][wallCoord[0]][wallCoord[1]] = 6
                print("Robot Should Drop!")
                lastDrop = deepcopy(coords)
                return True
        else:
            #DEAL WITH MOVING NEGATIVE CASES
            if map[robotZ][wallCoord[0]][wallCoord[1]] == 9 or map[robotZ][wallCoord[0]][wallCoord[1]] == 0:
                map[robotZ][wallCoord[0]][wallCoord[1]] = 4
                print("Robot Should Drop!")
                lastDrop = deepcopy(coords)
                return True
            elif map[robotZ][wallCoord[0]][wallCoord[1]] == 5:
                map[robotZ][wallCoord[0]][wallCoord[1]] = 6
                print("Robot Should Drop!")
                lastDrop = deepcopy(coords)
                return True
    print("Robot Should NOT Drop!")
    return False
        

def blackTile():
    print("BLACK TILE")
    bluetooth.send_string("[BLUE]:LIT;BLACK")
    global coords
    global map
    global backtraceArray
    map[robotZ][coords[0]][coords[1]] = 9
    map[robotZ][coords[0]][coords[1] + 1] = 2
    map[robotZ][coords[0]][coords[1] - 1] = 2
    map[robotZ][coords[0] + 1][coords[1]] = 2
    map[robotZ][coords[0] - 1][coords[1]] = 2
    print("BLACK TILE AT")
    print(coords)
    print("MOVING BACK TO")
    coords = deepcopy(lastCoords)
    print(coords)
    backtraceArray.pop()

def MoveBackFromBlack(lidarArray):
    global paused
    
    envelope = 15
    
    front = lidarArray[0]
    back = lidarArray[18]
    
    distance = 0
    TileMoved = False
    baseMotorSpeed = 20
    nextTileDir = None
    startTime = time.time()
    
    if front < back and front > 100:
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
    
    while movingBack and not paused:
    
        if PauseButton():
            paused = not paused
            StopMotors()
            
            while PauseButton():
                    time.sleep(0.5)
                
        lidarArray = readLidar()
        
        front = lidarArray[0]
        back = lidarArray[18]
        
        if nextTileDir == True and front > 0:
            distance = front
            baseMotorSpeed = startBaseMotorSpeed / -2
            TileMoved = abs(distance - nextTile) < (tileSize / envelope)
        
        elif nextTileDir == False and back > 0:
            distance = back
            baseMotorSpeed = startBaseMotorSpeed / -2
            TileMoved = abs(distance - nextTile) < (tileSize / envelope)
        else:
            MoveMotors(-startBaseMotorSpeed/2,-startBaseMotorSpeed/2)
            time.sleep(2.5)
            TileMoved = True
            
        lessThanTile = (back < 140 and back > 0)

        if (lessThanTile or TileMoved) or nextTile < 0 or firstMove or (startTime - time.time()) > 2.8: 
            StopMotors()
            movingBack = False    
        else:
            MoveMotors(-startBaseMotorSpeed/2,-startBaseMotorSpeed/2)    
    
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
    
silverTileZ = deepcopy(robotZ)

def silverTile():
    print("SILVER TILE")
    bluetooth.send_string("[BLUE]:LIT;SILVER")
    global backtraceArray
    global silverBacktraceArray
    
    global coords
    global lastDirection
    global lastSilverTileCoords
    global lastSilverTileDirection
    
    lastSilverTileCoords = [coords[0],coords[1],robotZ]
    lastSilverTileDirection = int(str(lastDirection))
    silverBacktraceArray = deepcopy(backtraceArray)
    map[robotZ][coords[0]][coords[1]] = 3
    
    silverTileZ = deepcopy(robotZ)
    
    
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
    robotZ = lastSilverTileCoords[2]
    fta = deepcopy(forwardTraceArray)
    backtraceArray = silverBacktraceArray + fta
    print(len(fta))
    for element in reversed(fta):
        backtraceArray.append(element)
    backtraceArray.append([coords[0],coords[1],robotZ]);
    print("TRIED TO REVERT TO SILVER TILE")
    print(len(backtraceArray))
    print(backtraceArray)
    print(currentFacingDirection)
    
    robotZ = deepcopy(silverTileZ)
    
    
wasPaused = False
initialPause = True

def updateBluetoothMaps(lidarArray):
    
    bluetooth.send_string("%s TIL;%i,%i,%i,%i" % ("[BLUE]:",lidarArray[0],lidarArray[9],lidarArray[18],lidarArray[27]))
    
    stringMap = ""
    
    for outside in reversed(map[robotZ]):
        for inside in outside:
            stringMap += "%i,"%(inside)
    stringMap = stringMap[:-1] 
    
    if lastSilverTileCoords != []:
        bluetooth.send_string("%s LST;%i,%i" % ("[BLUE]:",lastSilverTileCoords[1],74 - lastSilverTileCoords[0]))
        
    bluetooth.send_string("%s CRD;%i,%i" % ("[BLUE]:",coords[1],74-coords[0]))
    bluetooth.send_string("%s BTA;%s" % ("[BLUE]:", json.dumps(backtraceArray, ensure_ascii=True)))
    bluetooth.send_string("%s MAP;%s" % ("[BLUE]:",stringMap))

print("------------------Main Code----------------")
print(">Robot Is Currently Paused")
flashLEDs(3)
bluetooth.send_string("[BLUE]:MES;Robot Ready!")
while True:
    
    if PauseButton():
        paused = not paused
        StopMotors()
        resetCamBuffer()
        time.sleep(1)
        
        if not initialPause:
            wasPaused = True
            firstMove = True
            
        if not paused:
            initialPause = False
            bluetooth.send_string("[BLUE]:PAU;FALSE")
        else:
            bluetooth.send_string("[BLUE]:PAU;TRUE")
        
        while PauseButton():
            time.sleep(0.5)
            
    if not paused:
        
        if wasPaused:
            wasPaused = False
            revertToSilverTile()

        lidarArray = readLidar()
        IMUAngle = getCurrentPitch()

        if MoveForward(lidarArray,IMUAngle):

            if IMUAngle < RAMP_UP_ANGLE and IMUAngle > RAMP_DOWN_ANGLE:
                checkVictims(lidarArray)
                PID(lidarArray)
                robotOnRamp = False
                TicksOnRamp = 0
            else:
                #print(">Ramp PID")
                
                #superteams
                blackTile()
                MoveBackFromBlack(lidarArray)
                
                '''
                checkVictims(lidarArray)
                RampPID(lidarArray,IMUAngle)
                TicksOnRamp += 1
                
                if TicksOnRamp > 5:
                    robotOnRamp = True
                    robotWasOnRamp = True'''
        else:

            StopMotors()
            time.sleep(0.2)
            lidarArray = readLidar()
            checkVictims(lidarArray)
            
            if robotRampDirection != None:
                if finishTurn(lidarArray):
                    pass
                robotRampDirection = None  

            if tileColour() == 1:
                print(">silver Tile")
                silverTile()
                
            if tileColour() == 0:
                print(">Black Tile")
                
                #superteams
                '''blackTile()
                MoveBackFromBlack(lidarArray)
                lidarArray = readLidar()'''
            if TileTouchSensorRecorrections >= 3:
                print(">Object Detected 3 Times Calling Black Tile")
                blackTile()
            TileTouchSensorRecorrections = 0
            
            directionToGo = relativePositionCode(validTiles(lidarArray))
            lastDirection = directionToGo
            
            print("----------LIDAR MEASUREMENTS REL-----------\n")
            print("-FORWARD-----RIGHT------BACKWARDS-----LEFT-")
            print(lidarArray[0],lidarArray[9],lidarArray[18],lidarArray[27])
            print("-------------------Tile--------------------")
            print(validTiles(lidarArray))
            print("-----------------Direction-----------------")
            print(directionToGo)
            print("-------------------------------------------")
            
            if directionToGo is not None and directionToGo >= 0:
                moveDirection(directionToGo)
            else:
                paused = True
                
            #checkVictims(lidarArray)    
            updateBluetoothMaps(lidarArray)
                
            print("--------------------------------------------")
            
    else:
        StopMotors()
        TouchSensorValuesRET = TouchSensors()
        
        if TouchSensorValuesRET[0] and TouchSensorValuesRET[1] and  TouchSensorValuesRET[3]:
            subprocess.call("systemctl stop mainrobot.service", shell=True)
        elif TouchSensorValuesRET[0] and TouchSensorValuesRET[1]:
            flashLEDs(4)
            bluetooth.send_string("[BLUE]:MES;RESETING IMU NOW")
            print(">RESETING IMU... NOW")
            resetIMU()
            bluetooth.send_string("[BLUE]:MES;RESETING IMU DONE")
            print(">RESETING IMU... DONE")
            flashLEDs(4)
        elif TouchSensorValuesRET[2] and TouchSensorValuesRET[1]:
            flashLEDs(3)