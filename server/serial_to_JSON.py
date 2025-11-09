import serial
import json 
import requests

def serial_to_JSON(data):
    try:
        name, value = data.split(":")
        new_data ={name.strip():str(float(value.strip()))}
        json_str = json.dumps(new_data)
        print(json_str)
        return json_str
    except ValueError:
        print(f"Skipping invalid line: {data}")



def main() -> None:
    """Read from the serial port and forward each measurement to the Flask app."""

    ser = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
    while True:
        line = ser.readline().decode("utf-8").strip()
        if not line:
            continue
        else:
            jsonline = serial_to_JSON(line)
        requests.post("http://utd.d3llie.tech/recieve", json=jsonline)
main()
