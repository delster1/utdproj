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



def main():
    ser = serial.Serial("/dev/ttyACM1", 11520, timeout=1)
    time.sleep(2)
    
    while True:
        server_comf = ping_server("http://vibrator.d3llie.tech/vibrate")
        if server_comf:
            print("YAYYY IT WORKED")
            start_vibes(ser)
            time.sleep(2)
        else:
            print("It fr fr worked")
            pass

main()
