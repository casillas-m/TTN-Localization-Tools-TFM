#Mockup data for testing
from secrets_folder.parsed_data_recorrido import parsed_data_stored
mock_msg_count_test = 0

from secrets_folder.secrets_file import ttn_apikey, WEB_APP_URL, TTN_URL, DOWNLINK_DEV1_URL, DOWNLINK_DEV2_URL
from maps.disca_map import rss_map, RSS_NULL
from maps.disca_coordinates import disca_coord
import time
import ttn_data
import requests
import json

def least_squares_classification(rss_map, RSS_NULL, available_gateways, new_data, tx_channels_used):
    """
    Classify the new data (location) into the best matching category based on RSS values using least squares method.
    Inputs:
    - rss_map: Dictionary containing RSS values for each category and gateway.
    - RSS_NULL: Default RSS value for missing data.
    - available_gateways: List of gateways available for the classification.
    - new_data: Dictionary of new RSS data to be classified.
    - tx_channels_used: Bitmask indicating which transmission channels are been used.
    Outputs:
    - Returns the best matching category and the associated error scores.
    """
    new_data_gateways = list(new_data.keys())
    categories = list(rss_map.keys())
    scores = {}
    # Complete rss_map filling the missing gateways
    for category in rss_map.keys():
        category_gateways = rss_map[category].keys()
        for gateway in available_gateways:
            if gateway not in category_gateways:
                rss_map[category][gateway] = {}
                for ch in range(8):
                    rss_map[category][gateway][ch] = RSS_NULL  
    # Complete new_data with RSS_NULL values (for gateways just added)
    for missing_gateway in available_gateways:
        if missing_gateway not in new_data_gateways:
            new_data[missing_gateway]={}
            existing_channels = list(new_data[new_data_gateways[0]].keys())
            for existing_channel in existing_channels:
                new_data[missing_gateway][existing_channel] = RSS_NULL
    # Complete new_data with RSS_NULL values (knowing previously used channels)
    # Get binary list of used TX channels, 1 = Used
    tx_channels_used_arr = [(tx_channels_used>>k)&1 for k in range(0,8)]
    for tx_channel, tx_channel_flag in enumerate(tx_channels_used_arr):
        if tx_channel_flag:
            for gateway in available_gateways:
                if tx_channel not in new_data[gateway].keys():
                    new_data[gateway][tx_channel] = RSS_NULL       
    gateways = list(new_data.keys())
    # Get all squared errors
    for category in categories:
        squared_errors = []
        for gateway in gateways:
            gateway_rss = rss_map[category][gateway]
            new_data_rss = new_data[gateway]
            for channel in new_data_rss.keys():
                if channel in gateway_rss:
                    squared_error = (new_data_rss[channel] - gateway_rss[channel])**2
                    squared_errors.append(squared_error)
        # Addition of squared errors
        total_squared_error = sum(squared_errors)
        scores[category] = total_squared_error
    # Find the best category (less error)
    best_category = min(scores, key=scores.get)
    return best_category, scores

def get_current_location(rss_map, RSS_NULL, available_gateways, msg_qty, connection, consider_tx_channels):
    """
    Get the current location based on the latest RSS data.
    Inputs:
    - rss_map: Dictionary containing RSS values for each category and gateway.
    - RSS_NULL: Default RSS value for missing data.
    - available_gateways: List of gateways available for the classification.
    - msg_qty: Number of messages to fetch for the current location determination.
    - connection: Dictionary containing the TTN URL and headers for authentication.
    - consider_tx_channels: Boolean indicating whether to consider previous TX channels.
    Outputs:
    - Returns the classified location and the associated error scores.
    """
    json_data = []
    # Mockup or Real data select
    global mock_msg_count_test
    if mock_msg_count_test == 0:
        # Real data (get messages)
        json_data = ttn_data.get_last_n_messages(connection["url"], connection["headers"], msg_qty)
    else:
        # Mockup data
        json_data = True
    if json_data:
        latests_messages = []
        if mock_msg_count_test == 0:
            # Real data (parse data)
            latests_messages = ttn_data.parse_json_data(json_data)
        else:
            # Movement simulation for testing (mockup data) 
            latests_messages = parsed_data_stored[-(msg_qty + mock_msg_count_test):-mock_msg_count_test]
            if mock_msg_count_test%5 == 0:
                print(latests_messages[-1]["received_at"])
            mock_msg_count_test += 1
        # Check and get GPS coord. if available
        gps_location = {}
        for message in latests_messages:
            if "gps_3" in message["decoded_payload"].keys():
                gps_location = message["decoded_payload"]["gps_3"]
                return gps_location, {}
        new_data = {}
        # Get tx_channels_used from most recent message
        tx_channels_used = 0
        if len(latests_messages)>0:
            tx_channels_used = latests_messages[0]["decoded_payload"].get("digital_in_5",0)
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
        # Classify new_data
        if consider_tx_channels:
            classification, error_scores = least_squares_classification(rss_map, RSS_NULL, available_gateways, new_data, tx_channels_used)
            #print(error_scores)
        else:
            classification, error_scores = least_squares_classification(rss_map, RSS_NULL, available_gateways, new_data, 0)
            #print(error_scores)
        return classification, error_scores
        
def send_to_web(location):
    """
    Send the classified location data to the web application.
    Inputs:
    - location: The classified location, either as GPS coordinates or a location name.
    """
    #Check if location is a GPS coord.
    try:
        if isinstance(location, dict):
            response = requests.post(WEB_APP_URL + '/set_point', json=location)
        else:
            response = requests.post(WEB_APP_URL + '/set_point', json=disca_coord[location])
        #print(response.json())
    except requests.exceptions.RequestException as e:
        print("Web app error.")

def check_interior_exterior(connection, location, error_scores):
    """
    Check if the location is interior or exterior and adjust device settings accordingly.
    Inputs:
    - connection: Dictionary containing the TTN URL and headers for authentication.
    - location: The classified location.
    - error_scores: Dictionary of error scores for the classification.
    """
    #If location is str means no GPS (interior or exterior but gps not ready)
    if isinstance(location, str):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + ttn_apikey
        }
        json_data = ttn_data.get_last_n_messages(connection["url"], connection["headers"], 1)
        last_messages = ttn_data.parse_json_data(json_data)
        if len(last_messages) > 0:    
            last_message = last_messages[0]
            dev_interior = last_message["decoded_payload"]["digital_in_4"] #1 Interior, 0 Exterior
            
            # If error is more that 300 assume that location is exterior
            if ((dev_interior == 1) and (error_scores[location] > 300)):
                #GPS Wakeup
                print("Exterior")
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
            elif (dev_interior == 0):
                #GPS Sleep
                print("Interior")
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
                time.sleep(10)

def main():
    """
    Main function to run the location determination and accuracy measurement tool.
    This function allows the user to choose between using real or mockup data, measures accuracy, and continuously determines the current location.
    """
    connection = {
        "url": TTN_URL,
        "headers": {
            "Authorization": "Bearer " + ttn_apikey
        }
    }
    available_gateways = ["rak7248-grc-pm65","main-gtw-grc","itaca-upv-022"]
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
    
    print("Measure accuracy? (Y/N)")
    command = input("Command: ").strip().lower()
    if command == 'y':
        measure_accuracy_flag = True
        place_name = input("Enter place name: ").strip().lower()
    elif command == 'n':
        measure_accuracy_flag = False
    else:
        print("Unknown command. Exit.")
        return
    
    if measure_accuracy_flag:
        print("Measuring accuracy for :", place_name)
        cl_10_correct_count = 0
        cl_5_correct_count = 0
        cl_10_tx_correct_count = 0
        cl_5_tx_correct_count = 0
        for _ in range(36):
            cl_10, error_scores = get_current_location(rss_map, RSS_NULL, available_gateways, 10, connection, False)
            cl_5, error_scores = get_current_location(rss_map, RSS_NULL, available_gateways, 5, connection, False)
            cl_10_tx, error_scores = get_current_location(rss_map, RSS_NULL, available_gateways, 10, connection, True)
            cl_5_tx, error_scores = get_current_location(rss_map, RSS_NULL, available_gateways, 5, connection, True)
            
            if place_name == cl_10: cl_10_correct_count += 1
            if place_name == cl_5: cl_5_correct_count += 1
            if place_name == cl_10_tx: cl_10_tx_correct_count += 1
            if place_name == cl_5_tx: cl_5_tx_correct_count += 1
            time.sleep(5)
        print("cl_10 accuracy:", cl_10_correct_count/36)
        print("cl_5 accuracy:", cl_5_correct_count/36)
        print("cl_10_tx accuracy:", cl_10_tx_correct_count/36)
        print("cl_5_tx accuracy:", cl_5_tx_correct_count/36)
    else:
        print("Current location:")
        while True:
            current_location10, error_scores = get_current_location(rss_map, RSS_NULL, available_gateways, 10, connection, False)
            current_location5, error_scores = get_current_location(rss_map, RSS_NULL, available_gateways, 5, connection, False)
            print("10:",current_location10,"5:",current_location5)
            #send_to_web(current_location5)
            #check_interior_exterior(connection, current_location5, error_scores)
            time.sleep(5)
        
if __name__ == "__main__":
    main()
