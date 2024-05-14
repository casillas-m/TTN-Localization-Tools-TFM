from secrets_folder.secrets_file import ttn_apikey
from scipy.ndimage import gaussian_filter1d
from scipy.stats import median_abs_deviation
from datetime import datetime
import requests
import json
import numpy as np

def fetch_data(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text.splitlines()
    else:
        print("Error code:", response.status_code)
        return []

def get_channel(freq):
    channel_dict = {
        "868100000": 0,
        "868300000": 1,
        "868500000": 2,
        "867100000": 3,
        "867300000": 4,
        "867500000": 5,
        "867700000": 6,
        "867900000": 7,
        "868800000": 8
    }
    
    return channel_dict.get(str(freq))

def parse_json_data(json_data):
    parsed_data = []
    for line in json_data:
        parsed_line = json.loads(line)
        received_at = parsed_line.get("result", {}).get("received_at", {})
        uplink_message = parsed_line.get("result", {}).get("uplink_message", {})
        decoded_payload = uplink_message.get("decoded_payload")
        rx_metadata_arr = uplink_message.get("rx_metadata", [])
        frequency = uplink_message.get("settings", {}).get("frequency", {})
        channel = get_channel(frequency)
        if decoded_payload:
            parsed_line = {
                "received_at": received_at[:26] + "Z", #Shorten microseconds for datetime compatibility
                "decoded_payload": decoded_payload,
                "rx_metadata": [{"gateway_id": rx_meta.get("gateway_ids").get("gateway_id"), "eui": rx_meta.get("gateway_ids").get("eui"),"rssi": rx_meta.get("rssi")} for rx_meta in rx_metadata_arr],
                "frequency": frequency,
                "channel": channel
            }
            parsed_data.append(parsed_line)
            
    return parsed_data

def calculate_avg_rssi(parsed_data):
    gateway_rssi_dict = {}
    for item in parsed_data:
        rx_metadata_arr = item.get("rx_metadata", [])
        
        for rx_meta in rx_metadata_arr:
            gateway_id = rx_meta.get("gateway_id")
            rssi = rx_meta.get("rssi")

            if gateway_id not in gateway_rssi_dict:
                gateway_rssi_dict[gateway_id] = [rssi]
            else:
                gateway_rssi_dict[gateway_id].append(rssi)
    avg_rssi_per_gateway = {}
    for gateway_id, rssi_list in gateway_rssi_dict.items():
        avg_rssi_per_gateway[gateway_id] = sum(rssi_list) / len(rssi_list)

    return avg_rssi_per_gateway

def calculate_channels_avg_rssi(parsed_data):
    gateway_rssi_dict = {}
    for item in parsed_data:
        channel = item.get("channel")
        rx_metadata_arr = item.get("rx_metadata", [])
        
        for rx_meta in rx_metadata_arr:
            gateway_id = rx_meta.get("gateway_id")
            rssi = rx_meta.get("rssi")

            if gateway_id not in gateway_rssi_dict:
                gateway_rssi_dict[gateway_id] = {channel:[rssi]}
            elif channel not in gateway_rssi_dict[gateway_id].keys():
                gateway_rssi_dict[gateway_id][channel] = [rssi]
            else:
                gateway_rssi_dict[gateway_id][channel].append(rssi)
    avg_rssi_per_gateway = {}
    for gateway_id, ch_rssi_map in gateway_rssi_dict.items():
        avg_rssi_per_channel = {}
        for ch, rssi_list in ch_rssi_map.items():
            avg_rssi_per_channel[ch] = sum(rssi_list) / len(rssi_list)
        avg_rssi_per_gateway[gateway_id] = avg_rssi_per_channel
    return avg_rssi_per_gateway

def calculate_channels_gauss_rssi(parsed_data, sigma_mode):
    gateway_rssi_dict = {}
    for item in parsed_data:
        channel = item.get("channel")
        rx_metadata_arr = item.get("rx_metadata", [])
        
        for rx_meta in rx_metadata_arr:
            gateway_id = rx_meta.get("gateway_id")
            rssi = rx_meta.get("rssi")

            if gateway_id not in gateway_rssi_dict:
                gateway_rssi_dict[gateway_id] = {channel:[rssi]}
            elif channel not in gateway_rssi_dict[gateway_id].keys():
                gateway_rssi_dict[gateway_id][channel] = [rssi]
            else:
                gateway_rssi_dict[gateway_id][channel].append(rssi)
    avg_rssi_per_gateway = {}
    for gateway_id, ch_rssi_map in gateway_rssi_dict.items():
        avg_rssi_per_channel = {}
        for ch, rssi_list in ch_rssi_map.items():
            if sigma_mode == 1:
                sigma = median_abs_deviation(rssi_list) / 0.6745
            else:
                sigma = np.std(rssi_list)
            if sigma > 0:
                gauss_rssi_list = gaussian_filter1d(rssi_list, sigma=sigma)
                avg_rssi_per_channel[ch] = sum(gauss_rssi_list) / len(gauss_rssi_list)
            else:
                avg_rssi_per_channel[ch] = sum(rssi_list) / len(rssi_list)
        avg_rssi_per_gateway[gateway_id] = avg_rssi_per_channel
    return avg_rssi_per_gateway

def main():
    url = "https://eu1.cloud.thethings.network/api/v3/as/applications/tfm-lorawan/packages/storage/uplink_message"
    headers = {
      'Authorization': 'Bearer ' + ttn_apikey
    }

    json_data = fetch_data(url, headers)
    if json_data:
        parsed_data = parse_json_data(json_data)
        for message in parsed_data:
            print(message["decoded_payload"], message["frequency"], message["channel"], datetime.strptime(message["received_at"],"%Y-%m-%dT%H:%M:%S.%fZ"))
        rssi_gateways = calculate_avg_rssi(parsed_data)
        print("--------------------------")
        print("Average RSSI:")
        for gateway_id, avg_rssi in rssi_gateways.items():
            print(f"Gateway ID: {gateway_id}, Avg RSSI: {avg_rssi}")
        ch_rssi_gateways = calculate_channels_avg_rssi(parsed_data)
        print("--------------------------")
        print("Average per channel RSSI:")
        for gateway_id, ch_rssi in ch_rssi_gateways.items():
            ch_rssi_sorted = dict(sorted(ch_rssi.items()))
            print(f"Gateway ID: {gateway_id}, Avg RSSI: {ch_rssi_sorted}")
            for ch, rssi in ch_rssi_sorted.items():
                print(f"{ch},{rssi}")
    else:
        print("No data available")
        
if __name__ == "__main__":
    main()
