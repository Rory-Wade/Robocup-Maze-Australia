# ALL 360 DEGREES
# import zmq
# from rplidar import RPLidar
# import json
# import time
# import math

# lidar = RPLidar('/dev/ttyUSB0')

# context = zmq.Context()
# socket = context.socket(zmq.PUB)
# socket.set_hwm(1)
# socket.bind("tcp://*:5556")

# print(lidar.get_info())
# print(lidar.get_health())

# lidarArrayValue = [0] * 360
# try:
#     lidarArray = [[0] * 360, [0] * 360]
#     scan_count = 0
#     for new, quality, angle, measurement in lidar.iter_measurments():
#         if quality > 0:
#             index = int(angle) % 360
#             lidarArray[1][index] = lidarArray[1][index] + 1
#             lidarArray[0][index] = round(lidarArray[0][index] + ((measurement - lidarArray[0][index]) / lidarArray[1][index]), 1)
#         if new:
#             scan_count = scan_count + 1
#             if scan_count >= 2:
#                 socket.send_string("%s %s" % ("[LIDAR]", json.dumps(lidarArray[0], ensure_ascii=True)))
#                 lidarArray = [[0] * 360, [0] * 360]
#                 scan_count = 0
#                 time.sleep(0.1)
# except Exception as e:
#     print(e)
#     print("Caught error, safely stopping lidar")
#     lidar.stop()

# EVERY 10 DEGREES ARE INTEGRATED
# import zmq
# from rplidar import RPLidar
# import json
# import time
# import math

# lidar = RPLidar('/dev/ttyUSB0')

# context = zmq.Context()
# socket = context.socket(zmq.PUB)
# socket.set_hwm(1)
# socket.bind("tcp://*:5556")

# print(lidar.get_info())
# print(lidar.get_health())

# try:
#     lidarArray = [[0] * 36, [0] * 36]
#     for i, scandata in enumerate(lidar.iter_scans()):
#         for scan in scandata:
#             quality, angle, measurement = scan
#             index = (int(angle) % 360) / 10
#             lidarArray[1][index] = lidarArray[1][index] + 1
#             lidarArray[0][index] = round(lidarArray[0][index] + ((measurement - lidarArray[0][index]) / lidarArray[1][index]), 0)
        
#         socket.send_string("%s %s" % ("[LIDAR]:", json.dumps(lidarArray[0], ensure_ascii=True)))
#         lidarArray = [[0] * 36, [0] * 36]
#         time.sleep(0.05)
# except Exception as e:
#     print(e)
#     print("Caught error, safely stopping lidar")
#     lidar.stop()
import zmq
from rplidar import RPLidar
import json
import time
import math

print("Start")

lidar = RPLidar('/dev/ttyUSB0')

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.set_hwm(1)
socket.bind("tcp://*:5556")

print(lidar.get_info())
print(lidar.get_health())

lidarArray = [0] * 36
inc = 360 / len(lidarArray) 
thresh = 2
try:
    for i, scandata in enumerate(lidar.iter_scans()):
        for scan in scandata:
            quality, angle, measurement = scan
            
            if quality > 1:
                if angle % inc <= thresh or 10 - (angle % 10 ) <= thresh:
                    
                    if angle >= 360 - thresh or angle <= thresh:
                        lidarArray[0] = int(measurement)
                        
                    elif (angle % inc) > inc / 2:
                        lidarArray[int(angle // 10) + 1] = int(measurement)

        socket.send_string("%s %s" % ("[LIDAR]:", json.dumps(lidarArray, ensure_ascii=True)))
        #lidarArray = [0] * 36
except Exception as e:
    print(e)
    print("Caught error, safely stopping lidar")
    lidar.stop()
