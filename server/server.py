"""Flask application that receives sensor readings and stores them in Redis."""
from __future__ import annotations

import subprocess
from ml.rag_agent import main as start_rag_agent

from server.w2db import r

from flask import Flask, jsonify, request
import os

from server.redis2 import SensorLogStore, reading_from_dict, get_latest_sensor_data

from flask_cors import CORS
app = Flask(__name__)

CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:4321", "https://d3llie.tech"],
        "supports_credentials": True
    }
})

log_store = SensorLogStore()


@app.route("/")
def hp() -> str:
    return "<h1>hello world</h1>"

@app.route("/vibrate")
def vibrate() :

    return jsonify({"anomaly_detected" : f"{os.getenv("ANOMALY_STATUS")}"}) , 200

@app.route("/data")
def get_data():

    try:
        sensor_names = ["HeartRate", "Temp", "AccelX", "AccelY", "AccelZ"]
        data = {}

        for sensor_name in sensor_names:
            # Get last 6 values from Redis list
            raw_entries = r.lrange(sensor_name, 0, 5)
            # Decode and convert to float if possible
            values = []
            for e in raw_entries:
                try:
                    values.append(float(e.decode() if isinstance(e, bytes) else e))
                except:
                    continue
            data[sensor_name] = list(reversed(values))  # Chronological order

        return jsonify({"sensor_outputs": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/receive", methods=["POST"])
def process_json():
    """Parse a list of sensor readings and persist them in Redis."""

    try:
        responses = request.get_json()

        if not isinstance(responses, list):
            return jsonify({"error": "Expected a list of JSON objects"}), 400

        parsed_data = []
        readings = []
        for response in responses:
            sensor_name = response.get("sensor_name")
            sensor_output = response.get("sensor_output")
            if sensor_name is None or sensor_output is None:
                continue
            parsed_data.append({"sensor_name": sensor_name, "sensor_output": sensor_output})
            readings.append(reading_from_dict(response))

        if readings:
            log_store.bulk_push(readings)

        return jsonify({"status": "success", "data": parsed_data}), 200

    except Exception as exc:  # pragma: no cover - defensive fallback
        return jsonify({"error": f"Couldn't process request. Error: {str(exc)}"}), 400


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)
