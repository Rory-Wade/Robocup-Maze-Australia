import time
import Adafruit_TCS34725

tcs = Adafruit_TCS34725.TCS34725(busnum=2,gain=Adafruit_TCS34725.TCS34725_GAIN_16X)

tcs.set_interrupt(False)

LOWER_BOUND_WHITE = 97
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
Color: red=165 green=182 blue=163 clear=492
Color Temperature: 6843 K
Luminosity: 114 lux 109 lux 110 lux

SILVER
Color: red=152 green=141 blue=135 clear=387
Color Temperature: 6991 K
Luminosity: 74 lux 71 lux 80 lux


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
