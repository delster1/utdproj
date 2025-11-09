import serial
import json 


def serial_to_JSON(data):
    try:
        name, value = data.split(":")
        new_data = { "Responses" : [
            {"Sensor:" : name.strip(),
            "Value:" : float(value.strip())}
        ]
        }
        json_str = json.dumps(new_data)
        print(json_str)
    except ValueError:
        print(f"Skipping invalid line: {data}")


def main():
    '''RUN AND READ HERE'''
    ser = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
    while True:
        line = ser.readline().decode("utf-8").strip()
        if not line:
            continue
        else:
            serial_to_JSON(line)
main()