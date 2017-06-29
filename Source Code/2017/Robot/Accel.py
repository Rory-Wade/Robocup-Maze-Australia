# Simple Adafruit BNO055 sensor reading example.  Will print the orientation
# and calibration data every second.
#
# Copyright (c) 2015 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import logging
import sys
import time
from Adafruit_BNO055 import BNO055

BNO055_PWR_MODE_ADDR                 = 0X3E
POWER_MODE_NORMAL                    = 0X00
BNO055_SYS_TRIGGER_ADDR              = 0X3F

bno = BNO055.BNO055(rst='P9_27', busnum=2)

# Enable verbose debug logging if -v is passed as a parameter.
if len(sys.argv) == 2 and sys.argv[1].lower() == '-v':
    logging.basicConfig(level=logging.DEBUG)

# Initialize the BNO055 and stop if something went wrong.
if not bno.begin():
    raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')

# Print system status and self test result.
status, self_test, error = bno.get_system_status()

print('System status: {0}'.format(status))
print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
# Print out an error if system status is in error mode.
if status == 0x01:
    print('System error: {0}'.format(error))
    print('See datasheet section 4.3.59 for the meaning.')

#bno.set_calibration([222, 255, 223, 255, 3, 0, 80, 0, 48, 0, 0, 0, 0, 0, 0, 0, 0, 0, 232, 3, 192, 2])
#bno.set_mode(OPERATION_MODE_M4G)
# Print BNO055 software revision and other diagnostic data.
sw, bl, accel, mag, gyro = bno.get_revision()
print('Software version:   {0}'.format(sw))
print('Bootloader version: {0}'.format(bl))
print('Accelerometer ID:   0x{0:02X}'.format(accel))
print('Magnetometer ID:    0x{0:02X}'.format(mag))
print('Gyroscope ID:       0x{0:02X}\n'.format(gyro))

print('Reading BNO055 data, press Ctrl-C to quit...')

heading, roll, pitch = bno.read_euler()
sys, gyro, accel, mag = bno.get_calibration_status()

print('Heading={0:0.2F} Roll={1:0.2F} Pitch={2:0.2F}\tSys_cal={3} Gyro_cal={4} Accel_cal={5} Mag_cal={6}'.format(heading, roll, pitch, sys, gyro, accel, mag))

def getCurrentAngle():
    try:
        heading, roll, pitch = bno.read_euler()
        return heading
        
    except IndexError:
        print("\nBNO READ ERROR - PASSING NONE! ERROR-> {}".format(IndexError))
        return None

def resetIMU():
    bno._gpio.set_low(bno._rst)
    time.sleep(0.01)  # 10ms
    bno._gpio.set_high(bno._rst)
    time.sleep(0.65)
    bno._write_byte(BNO055_PWR_MODE_ADDR, POWER_MODE_NORMAL)
    # Default to internal oscillator.
    bno._write_byte(BNO055_SYS_TRIGGER_ADDR, 0x0)
    bno._operation_mode()


if __name__ == "__main__":
    while True:
        # Read the Euler angles for heading, roll, pitch (all in degrees).
        heading, roll, pitch = bno.read_euler()
        # Read the calibration status, 0=uncalibrated and 3=fully calibrated.
        sys, gyro, accel, mag = bno.get_calibration_status()
        # Print everything out.
        print('Heading={0:0.2F} Roll={1:0.2F} Pitch={2:0.2F}\tSys_cal={3} Gyro_cal={4} Accel_cal={5} Mag_cal={6}'.format(
              heading, roll, pitch, sys, gyro, accel, mag))
                    
        response = raw_input("Reset?")
        if response == "y":
            resetIMU()

        time.sleep(1)
        