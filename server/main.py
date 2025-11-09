from serial_to_JSON import serial_to_JSON
from w2db import write2redis
import serial

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
main()

