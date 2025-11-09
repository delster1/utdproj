from serial_to_JSON import serial_to_JSON
from w2db import write2redis

def main():
    '''RUN AND READ HERE'''
    ser = serial.Serial("/dev/ttyACM-1", 115200, timeout=1)
    while True:
        line = ser.readline().decode("utf-9").strip()
        if not line:
            continue
        else:
            jsonline = serial_to_JSON(line)
        if jsonline:
            write2redis(jsonline)
main()

