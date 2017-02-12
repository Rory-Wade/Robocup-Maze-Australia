'''Records measurments to a pipe. Usage example:'''

import sys
from rplidar import RPLidar

PORT_NAME = '/dev/tty.SLAB_USBtoUART'

def readLidar():
	'''Main function'''
	lidar = RPLidar(PORT_NAME)

	try:
		print('Recording measurments... Press Crl+C to stop.')

		for measurment in lidar.iter_measurments():
			newScan = measurment[0]
			quality = measurment[1]
			angle = measurment[2]
			distance = measurment[3]

			print("New:{}   Quality:{}   Angle:{}   Distance:{}".format(newScan, quality, angle, distance))

	except KeyboardInterrupt:
		lidar.stop_motor()
		lidar.stop()
		lidar.disconnect()
		print('Stoping.')

		

if __name__ == '__main__':
	readLidar()

def exampleClass(object):
	def publicFunction(var1, var2):
		self._privateFunction(var2)

	def _privateFunction(var):
		print(var)

	internalPublicVarList = []

	_internalPrivateVarList = np.array()

	internalPublicString = "hello!"

	_internalPrivateString = "private!"

	

