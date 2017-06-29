'''
import time
import mraa

def BrightRead(port):
    air = mraa.Aio(port)
    airValue = air.read()
    return airValue

def PauseButton():
    relay = mraa.Gpio(62) # GPIO_51
    relay.dir(mraa.DIR_IN)
    return bool(relay.read())

def TouchRight(port):
    relay = mraa.Gpio(port) # GPIO_51
    relay.dir(mraa.DIR_IN)
    value = relay.read()
    relay.dir(mraa.DIR_OUT)
    relay.write(0)
    return bool(value)
    
def TouchLeft(port):
    air = mraa.Aio(port)
    airValue = air.read()
    
    if airValue < 400:
        airValue = 0
        
    return bool(airValue)
    
def TouchSensors():
    return [bool(TouchLeft(4)),bool(TouchRight(71)),bool(TouchRight(73)),bool(TouchLeft(3))]
    
if __name__ == "__main__":
    while True:
        
        print(chr(27) + "[2J")
        print("Pause Button: %i"%(PauseButton()))
        #print("Light Sensor Right: %i Light Sensor Left: %i"%(BrightRead(1),BrightRead(2)))
        #print("Touch Sensor F Right: %i Touch Sensor F Left: %i Touch Sensor B Left: %i Touch Sensor B Right: %i"%(TouchSensors()[0],TouchSensors()[1],TouchSensors()[2],TouchSensors()[3]))
        
        time.sleep(1)
'''
import time
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.ADC as ADC

ADC.setup()

PAUSE_BUTTON = "P9_16"
LEFT_FRONT_TOUCH_SENSOR = "AIN1"
RIGHT_FRONT_TOUCH_SENSOR = "AIN3"
LEFT_BACK_TOUCH_SENSOR = "AIN0"
RIGHT_BACK_TOUCH_SENSOR = "AIN2"

TOUCH_BUTTONS = [LEFT_FRONT_TOUCH_SENSOR,RIGHT_FRONT_TOUCH_SENSOR,LEFT_BACK_TOUCH_SENSOR,RIGHT_BACK_TOUCH_SENSOR]

GPIO.setup(PAUSE_BUTTON, GPIO.IN) 

def PauseButton():
    return bool(GPIO.input(PAUSE_BUTTON))
    
def TouchSensors():
    values = []
    for i in TOUCH_BUTTONS:
        values.append(ReadSingleTouch(i))
    return values
    
def ReadSingleTouch(port):
    value = ADC.read_raw(port)
    if value < 1500:
        value = 0
    return bool(value)
    
    

GPIO.setup("P8_39", GPIO.OUT)
GPIO.setup("P8_41", GPIO.OUT)
GPIO.setup("P8_43", GPIO.OUT)
    
def LightUp(r,g,b):
    if (r == 1):
        GPIO.output("P8_41",GPIO.HIGH)
        print("RED ON")
        time.sleep(1)
    elif (r == 0):
        GPIO.output("P8_41",GPIO.LOW)
    
    if (g == 1):
        GPIO.output("P8_39",GPIO.HIGH)
        print("GREEN ON")
        time.sleep(1)
    elif (g == 0):
        GPIO.output("P8_39",GPIO.LOW)
        
    if (b == 1):
        GPIO.output("P8_43",GPIO.HIGH)
        print("BLUE ON")
        time.sleep(1)
    elif (b == 0):
        GPIO.output("P8_43",GPIO.LOW)


    
if __name__ == "__main__":
    while True:
        
        print(TouchSensors())
        print(PauseButton())
        time.sleep(1)
        
        #LightUp(1,0,1)
        #time.sleep(0.5)
        LightUp(1,1,1)
        time.sleep(1)
        
        #LightUp(0,0,0)
        #time.sleep(1)
        #LightUp(1,1,0)
        #time.sleep(0.5)
        #LightUp(0,1,1)
        #time.sleep(1)
        #LightUp(0,0,0)
        #time.sleep(1)
        #LightUp(0,1,1)
        #time.sleep(0.5)
        #LightUp(1,1,0)
        #time.sleep(1)
        #LightUp(0,0,0)
        #time.sleep(1)