from flask import Flask, request, jsonify
import json

app = Flask(__name__)  

@app.route('/')
def hp():
    return '<h1>hello world</h1>'

@app.route('/receive', methods=['POST'])  
def process_json():
    try:
        responses = request.get_json()

        if not isinstance(responses, list):
            return jsonify({'error': 'Expected a list of JSON objects'}), 400

        parsed_data = []
        for response in responses:
            sensor_name = response.get('sensor_name')
            sensor_output = response.get('sensor_output')
            parsed_data.append({'sensor_name': sensor_name, 'sensor_output': sensor_output})

        return jsonify({'status': 'success', 'data': parsed_data}), 200

    except Exception as e:
        return jsonify({'error': f"Couldn't process request. Error: {str(e)}"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

