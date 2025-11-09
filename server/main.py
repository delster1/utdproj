from serial_to_JSON import serial_to_JSON
from w2db import write2redis
from vibrate import start_vibes, ping_server
import serial
import time
import requests

def main():
    '''RUN AND READ HERE'''
    ser = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
    while True:
        line = ser.readline().decode("utf-8").strip()
        if not line:
            continue
        else:
            jsonline = serial_to_JSON(line)
        if jsonline:
            write2redis(jsonline)
            
        ser = serial.Serial("/dev/ttyACM1", 11520, timeout=1)
        time.sleep(2)
        
        server_comf = ping_server("http://vibrator.d3llie.tech/vibrate")
        if server_comf:
            print("YAYYY IT WORKED")
            start_vibes(ser)
            time.sleep(2)
        else:
            print("It fr fr worked")
            pass
main()

