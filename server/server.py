"""Flask application that receives sensor readings and stores them in Redis."""
from __future__ import annotations

from flask import Flask, jsonify, request

from server.redis import SensorLogStore, reading_from_dict

app = Flask(__name__)
log_store = SensorLogStore()


@app.route("/")
def hp() -> str:
    return "<h1>hello world</h1>"


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
