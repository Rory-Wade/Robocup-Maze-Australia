#!/usr/bin/env python
#
# dynamixel.py, based on the same by Mac Mason <mac@cs.duke.edu>
#
# Pythonic access to a Robotis AX-12 servo. Requires pySerial, but is
# otherwise pure Python, and should JustWork(TM).
#
# This code is made available under a Creative Commons
# Attribution-Noncommercial-Share-Alike 3.0 license. See
# <http://creativecommons.org/licenses/by-nc-sa/3.0> for details. If you'd
# like some other license, send me an e-mail. If you're doing something cool
# with this code, send me an e-mail, too: I'd like to see it.

import sys
import serial
import time
import zmq

print("Started")

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5557")

# The exposed EEPROM addresses
MODELNO_L     = [0x00] # R
MODELNO_H     = [0x01] # R
FWVERSION     = [0x02] # R
IDNUMBER      = [0x03] # RW
BAUDRATE      = [0x04] # RW
RETDELAY      = [0x05] # RW
CWANGLELIM_L  = [0x06] # RW
CWANGLELIM_H  = [0x07] # RW
CCWANGLELIM_L = [0x08] # RW
CCWANGLELIM_H = [0x09] # RW
MAXTEMP       = [0x0B] # RW (note 0x0A is reserved)
MINVOLTAGE    = [0x0C] # RW
MAXVOLTAGE    = [0x0D] # RW
MAXTORQUE_L   = [0x0E] # RW
MAXTORQUE_H   = [0x0F] # RW
STATUSRET     = [0x10] # RW
ALARMLED      = [0x11] # RW
ALARMSHUTDOWN = [0x12] # RW

# The exposed RAM addresses
TORQUEEN      = [0x18] # RW
LED           = [0x19] # RW
CWCOMPMARGIN  = [0x1A] # RW
CCWCOMPMARGIN = [0x1B] # RW
CWCOMPSLOPE   = [0x1C] # RW
CCWCOMPSLOPE  = [0x1D] # RW
GOALPOS_L     = [0x1E] # RW
GOALPOS_H     = [0x1F] # RW
MOVINGSPEED_L = [0x20] # RW
MOVINGSPEED_H = [0x21] # RW
TORQUELIM_L   = [0x22] # RW
TORQUELIM_H   = [0x23] # RW
POSITION_L    = [0x24] # R
POSITION_H    = [0x25] # R
SPEED_L       = [0x26] # R
SPEED_H       = [0x27] # R
LOAD_L        = [0x28] # R
LOAD_H        = [0x29] # R
VOLTAGE       = [0x2A] # R
TEMPERATURE   = [0x2B] # R
REGISTERED    = [0x2C] # R
MOVING        = [0x2E] # R (note 0x2D is reserved)
LOCK_EEPROM   = [0x2F] # RW
PUNCH_L       = [0x30] # RW
PUNCH_H       = [0x31] # RW

# The types of packets.
PING       = [0x01]
READ_DATA  = [0x02]
WRITE_DATA = [0x03]
REG_WRITE  = [0x04]
ACTION     = [0x05]
RESET      = [0x06]
SYNC_WRITE = [0x83]

# The various errors that might take place.
ERRORS = {64 : "Instruction",
          32 : "Overload",
          16 : "Checksum",
           8 : "Range",
           4 : "Overheating",
           2 : "AngleLimit",
           1 : "InputVoltage"}

def _Checksum(s):
  """Calculate the Dynamixel checksum (~(ID + length + ...)) & 0xFF."""
  return (~sum(s)) & 0xFF

def _VerifyID(id):
  """
  Just make sure the id is valid.
  """
  if not (0 <= id <= 0xFD):
    raise ValueError( "ID %d isn't legal!" % id)

def _EnWire(v):
  """
  Convert an int to the on-wire (little-endian) format. Actually returns the
  list [lsbyte, msbyte]. Of course, this is only useful for the 16-bit
  quantities we need to deal with.
  """
  if not 0 <= v <= 2047:
    raise ValueError( "EnWiring illegal value: %d" % v)
  return [v & 255, v >> 8]

def _DeWire(v):
  """
  Invert EnWire. v should be the list [lsbyte, msbyte].
  """
  return (v[1] << 8) + v[0]

class Response:
  """
  A response packet. Takes care of parsing the response, and figuring what (if
  any) errors have occurred. These will appear in the errors field, which is a
  list of strings, each of which is an element of ERRORS.values().
  """
  def __init__(self, data):
    """
    Data should be the result of a complete read from the serial port, as a
    list of ints. See ServoController.Interact().
    """
    if len(data) == 0 or data[0] != 0xFF or data[1] != 0xFF:
      
      raise ValueError("Is 12V on? -> Bad Header! ('%s')" % str(data))
    if _Checksum(data[2:-1]) != data[-1]:
      raise ValueError( "Checksum %s should be %s" % (_Checksum(data[2:-1]),
                                                      data[-1]))
    self.data = data
    self.id, self.length = data[2:4]
    self.errors = []
    for k in ERRORS.keys():
      if data[4] & k != 0:
        self.errors.append(ERRORS[k])
    # Lastly, the data we actually asked for, if any.
    self.parameters = self.data[5:-1]

  def __str__(self):
    return " ".join(map(hex, self.data))

  def Verify(self):
    """
    Ensure that nothing went wrong.
    """
    if len(self.errors) != 0:
      raise ValueError( "ERRORS: %s" % " ".join(self.errors))
    return self  # Syntactic sugar; lets us do return foo.Verify().

class ServoController:
  """
  Interface to a servo. Most of the real work happens in Interact(), which
  does a complete round of send-and-recv. The rest of the functions do what it
  sounds like they do. Note that this represents an entire _collection_ of
  servos, not just a single servo: therefore, each function takes a servo ID
  as its first argument, to specify the servo that should get the command.
  """

  wheelmode = False

  def __init__(self, portstring="/dev/ttyUSB0"):
    """
    Provide the name of the serial port to which the servos are connected.
    """
    self.portstring = portstring
    self.port = serial.Serial(self.portstring,
                              1000000,
                              timeout=5) # Picked from a hat.
  def Close(self):
    """Close the serial port."""
    self.port.close()

  def __del__(self):
    """
    All this needs to do is shut down, which you can also do by hand using
    Close().
    """
    self.Close()

  def Interact(self, id, packet):
    """
    Given an (assembled) payload, add the various extra bits, and transmit to
    servo at id. Returns the status packet as a Response. id must be in the
    range [0, 0xFD].

    Note that the payload should be a list of integers, suitable for passing
    to chr(). See the user manual, page 10, for what's going on here.

    This is the low-level communication function; you probably want one of the
    other functions that does specific things.
    """
    _VerifyID(id)
    P = [id, len(packet)+1] + packet
    command = b"".join(map(chr, [0xFF, 0xFF] + P + [_Checksum(P)]))
    self.port.write(command)
    self.port.flushOutput()
    time.sleep(0.005)

    # Handle the read.
    res = []
    while self.port.inWaiting() > 0:
      res.append(self.port.read())
    return Response(map(ord, res)).Verify()

  # From here on out, you're looking at functions that really do something to
  # the servo itself. You should look at the user manual for details on what
  # all of these mean, although most are self-explanatory.

  def Reset(self, id):
    """
    Perform a reset on the servo. Note that this will reset the ID to 1, which
    could be messy if you have many servos plugged in.
    """
    _VerifyID(id)
    self.Interact(id, RESET).Verify()

  def GetPosition(self, id):
    """
    Return the current position of the servo. See the user manual, page 16,
    for what the return value means.
    """
    _VerifyID(id)
    packet = READ_DATA + POSITION_L + [2]
    res = self.Interact(id, packet).Verify()
    if len(res.parameters) != 2:
      raise ValueError( "GetPosition didn't get two parameters!")
    return _DeWire(res.parameters)

  def GetVoltage(self, id):
    """
    Return the current position of the servo. See the user manual, page 16,
    for what the return value means.
    """
    _VerifyID(id)
    packet = READ_DATA + VOLTAGE + [1]
    res = self.Interact(id, packet).Verify()
    return res.parameters[0]
    
  def GetPositionDegrees(self, id):
    """
    If you'd rather work in degrees, use this one. Again, see the user manual,
    page 16, for details.
    """
    return self.GetPosition(id) * (300.0 / 1023.0)

  def SetPosition(self, id, position):
    """
    Set servo id to be at position position. See the user manual, page 16, for
    how this works. This just sends the set position packet; the servo won't
    necessarily go where you told it. You can use GetPosition to figure out
    where it actually went.
    """
    _VerifyID(id)
    if not (0 <= position <= 1023):
      raise ValueError( "Invalid position!")
    packet = WRITE_DATA + GOALPOS_L + _EnWire(position)
    self.Interact(id, packet).Verify()

  def SetPositionDegrees(self, id, deg):
    """
    Set the position in degrees, according to the diagram in the manual on
    page 16.
    """
    if not 0 <= deg <= 300:
      raise ValueError( "%d is not a valid angle!" % deg)
    self.SetPosition(id, int(1023.0/300 * deg))

  def SetComplianceMargin(self, id, margin):
    """
    Set both the CW and CCW compliance margins.
    """
    _VerifyID(id)
    if not 0 <= margin < 256:
      raise ValueError( "%d is not a valid margin!" % margin)
    packetcw  = WRITE_DATA + CWCOMPMARGIN + [int(margin)] # CW
    packetccw = WRITE_DATA + CCWCOMPMARGIN + [int(margin)] # CCW
    self.Interact(id, packetcw).Verify()
    self.Interact(id, packetccw).Verify()

  def GetComplianceMargin(self, id):
    """
    Return the compliance margins as (CW, CCW).
    """
    _VerifyID(id)
    packetcw  = READ_DATA + CWCOMPMARGIN + [1]
    packetccw = READ_DATA + CCWCOMPMARGIN + [1]
    Q = self.Interact(id, packetcw).Verify()
    if len(Q.parameters) != 1:
      raise ValueError( "CW Compliance Margin parameter count problem!")
    temp = Q.parameters[0]
    Q = self.Interact(id, packetccw).Verify()
    if len(Q.parameters) != 1:
      raise ValueError( "CCW Compliance Margin parameter count problem!")
    return (temp, Q.parameters[0])

  def SetCWAngleLimit(self, id, limit):
    """
    Set the clockwise (smaller) angle limit, in servo units.
    """
    _VerifyID(id)
    if not 0 <= limit <= 1023:
      raise ValueError( "%d is not a valid CW angle limit!" % limit)
    packet = WRITE_DATA + CWANGLELIM_L + _EnWire(limit)
    self.Interact(id, packet).Verify()

  def GetCWAngleLimit(self, id):
    _VerifyID(id)
    packet = READ_DATA + CWANGLELIM_L + [2]
    Q = self.Interact(id, packet).Verify()
    if len(Q.parameters) != 2:
      raise ValueError( "GetCWAngleLimit has the wrong return shape!")
    return _DeWire(Q.parameters)

  def SetCCWAngleLimit(self, id, limit):
    """
    Set the counterclockwise (larger) angle limit, in servo units.
    """
    _VerifyID(id)
    if not 0 <= limit <= 1023:
      raise ValueError( "%d is not a valid CCW angle limit!" % limit)
    packet = WRITE_DATA + CCWANGLELIM_L + _EnWire(limit)
    self.Interact(id, packet).Verify()

  def GetCCWAngleLimit(self, id):
    _VerifyID(id)
    packet = READ_DATA + CCWANGLELIM_L + [2]
    Q = self.Interact(id, packet).Verify()
    if len(Q.parameters) != 2:
      raise ValueError( "GetCCWAngleLimit has the wrong return shape!")
    return _DeWire(Q.parameters)

  def SetWheelMode(self, id, wheelmode):
    _VerifyID(id)
    self.wheelmode = wheelmode
    if (wheelmode):
        self.SetCWAngleLimit(id, 0)
        self.SetCCWAngleLimit(id, 0)

  def SetID(self, id, nid):
    """
    Change the ID of a servo. Note that this is persistent; you may also be
    interested in Reset().
    """
    _VerifyID(id)
    if not 0 <= nid <= 0xFD:
      raise ValueError( "%id is not a valid servo ID!" % nid)
    packet = WRITE_DATA + IDNUMBER + [nid]
    self.Interact(id, packet).Verify()

  def GetMovingSpeed(self, id):
    """
    Get the moving speed. 0 means "unlimited".
    """
    _VerifyID(id)
    packet = READ_DATA + MOVINGSPEED_L + [2]
    Q = self.Interact(id, packet).Verify()
    if len(Q.parameters) != 2:
      raise ValueError( "GetMovingSpeed has the wrong return shape!")
    return _DeWire(Q.parameters)

  def SetMovingSpeed(self, id, speed):
    """
    Set the moving speed. 0 means "unlimited", so the servo will move as fast
    as it can.
    """
    _VerifyID(id)
    if not self.wheelmode:
      if not 0 <= speed <= 1023:
        raise ValueError( "%d is not a valid moving speed!" % speed)
    else:
      if not 0 <= speed <= 2047:
        raise ValueError( "%d is not a valid movign speed!" % speed)
    packet = WRITE_DATA + MOVINGSPEED_L + _EnWire(speed)
    self.Interact(id, packet).Verify()

  def Moving(self, id):
    """
    Return True if the servo is currently moving, False otherwise.
    """
    _VerifyID(id)
    packet = READ_DATA + MOVING + [1]
    Q = self.Interact(id, packet).Verify()
    return Q.parameters[0] == 1
    
  def WaitUntilStopped(self, id):
    """
    Spinlock until the servo has stopped moving.
    """
    while self.Moving(id):
      pass

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return int(rightMin + (valueScaled * rightSpan))
    
ps = "/dev/ttyACM0"

def MoveMotor(id, direction, speed):
  
  internalSpeed = translate(speed, 0, 100, 0, 1023) + direction * 1024
  driver = ServoController(ps)
  driver.SetWheelMode(id,True)
  driver.SetMovingSpeed(id, internalSpeed)

def StopMotors():
  motorDriver.SetMovingSpeed(motorFL,0)
  motorDriver.SetMovingSpeed(motorFR,0)
  motorDriver.SetMovingSpeed(motorBL,0)
  motorDriver.SetMovingSpeed(motorBR,0)
  
def MoveMotors(speedL,speedR):
  
  if speedL >= 100:
    speedL = 99
  elif speedL <= -100:
    speedL = -99
  
  if speedR >= 100:
    speedR = 99
  elif speedR <= -100:
    speedR = -99
    
  directionFL = 0
  directionFR = 1
  directionBL = 0
  directionBR = 1
  
  if speedL < 0:
    directionFL = 1
    directionBL = 1
    
    speedL = speedL * -1
    
  if speedR < 0:
    directionFR = 0
    directionBR = 0
    
    speedR = speedR * -1
    
  motorFL = 2
  motorFR = 4
  motorBL = 1
  motorBR = 3
  
  motorDriver.SetMovingSpeed(motorFL, translate(speedL % 100, 0, 100, 0, 1023) + directionFL * 1024)
  motorDriver.SetMovingSpeed(motorFR, translate(speedR % 100, 0, 100, 0, 1023) + directionFR * 1024)
  motorDriver.SetMovingSpeed(motorBL, translate(speedL % 100, 0, 100, 0, 1023) + directionBL * 1024)
  motorDriver.SetMovingSpeed(motorBR, translate(speedR % 100, 0, 100, 0, 1023) + directionBR * 1024)


forwards = 1023
backwards = 2047

global motorDriver

global lastSpeedL
global lastSpeedR

motorDriver= ServoController(ps)

motorFL = 2
motorFR = 3
motorBL = 1
motorBR = 4

initialised = False
while not initialised:
  try:
    motorDriver.SetWheelMode(motorFL,True)
    motorDriver.SetWheelMode(motorBL,True)
    motorDriver.SetWheelMode(motorFR,True)
    motorDriver.SetWheelMode(motorBR,True)
    initialised = True
  except Exception as e:
    print(e)
    print("Failed to initialised, trying again")
    time.sleep(1)

print("Motors Ready!")
StopMotors()

print(motorDriver.GetVoltage(1))


def MessageHandle():

    while True:
        #  Wait for next request from client
        message = socket.recv().split(",")
        #message = message.split(",")
        try:
          MoveMotors(int(message[0]),int(message[1]))
        except Exception as e:
          print(e)
          print("Failed command, waiting for next one to come along")
        socket.send_string(b"True")


'''
10.9v = 111
11.0v = 113
11.9v = 123
12.0v = 123
12.4v = 124

'''
# Handy for interactive testing.
if __name__ == "__main__":
  
  MessageHandle()
  
  if len(sys.argv) != 1:  # Specifying a port for interactive use
    ps = sys.argv[1]
    
  else:
    ps = "/dev/ttyACM0"


  '''
  while True:

     
    MoveMotors(100,100)
    time.sleep(1)
    MoveMotors(-100,-100)
    time.sleep(1)
    
    '''
