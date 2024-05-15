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
    print("Type 'A' to get average rss map")
    print("Type 'G1' to get average gauss filtered (sigma MAD / 0.6745) rss map")
    print("Type 'G2' to get average gauss filtered (sigma std) rss map")
    while True: 
      command = input("Command: ").strip().lower()
      if command in ['a','g1','g2']:
        break
      else:
        print("Unknown command")
    print("---------------------------")
    print("RSS_NULL = -200")
    print("rss_map = {")
    #Iterate through all time tuples
    for place in time_map:
      (begin, end) = place["time_tuple"]
      place_name = place["place_name"]
      begin_end_messages = ttn_data.get_time_range_messages(parsed_data, begin, end)
      ch_rssi_gateways = {}
      if command == 'a':
        ch_rssi_gateways = ttn_data.calculate_channels_avg_rssi(begin_end_messages)
      elif command == 'g1':
        ch_rssi_gateways = ttn_data.calculate_channels_gauss_rssi(begin_end_messages, 1)
      elif command == 'g2':
        ch_rssi_gateways = ttn_data.calculate_channels_gauss_rssi(begin_end_messages, 0)
      ch_rssi_gateways = dict(sorted(ch_rssi_gateways.items()))
      for gateway_id, ch_rssi in ch_rssi_gateways.items():
          #Completar canales con RSSI NULL
          for ch in range(8):
            if ch not in ch_rssi.keys():
              ch_rssi[ch] = 'RSS_NULL'
          ch_rssi_gateways[gateway_id] = dict(sorted(ch_rssi.items()))     
      print(f"'{place_name}':",str(ch_rssi_gateways).replace("'RSS_NULL'","RSS_NULL"))
      print(",")
    print("}")
    print("---------------------------")
  else:
    print("No data available")


if __name__ == "__main__":
    main()
