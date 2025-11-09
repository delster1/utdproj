import serial 
import time
import requests


def start_vibes(ser):
    ser.write(b"START\n")
    print("ITS GOING")


def ping_server(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        value = data["anomaly_detected"]
        print(value)
        value = int(value)
        value = bool(value)
        print(value)
        return value
    else:
        raise RuntimeError("talking to the server issues")


