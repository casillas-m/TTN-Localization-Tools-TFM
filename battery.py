from secrets_folder.secrets_file import ttn_apikey, TTN_URL
from datetime import datetime, timezone
import matplotlib.pyplot as plt
import time_mapping
import ttn_data
import time

def plot_battery_level(battery_level):
    """
    Plot the battery voltage over time.
    Inputs:
    - battery_level: List of tuples (seconds, voltage)
    This function plots voltage data over time using matplotlib, with custom settings for plot size, markers, colors, and axes.
    """
    seconds = [measurement[0] for measurement in battery_level]
    battery_voltages = [measurement[1] for measurement in battery_level]
    plt.figure(figsize=(12, 6))
    plt.plot(seconds, battery_voltages, marker='o', color='blue')
    plt.title('Battery level over time')
    plt.xlabel('Seconds (s)')
    plt.ylabel('Voltage (v)')
    plt.ylim(3.25, 4.1)
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_battery_level_2(battery_level1, battery_level2):
    """
    Plot two sets of battery voltage data for comparison.
    Inputs:
    - battery_level1: First list of tuples (seconds, voltage)
    - battery_level2: Second list of tuples (seconds, voltage)
    This function compares two battery tests by plotting their voltage levels over time on the same graph with different colors and markers.
    """
    seconds1 = [measurement[0] for measurement in battery_level1]
    battery_voltages1 = [measurement[1] for measurement in battery_level1]
    seconds2 = [measurement[0] for measurement in battery_level2]
    battery_voltages2 = [measurement[1] for measurement in battery_level2]
    plt.figure(figsize=(12, 6))
    plt.plot(seconds1, battery_voltages1, label='Battery test 1', marker='o', color='blue')
    plt.plot(seconds2, battery_voltages2, label='Battery test 2', marker='o', color='red')
    plt.title('Battery level over time')
    plt.xlabel('Seconds (s)')
    plt.ylabel('Voltage (v)')
    plt.ylim(3.25, 4.1)
    plt.legend()
    plt.grid(True)
    plt.show()
    
def get_last_battery_voltage(connection):
    """
    Retrieve the last recorded battery voltage from the TTN data source.
    Input:
    - connection: Dictionary containing server URL and headers
    Returns the last recorded battery voltage if available, parsing JSON data received from the server.
    """
    json_data = ttn_data.get_last_n_messages(connection["url"], connection["headers"], 1)
    if json_data:
        parsed_data = ttn_data.parse_json_data(json_data)
        if len(parsed_data)>0:
            last_message = parsed_data[0]
            if "decoded_payload" in last_message.keys():
                if "analog_in_8" in last_message["decoded_payload"].keys():
                    battery_voltage = last_message["decoded_payload"]["analog_in_8"]
                    return battery_voltage

def get_range_battery_levels(connection, begin, end):
    """
    Retrieve battery voltage levels for a specific time range from the TTN data source.
    Inputs:
    - connection: Dictionary containing server URL and headers
    - start_time: Start time of the range as a string in the format "YYYY-MM-DDTHH:MM:SS.SSSSSSZ"
    - end_time: End time of the range as a string in the format "YYYY-MM-DDTHH:MM:SS.SSSSSSZ"
    Outputs:
    - Returns a list of tuples (time, voltage) for the specified time range.
    """
    begin = datetime.strptime(begin,"%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    end = datetime.strptime(end,"%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    battery_level = []
    json_data = ttn_data.fetch_data(connection["url"], connection["headers"])
    if json_data:
        parsed_data = ttn_data.parse_json_data(json_data)
        begin_end_messages = ttn_data.get_time_range_messages(parsed_data, begin, end)
        if len(begin_end_messages) > 0:
            message = begin_end_messages[0]
            begin_time = datetime.strptime(message["received_at"],"%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            print(begin_time)
        for message in begin_end_messages:
            if "decoded_payload" in message.keys():
                if "analog_in_8" in message["decoded_payload"].keys():
                    battery_voltage = message["decoded_payload"]["analog_in_8"]
                    received_at = datetime.strptime(message["received_at"],"%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
                    seconds = (received_at - begin_time).total_seconds()
                    battery_level.append((seconds,battery_voltage))
    return battery_level

def main():
    """
    Main function to interact with the user for battery performance measurement.
    This function allows the user to choose between measuring battery voltage over 15 minutes or using a predefined time range to plot the battery levels.
    """
    connection = {
        "url": TTN_URL,
        "headers": {
            "Authorization": "Bearer " + ttn_apikey
        }
    }
    #battery_level2 = [(0, 4.02), (10, 4.02), (20, 4.02), (30, 4.02), (40, 4.02), (50, 4.02), (60, 4.02), (70, 4.02), (80, 4.02), (90, 4.02), (100, 4.02), (110, 4.02), (120, 4.02), (130, 4.02), (140, 4.02), (150, 4.02), (160, 4.02), (170, 4.02), (180, 4.02), (190, 4.02), (200, 4.02), (210, 4.02), (220, 4.02), (230, 4.02), (240, 4.02), (250, 4.02), (260, 4.02), (270, 4.02), (280, 4.02), (290, 4.02), (300, 4.01), (310, 4.01), (320, 4.01), (330, 4.01), (340, 4.01), (350, 4.01), (360, 4.01), (370, 4.01), (380, 4.01), (390, 4.01), (400, 4.01), (410, 4), (420, 4), (430, 4), (440, 4), (450, 4), (460, 4), (470, 4), (480, 4), (490, 4), (500, 4), (510, 4), (520, 4), (530, 4), (540, 4), (550, 4), (560, 4), (570, 4), (580, 4), (590, 4), (620, 3.99), (630, 3.99), (640, 3.99), (650, 3.99), (660, 3.99), (670, 3.99), (680, 3.99), (690, 3.99), (700, 3.99), (710, 3.99), (720, 3.99), (730, 3.99), (740, 3.99), (750, 3.99), (760, 3.99), (770, 3.99), (780, 3.99), (790, 3.99), (800, 3.99), (810, 3.99), (820, 3.99), (830, 3.99), (840, 3.99), (850, 3.99), (860, 3.99), (870, 3.98), (880, 3.98), (890, 3.98)]
    #battery_level1 = [(0, 4.02), (10, 4.02), (20, 4.02), (30, 4.02), (40, 4.02), (50, 4.02), (60, 4.02), (70, 4.01), (80, 4.01), (90, 4.01), (100, 4.01), (110, 4.01), (120, 4.01), (130, 4.01), (140, 4.01), (150, 4), (160, 4), (170, 4.01), (180, 4.01), (190, 4), (200, 4), (210, 4), (220, 4), (230, 4), (240, 4), (250, 3.99), (260, 3.99), (270, 3.99), (280, 3.99), (290, 3.99), (300, 3.99), (310, 3.99), (320, 3.99), (330, 3.99), (340, 3.99), (350, 3.99), (360, 3.99), (370, 3.98), (380, 3.98), (390, 3.99), (400, 3.99), (410, 3.98), (420, 3.98), (430, 3.98), (440, 3.98), (450, 3.98), (460, 3.98), (470, 3.98), (480, 3.98), (490, 3.97), (500, 3.97), (510, 3.97), (520, 3.97), (530, 3.97), (540, 3.97), (550, 3.97), (560, 3.97), (570, 3.97), (580, 3.97), (590, 3.97), (600, 3.97), (610, 3.97), (620, 3.97), (630, 3.96), (640, 3.96), (650, 3.96), (660, 3.96), (670, 3.96), (680, 3.96), (690, 3.96), (700, 3.96), (710, 3.96), (720, 3.96), (730, 3.96), (740, 3.96), (750, 3.96), (760, 3.96), (770, 3.95), (780, 3.95), (790, 3.95), (800, 3.95), (810, 3.95), (820, 3.95), (830, 3.95), (840, 3.94), (850, 3.94), (860, 3.94), (870, 3.94), (880, 3.94), (890, 3.94)]
    #plot_battery_level_2(battery_level1, battery_level2)
    
    print("Battery performance tool")
    print("Type 'M' to measure for 15 minutes")
    print("Type 'R' to use message time range")
    command = input("Command: ").strip().lower()
    battery_level = []
    if command == 'm':
        for moment in range(90):
            if moment%6 == 0: print("Minute:", moment/6)
            battery_voltage = get_last_battery_voltage(connection)
            if battery_voltage:
                battery_level.append((moment*10,battery_voltage))
            time.sleep(10)
        print("battery_level =", battery_level)
        plot_battery_level(battery_level) 
    elif command == 'r':
        time_map = time_mapping.time_map()
        for time_range in time_map:
            (begin, end) = time_range["time_tuple"]
            battery_level = get_range_battery_levels(connection, begin.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), end.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
            #battery_level = get_range_battery_levels(connection, "2024-06-10T10:27:00.000000Z", "2024-06-10T11:27:00.000000Z")
            plot_battery_level(battery_level)
    else:
        print("Unknown command. Exit.")
        return
    
if __name__ == "__main__":
    main()