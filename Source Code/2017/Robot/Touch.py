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