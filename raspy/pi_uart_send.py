import serial
import time

ser = serial.Serial(
    port='/dev/serial0',
    baudrate=115200,
    timeout=1
)

time.sleep(2)

while True:
    ser.write(b'Hello from Raspberry Pi!\n')
    print("msg sent")
    time.sleep(2)

