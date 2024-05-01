from secrets_folder.secrets_file import ttn_apikey
import ttn_data
import time_mapping
from datetime import datetime, timezone

def main(): 
  url = "https://eu1.cloud.thethings.network/api/v3/as/applications/tfm-lorawan/packages/storage/uplink_message"
  headers = {
    'Authorization': 'Bearer ' + ttn_apikey
  }
  time_map = time_mapping.time_map()
  json_data = ttn_data.fetch_data(url, headers)
  if json_data:
    parsed_data = ttn_data.parse_json_data(json_data)
    #Iterate through all time tuples
    for i, (begin, end) in enumerate(time_map, 1):
      print(f"Begin: {begin.strftime("%Y-%m-%dT%H:%M:%S.%fZ")} End: {end.strftime("%Y-%m-%dT%H:%M:%S.%fZ")}")
      begin_end_messages = []
      #Iterate trhough all TTN messages
      for message in parsed_data:
        received_at = datetime.strptime(message["received_at"],"%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        #Message between time begin and end
        if begin.replace(tzinfo=timezone.utc) <= received_at <= end.replace(tzinfo=timezone.utc):
          begin_end_messages.append(message)
          print(message["decoded_payload"])
      rssi_gateways = ttn_data.calculate_avg_rssi(begin_end_messages)
      print("Average RSSI:")
      for gateway_id, avg_rssi in rssi_gateways.items():
            print(f"Gateway ID: {gateway_id}, Avg RSSI: {avg_rssi}")
      ch_rssi_gateways = ttn_data.calculate_channels_rssi(begin_end_messages)
      print("Average per channel RSSI:")
      for gateway_id, ch_rssi in ch_rssi_gateways.items():
          ch_rssi_sorted = dict(sorted(ch_rssi.items()))
          print(f"Gateway ID: {gateway_id}, Avg RSSI: {ch_rssi_sorted}")
          for ch, rssi in ch_rssi_sorted.items():
              print(f"{ch},{rssi}")
      print("------------------")
  else:
    print("No data available")


if __name__ == "__main__":
    main()
