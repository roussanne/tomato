"""Arduino 직렬 통신으로 로봇 팔의 X/Y/Z 좌표를 전송하는 스크립트."""

import serial
import time


arduino_port = "/dev/ttyACM0"
baud_rate = 9600

arduino_serial = serial.Serial(arduino_port, baud_rate, timeout=1)

try:
    while True:
        x_value = input("Enter X, Y, Z values (e.g., 100,200,300): ")
        arduino_serial.write(x_value.encode() + b'\n')

        time.sleep(0.1)
except KeyboardInterrupt:
    arduino_serial.close()
    print("Serial port closed.")
