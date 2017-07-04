import time
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.ADC as ADC


try:
    ADC.setup()
except Exception as e:
    print("ADC error:")
    print(e)
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
        time.sleep(1)
        
        #LightUp(1,0,1)
        #time.sleep(0.5)
        LightUp(1,1,1)
        time.sleep(1)
