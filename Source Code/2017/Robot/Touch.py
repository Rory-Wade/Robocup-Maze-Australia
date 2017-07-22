import time
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.ADC as ADC

initialised = False
while not initialised:
    try:
        ADC.setup()
        initialised = True
    except Exception as e:
        print("ADC error:")
        print(e)
        time.sleep(1)

PAUSE_BUTTON = "P9_25"
FAR_LEFT_TOUCH_SENSOR = "AIN0"
MID_LEFT_TOUCH_SENSOR = "AIN1"
FAR_RIGHT_TOUCH_SENSOR = "AIN2"
MID_RIGHT_TOUCH_SENSOR = "AIN3"

TOUCH_BUTTONS = [FAR_LEFT_TOUCH_SENSOR,MID_LEFT_TOUCH_SENSOR,MID_RIGHT_TOUCH_SENSOR,FAR_RIGHT_TOUCH_SENSOR]

GPIO.setup(PAUSE_BUTTON, GPIO.IN) 

def PauseButton():
    GPIO.setup(PAUSE_BUTTON, GPIO.IN) 
    state = bool(GPIO.input(PAUSE_BUTTON))
    
    if state:
        time.sleep(0.1)
        GPIO.setup(PAUSE_BUTTON, GPIO.OUT)
        GPIO.output("P8_41",GPIO.LOW)
        GPIO.setup(PAUSE_BUTTON, GPIO.IN) 
    
    return state
    
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
    elif (r == 0):
        GPIO.output("P8_41",GPIO.LOW)
    
    if (g == 1):
        GPIO.output("P8_39",GPIO.HIGH)
    elif (g == 0):
        GPIO.output("P8_39",GPIO.LOW)
        
    if (b == 1):
        GPIO.output("P8_43",GPIO.HIGH)
    elif (b == 0):
        GPIO.output("P8_43",GPIO.LOW)


    
if __name__ == "__main__":
    while True:
        
        print(TouchSensors())
        print(PauseButton())
        time.sleep(0.1)

