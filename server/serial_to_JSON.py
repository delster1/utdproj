import serial
import json 
import requests

def serial_to_JSON(data):
    try:
        name, value = data.split(":")
        new_data =
            {name.strip():str(float(value.strip()))}
        json_str = json.dumps(new_data)
        print(json_str)
        return json_str
    except ValueError:
        print(f"Skipping invalid line: {data}")
        return NULL
