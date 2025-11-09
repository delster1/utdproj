"""Helpers for converting serial data into JSON payloads."""
from __future__ import annotations

import json
from typing import Dict, List

import requests
import serial


def serial_to_json(line: str) -> Dict[str, object]:
    """Convert a raw ``name:value`` line from the serial bus into JSON-ready data."""

    name, value = line.split(":", maxsplit=1)
    return {"sensor_name": name.strip(), "sensor_output": float(value.strip())}


def main() -> None:
    """Read from the serial port and forward each measurement to the Flask app."""

    ser = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
    endpoint = "http://localhost:5000/receive"

    while True:
        line = ser.readline().decode("utf-8").strip()
        if not line:
            continue
        try:
            reading = serial_to_json(line)
        except ValueError:
            print(f"Skipping invalid line: {line}")
            continue

        payload: List[Dict[str, object]] = [reading]
        print(json.dumps(payload))
        response = requests.post(endpoint, json=payload, timeout=5)
        if response.status_code != 200:
            print(f"Server returned {response.status_code}: {response.text}")


if __name__ == "__main__":
    main()
