import requests

nuevo_punto = {
    'latitude': 39.4827,
    'longitude': -0.3471
}
response = requests.post('http://127.0.0.1:5000/set_point', json=nuevo_punto)
print(response.json())