from flask import Flask, render_template, request, jsonify
from secrets_folder.secrets_file import ttn_apikey, TTN_URL, DOWNLINK_DEV1_URL, DOWNLINK_DEV2_URL
import ttn_data
import requests
import json
import folium
import os

app = Flask(__name__)
locations = []

@app.route('/')
def index():
    """
    Render the main page with the map.
    This function handles the root URL and renders the 'map.html' template.
    """
    return render_template('map.html')

@app.route('/set_point', methods=['POST'])
def set_point():
    """
    Set a new point on the map based on the received JSON data.
    This function receives JSON data via POST request, updates the locations list, and calls map_update to refresh the map.
    """
    data = request.get_json()
    locations = [data]
    map_update(locations)
    return jsonify({'status': 'success'})

@app.route('/gps_status', methods=['GET'])
def gps_status():
    """
    Get the current GPS status of the device.
    This function retrieves the last message from the TTN data source and extracts the 'digital_in_4' status to determine if the device is interior or exterior.
    """
    connection = {
        "url": TTN_URL,
        "headers": {
            "Authorization": "Bearer " + ttn_apikey
        }
    }
    json_data = ttn_data.get_last_n_messages(connection["url"], connection["headers"], 1)
    last_messages = ttn_data.parse_json_data(json_data)
    dev_interior = 1
    if len(last_messages) > 0:    
        last_message = last_messages[0]
        dev_interior = last_message["decoded_payload"]["digital_in_4"] #1 Interior, 0 Exterior
    return jsonify({'dev_interior': dev_interior})

@app.route('/gps_enable', methods=['GET'])
def gps_enable():
    """
    Send a command to enable GPS on the device.
    This function sends a downlink message to enable GPS on two devices.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + ttn_apikey
    }
    payload = json.dumps({
        "downlinks": [
            {
            "frm_payload": "RQ==",
            "f_port": 1,
            "priority": "NORMAL"
            }
        ]
    })
    requests.request("POST", DOWNLINK_DEV1_URL, headers=headers, data=payload)
    requests.request("POST", DOWNLINK_DEV2_URL, headers=headers, data=payload)
    return jsonify({'status': 'GPS_ENABLE_SEND'})

@app.route('/gps_disable', methods=['GET'])
def gps_disable():
    """
    Send a command to disable GPS on the device.
    This function sends a downlink message to disable GPS on two devices.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + ttn_apikey
    }
    payload = json.dumps({
        "downlinks": [
            {
            "frm_payload": "SQ==",
            "f_port": 1,
            "priority": "NORMAL"
            }
        ]
    })
    requests.request("POST", DOWNLINK_DEV1_URL, headers=headers, data=payload)
    requests.request("POST", DOWNLINK_DEV2_URL, headers=headers, data=payload)
    return jsonify({'status': 'GPS_ENABLE_SEND'})

def map_update(locations):
    """
    Update the map with new locations.
    This function creates a Folium map with markers for each location and saves it as 'mapa.html' in the 'static' directory.
    """
    if locations:
        map = folium.Map(location=[locations[0]['latitude'], locations[0]['longitude']], zoom_start=18)

        for location in locations:
            folium.Marker(
                location=[location['latitude'], location['longitude']]
            ).add_to(map)
        map.save(os.path.join('static', 'mapa.html'))

map_update(locations)

if __name__ == '__main__':
    app.run(debug=True)