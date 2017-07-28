import time
import Adafruit_TCS34725

initialised = False
while not initialised:
    try:
        LightSensorRight = Adafruit_TCS34725.TCS34725(busnum=2,gain=Adafruit_TCS34725.TCS34725_GAIN_60X)
        LightSensorRight.set_interrupt(False)
        initialised = True
    except Exception as e:
        print(e)
        print("Re-Initialise right light sensors...")

print(">Left Light Sensor Status: Good")

initialised = False
while not initialised:
    try:
        LightSensorLeft = Adafruit_TCS34725.TCS34725(busnum=1,gain=Adafruit_TCS34725.TCS34725_GAIN_60X)
        LightSensorLeft.set_interrupt(False)
        initialised = True
    except Exception as e:
        print(e)
        print("Re-Initialise left light sensors...")
        
print(">Right Light Sensor Status: Good \n")        
LOWER_BOUND_WHITE = 245
HIGHER_BOUND_BLACK = 100



def tileColour():
    Rr, Rg, Rb, Rc = LightSensorRight.get_raw_data()
    
    Rightlux = Adafruit_TCS34725.calculate_lux(Rr, Rg, Rb)
    
    Lr, Lg, Lb, Lc = LightSensorLeft.get_raw_data()
    
    Leftlux = Adafruit_TCS34725.calculate_lux(Lr, Lg, Lb)
        
    if(Leftlux > LOWER_BOUND_WHITE and Rightlux > LOWER_BOUND_WHITE):
        return None
    elif(Leftlux < HIGHER_BOUND_BLACK or Rightlux < HIGHER_BOUND_BLACK):
        return 0 #black
    
    return 1 # else its silver

def valueColour():
    Rr, Rg, Rb, Rc = LightSensorRight.get_raw_data()
    
    Rightlux = Adafruit_TCS34725.calculate_lux(Rr, Rg, Rb)
    
    Lr, Lg, Lb, Lc = LightSensorLeft.get_raw_data()
    
    Leftlux = int(Adafruit_TCS34725.calculate_lux(Lr, Lg, Lb) * 1.3)
        
    return [Rightlux,Leftlux] # else its silver
    
'''
BLACK
Color: red=26 green=16 blue=15 clear=48
Color Temperature: 2838 K
Luminosity: 5 lux 6 lux

WHITE
Light Sensor Active
Color: red=172 green=205 blue=185 clear=563
Color Temperature: 7406 K
Luminosity: 132 lux
None

SILVER
Color: red=169 green=173 blue=158 clear=490
Color Temperature: 6740 K
Luminosity: 102 lux
1


'''
#white
'''
[349, 367]
[346, 374]
[352, 321]
[325, 354]
[343, 387]
[342, 364]
[351, 366]
[328, 344]
[345, 352]
[342, 401]
[366, 374]
'''
#silver
'''[167, 165]
[166, 162]
[192, 156]
[176, 170]
[193, 175]
[159, 161]
[177, 161]
[170, 158]
'''
if __name__ == "__main__":
    while True:
        
        print(valueColour())
        time.sleep(1)