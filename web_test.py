import requests

# Define a new point with latitude and longitude
new_location = {
    'latitude': 39.4827,
    'longitude': -0.3471
}
# Send a POST request to the local Flask server to set the new point on the map
response = requests.post('http://127.0.0.1:5000/set_point', json=new_location)
# Print the response from the server
print(response.json())