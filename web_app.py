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
    return render_template('map.html')

@app.route('/set_point', methods=['POST'])
def set_point():
    data = request.get_json()
    locations = [data]
    map_update(locations)
    return jsonify({'status': 'success'})

@app.route('/gps_status', methods=['GET'])
def gps_status():
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