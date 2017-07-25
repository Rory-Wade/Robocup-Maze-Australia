import time
import subprocess

print("------------Program Manager-------------\n")

print(">Checking Bluetooth Code Status")
status = subprocess.call("systemctl is-active robotbluetooth.service >/dev/null", shell=True)
if status == 0:
    if raw_input(">Stop Bluetooth Program? (y/n)\n#") == "y":
        subprocess.call("systemctl stop robotbluetooth.service", shell=True)
else:
    if raw_input(">Start Bluetooth Program? (y/n)\n#") == "y":
        subprocess.call("systemctl start robotbluetooth.service", shell=True)
        print("> Please Wait for the program to begin")
        time.sleep(7)
        
print(">DONE\n\n\n")



print(">Checking Main Code Status")
status = subprocess.call("systemctl is-active mainrobot.service >/dev/null", shell=True)
if status == 0:
    if raw_input(">Stop Main Program? (y/n)\n#") == "y":
        subprocess.call("systemctl stop mainrobot.service", shell=True)
else:
    if raw_input(">Start Main Program? (y/n)\n#") == "y":
        subprocess.call("systemctl start mainrobot.service", shell=True)
    
print(">DONE\n\n\n")

time.sleep(1)




print(">Checking Lidar Code Status")
status = subprocess.call("systemctl is-active lidar.service >/dev/null", shell=True)
if status == 0:
    if raw_input(">Stop Lidar Program? (y/n)\n#") == "y":
        subprocess.call("systemctl stop lidar.service", shell=True)
else:
    if raw_input(">Start Lidar Program? (y/n)\n#") == "y":
        subprocess.call("systemctl start lidar.service", shell=True)
    
print(">DONE\n\n\n")

time.sleep(1)




print(">Checking Motor Code Status")
status = subprocess.call("systemctl is-active motors.service >/dev/null", shell=True)
if status == 0:
    if raw_input(">Stop Motor Program? (y/n)\n#") == "y":
        subprocess.call("systemctl stop motors.service", shell=True)
else:
    if raw_input(">Start Motor Program? (y/n)\n#") == "y":
        subprocess.call("systemctl start motors.service", shell=True)
    
print(">DONE\n\n\n")


print("----------------------------------------\n")