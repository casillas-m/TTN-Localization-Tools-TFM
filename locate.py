#Mockup data for testing
from secrets_folder.parsed_data_recorrido import parsed_data_stored
mock_msg_count_test = 0

from secrets_folder.secrets_file import ttn_apikey, WEB_APP_URL, TTN_URL
from maps.disca_map import rss_map, RSS_NULL
from maps.disca_coordinates import disca_coord
import time
import ttn_data
import requests

def least_squares_classification(rss_map, RSS_NULL, available_gateways, new_data):
    new_data_gateways = list(new_data.keys())
    categories = list(rss_map.keys())
    scores = {}
    
    #Completar rss_map con gateways faltantes
    for category in rss_map.keys():
        category_gateways = rss_map[category].keys()
        for gateway in available_gateways:
            if gateway not in category_gateways:
                rss_map[category][gateway] = {}
                for ch in range(8):
                    rss_map[category][gateway][ch] = RSS_NULL
                
    # Completar new_data con valores RSS nulos
    for missing_gateway in available_gateways:
        if missing_gateway not in new_data_gateways:
            new_data[missing_gateway]={}
            existing_channels = list(new_data[new_data_gateways[0]].keys())
            for existing_channel in existing_channels:
                new_data[missing_gateway][existing_channel] = RSS_NULL
        
    
    gateways = list(new_data.keys())
    
    for category in categories:
        squared_errors = []
        for gateway in gateways:
            gateway_rss = rss_map[category][gateway]
            new_data_rss = new_data[gateway]
            for channel in new_data_rss.keys():
                if channel in gateway_rss:
                    squared_error = (new_data_rss[channel] - gateway_rss[channel])**2
                    squared_errors.append(squared_error)
        
        # Suma de errores cuadráticos
        total_squared_error = sum(squared_errors)
        scores[category] = total_squared_error
    
    # Encontrar la categoría con el menor error cuadrático
    best_category = min(scores, key=scores.get)
    return best_category, scores

def get_current_location(rss_map, RSS_NULL, available_gateways, msg_qty, connection):
    json_data = []
    #Mockup or Real data select
    global mock_msg_count_test
    if mock_msg_count_test == 0:
        #Real
        json_data = ttn_data.get_last_n_messages(connection["url"], connection["headers"], msg_qty)
    else:
        json_data = True
    if json_data:
        latests_messages = []
        if mock_msg_count_test == 0:
            latests_messages = ttn_data.parse_json_data(json_data)
        else:
            #Movement simulation for testing (mockup data) 
            latests_messages = parsed_data_stored[-(msg_qty + mock_msg_count_test):-mock_msg_count_test]
            if mock_msg_count_test%5 == 0:
                print(latests_messages[-1]["received_at"])
            mock_msg_count_test += 1
        gps_location = {}
        for message in latests_messages:
            if "gps_3" in message["decoded_payload"].keys():
                gps_location = message["decoded_payload"]["gps_3"]
        if gps_location:
            return gps_location
        else:
            new_data = {}
            for message in latests_messages:
                channel = message["channel"] 
                for gateway in message["rx_metadata"]:
                    gateway_id = gateway["gateway_id"]
                    rssi = gateway["rssi"]
                    if gateway_id not in new_data:
                        new_data[gateway_id] = {}
                    if channel in new_data[gateway_id]:
                        new_data[gateway_id][channel] = (rssi + new_data[gateway_id][channel])/2
                    else:
                        new_data[gateway_id][channel] = rssi
            classification, error_scores = least_squares_classification(rss_map, RSS_NULL, available_gateways, new_data)
            #print(error_scores)
            return classification
        
def send_to_web(location):
    #Check if location is a GPS coord.
    if isinstance(location, dict):
        response = requests.post(WEB_APP_URL + '/set_point', json=location)
    else:
        response = requests.post(WEB_APP_URL + '/set_point', json=disca_coord[location])
    print(response.json())

def main():
    connection = {
        "url": TTN_URL,
        "headers": {
            "Authorization": "Bearer " + ttn_apikey
        }
    }
    available_gateways = ["rak7248-grc-pm65","main-gtw-grc","itaca-upv-022"]
    new_data = { #0e
        "main-gtw-grc": {0: -96.66666666666667, 1: -95.0, 2: -96.25, 3: -99.0, 4: -98.25, 5: -97.0, 6: -98.4, 7: -97.66666666666667}
    }
    classification, error_scores = least_squares_classification(rss_map, RSS_NULL, available_gateways, new_data)
    print(f"El nuevo dato pertenece a la categoría: '{classification}' con los siguientes puntajes de error: {error_scores}")
    
    print("Locate tool")
    print("Type 'R' to use real data")
    print("Type 'M' to use mockup data (for testing)")
    command = input("Command: ").strip().lower()
    global mock_msg_count_test
    if command == 'r':
        mock_msg_count_test = 0
    elif command == 'm':
        mock_msg_count_test = 1
    else:
        print("Unknown command. Exit.")
        return
    print("Current location:")
    while True:
        #current_location7 = get_current_location(rss_map, RSS_NULL, available_gateways, 7, connection)
        current_location5 = get_current_location(rss_map, RSS_NULL, available_gateways, 5, connection)
        #current_location3 = get_current_location(rss_map, RSS_NULL, available_gateways, 3, connection)
        #current_location2 = get_current_location(rss_map, RSS_NULL, available_gateways, 2, connection)
        #current_location1 = get_current_location(rss_map, RSS_NULL, available_gateways, 1, connection)
        #print("7:",current_location7, "5:",current_location5, "3:",current_location3, "2:",current_location2, "1:",current_location1)
        print("5:",current_location5)
        send_to_web(current_location5)
        time.sleep(5)
        

if __name__ == "__main__":
    main()
