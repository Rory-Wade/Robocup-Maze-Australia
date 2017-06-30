import time
import Adafruit_TCS34725

tcs = Adafruit_TCS34725.TCS34725(busnum=2,gain=Adafruit_TCS34725.TCS34725_GAIN_16X)

tcs.set_interrupt(False)

LOWER_BOUND_WHITE = 120
HIGHER_BOUND_BLACK = 20

print("Light Sensor Active")

def tileColour():
    r, g, b, c = tcs.get_raw_data()
    
    lux = Adafruit_TCS34725.calculate_lux(r, g, b)
        
    if(lux > LOWER_BOUND_WHITE):
        return None
    elif(lux < HIGHER_BOUND_BLACK):
        return 0 #black
    
    return 1 # else its silver
    
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

if __name__ == "__main__":
    
    # Read the R, G, B, C color data.
    r, g, b, c = tcs.get_raw_data()
    
    # Calculate color temperature using utility functions.  You might also want to
    # check out the colormath library for much more complete/accurate color functions.
    color_temp = Adafruit_TCS34725.calculate_color_temperature(r, g, b)
    
    # Calculate lux with another utility function.
    lux = Adafruit_TCS34725.calculate_lux(r, g, b)
    
    # Print out the values.
    print('Color: red={0} green={1} blue={2} clear={3}'.format(r, g, b, c))
    
    # Print out color temperature.
    if color_temp is None:
        print('Too dark to determine color temperature!')
    else:
        print('Color Temperature: {0} K'.format(color_temp))
    
    # Print out the lux.
    print('Luminosity: {0} lux'.format(lux))
    
    print(tileColour())
    # Enable interrupts and put the chip back to low power sleep/disabled.
    tcs.set_interrupt(True)
    tcs.disable()
