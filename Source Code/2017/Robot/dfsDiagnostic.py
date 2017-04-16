import time
import math
#X,Y
#Y goes up when the robot goes up
#X goes up when the robot goes right
#ALL COORDINATES ARE Y,X

KP = 0.5
KI = 0.5
KD = 0.5

map = []
for width in range(0,9):
    map.append([])
    for height in range(0,9):
        map[width].append(0)
print("COMPLETED MAP CREATION")
coords = [4,4]
explored = []
backtraceArray = [[coords[0],coords[1]]]
tileSize = 300

def getCurrentAngle():
    return 8

def getLidarValues():
    #PUT CODE HERE TO SEND LIDAR VALUS BACK
    return []


lastError = 0
integral = 0
derivative = 0
proportion = 0

movingForward = True

def moveForward():
    lidarData = getLidarValues()
    if movingForward and lidarData is not None:
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

        #Modulo all the pid values
        leftOnePidVal %= modOne
        leftTwoPidVal %= tileSize
        leftThreePidVal %= modTwo
        rightOnePidVal %= modOne
        rightTwoPidVal %= tileSize
        rightThreePidVal %= modTwo

        #actual PID
        proportion = rightTwoPidVal - leftTwoPidVal
        integral += proportion
        derivative = proportion - lastError
        lastError = proportion

        turn = KP * proportion + KI * integral + KD * derivative

        leftMotorSpeed = 100 - turn
        rightMotorSpeed = 100 + turn

        #CALL MOTOR CODE



def turn(currentAngle,toAngle):
    movingForward = False
    #MoveMotors
    #LEFT SIDE RIGHT SIDE
    if abs((currentAngle - toAngle) % 360) < 3:
        #FINISHED TURNING
        movingForward = True
        return True
    elif abs((currentAngle - toAngle) % 360) < 180:
        #LEFT
        #WHERE THE CODE GOES
        rightMotorSpeed = (abs((currentAngle - toAngle) % 360) / 180) * 100
        leftMotorSpeed = -((abs((currentAngle - toAngle) % 360) / 180) * 100)
    else:
        #RIGHT
        #WHERE THE CODE GOES
        leftMotorSpeed = (abs((currentAngle - toAngle) % 360) / 180) * 100
        rightMotorSpeed = -((abs((currentAngle - toAngle) % 360) / 180) * 100)

    time.sleep(0.05)
    turn(getCurrentAngle(),toAngle)

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


#where maptile is 0, then it's unknown and unexplored. 9 is wall, and 1 is explored.
def useLidar(lidarArray):
    directionToGo = useLidarToCalculateNextMotion(lidarArray[2])
    if directionToGo is not None:
        #NEW INSTRUCTIONS MY DUDE
        callMotors(directionToGo)
    sleep(5)

def numberFitsEnvelope(number, desired, envelope):
    if abs(number - desired) < envelope:
        return True
    return False

def useLidarToCalculateNextMotion(lidarArray):
    #LIDAR DATA IS THIRD ELEMENT IN ARRAY
    bestForwardsMeasurement = 0.0
    numOfForwards = 0
    bestRightMeasurement = 0.0
    numOfRights = 0
    bestDownMeasurement = 0.0
    numOfDowns = 0
    bestLeftMeasurement = 0.0
    numOfLefts = 0
    for i in range(0,(len(lidarArray) - 1)):
        if i < 2 or i > 358:
            #UP VALUES
            if lidarArray[i] is not None:
                numOfForwards += 1
                length = abs(math.cos(i) * lidarArray[i])
                bestForwardsMeasurement += length
        if i < 92 and i > 88:
            #RIGHT VALUES
            if lidarArray[i] is not None:
                numOfRights += 1
                length = abs(math.cos(i) * lidarArray[i])
                bestRightMeasurement += length
        if i < 182 and i > 178:
            #DOWN VALUES
            if lidarArray[i] is not None:
                numOfDowns += 1
                length = abs(math.cos(i) * lidarArray[i])
                bestDownMeasurement += length
        if i < 272 and i > 268:
            #LEFT VALUES
            if lidarArray[i] is not None:
                numOfLefts += 1
                length = abs(math.cos(i) * lidarArray[i])
                bestLeftMeasurement += length

    #Make Averages
    bestLeftMeasurement /= numOfLefts
    bestRightMeasurement /= numOfRights
    bestForwardsMeasurement /= numOfForwards
    bestDownMeasurement /= numOfDowns

    if numberFitsEnvelope(bestForwardsMeasurement % tileSize, tileSize / 2, tileSize / 10):
        #xd number fits what2donow?
        forwardsTiles = int(bestForwardsMeasurement / tileSize)
        backwardsTiles = int(bestDownMeasurement / tileSize)
        leftTiles = int(bestLeftMeasurement / tileSize)
        rightTiles = int(bestRightMeasurement / tileSize)
        return relativePositionCode(forwardsTiles,rightTiles,backwardsTiles,leftTiles)

    return None

#CurrentFacingDirection
currentFacingDirection = 0
lastSentCoords = []
def relativePositionCode(up,right,down,left):
    directions = [up,right,down,left]
    if currentFacingDirection == 1:
        #FACING RIGHT SO, UP BECOMES RIGHT, RIGHT BECOMES DOWN, DOWN BECOMES LEFT AND LEFT BECOMES UP
        directions[left,up,right,down]
    elif currentFacingDirection == 2:
        #EVERYTHING CHANGES Xdddddddddd
        directions[down,left,up,right]
    elif currentFacingDirection == 3:
        directions[right,down,left,up]
    if directions != lastSentCoords:
        #IF FACING 0, GO THE DIRECTION RETURNED, AND SET DIRECTION TO directions
        #SUBTRACT NEW DIRECTION FROM FACING DIRECTION % 4
        returnDirection = DFS(directions[0],directions[1],directions[2],directions[3])
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
while True:
    up = input("up: ")
    right = input("right: ")
    down = input("down: ")
    left = input("left: ")
    print(DFS(int(up),int(right),int(down),int(left)))
    for thing in map[::-1]:
        print(thing)
    '''print("[",end='')
    for y in range(0,len(map)):
        for x in range(0,len(map[y])):
            if (y + 1) == coords[0] and x == coords[1]:
                print("R",end='')
            else:
                print(map[::-1][y][x],end='')
            if x != len(map[y]) - 1:
                print(", ",end='')
            else:
                print("]")
                if y != len(map) - 1:
                    print("[",end='')'''
