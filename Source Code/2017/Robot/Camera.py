import time
import mraa

# Initialize UART
u=mraa.Uart(3)

# Set UART parameters
u.setBaudRate(115200)
u.setMode(8, mraa.UART_PARITY_NONE, 1)

print("Online")

while True:
    print(u.read(1))
