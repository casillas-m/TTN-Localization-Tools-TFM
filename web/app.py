from flask import Flask, render_template, request, jsonify
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