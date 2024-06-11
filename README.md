# Project Documentation

![Generic badge](https://img.shields.io/badge/version-1.0.0-green.svg)
![Generic badge](https://img.shields.io/badge/license-MIT-blue.svg)

## Table of Contents
1. [Overview](#overview)
2. [Files and Descriptions](#files-and-descriptions)
3. [Setup and Configuration](#setup-and-configuration)
4. [Related Repositories](#related-repositories)
5. [License](#license)

## Overview
This project is developed as part of a Master's thesis focused on demonstrating real-time localization of LoRaWAN devices. It facilitates the interaction with The Things Network (TTN), graphical representation of data, and performance testing of the deployments.

### Files and Descriptions

#### `battery.py`
- **Purpose**: Manages battery level monitoring for IoT devices.
- **Key Functions**:
  - `plot_battery_level()`: Graphs battery voltage over time.
  - `get_last_battery_voltage()`: Retrieves the last recorded battery voltage.
  - `get_range_battery_levels()`: Fetches battery voltage levels within a specified time range.

#### `map.py`
- **Purpose**: Manages RSS map generation for TTN data. The resulting output is intended to be written in a file inside a folder named "maps".
- **Key Functions**:
  - `main()`: Fetches and processes data to generate RSS maps based on user input.

#### `benchmark.py`
- **Purpose**: Provides benchmarking tools for location accuracy testing.
- **Dependencies**: In order to work this script needs a previously generated map (using the map.py script).
- **Key Functions**:
  - `plot_benchmark_accuracy()`: Plots the accuracy of location benchmarks.
  - `generate_benchmark_tests()`: Generates test data for benchmarking location systems.
  - `run_benchmark()`: Runs benchmark tests and returns accuracy data.

#### `locate.py`
- **Purpose**: Handles location determination based on RSSI data.
- **Dependencies**: In order to work this script needs a previously generated map (using the map.py script).
- **Key Functions**:
  - `least_squares_classification()`: Classifies the new data into location categories using the least squares method.
  - `get_current_location()`: Fetches the current location using the latest RSS data.

#### `time_mapping.py`
- **Purpose**: Provides tools for creating time-based mappings for data analysis.
- **Key Functions**:
  - `time_map_manual()`: Allows manual entry of time-place mappings.
  - `time_map_csv()`: Creates time mappings from CSV-like input.

#### `ttn_data.py`
- **Purpose**: Manages data fetching and processing from TTN.
- **Key Functions**:
  - `fetch_data()`: Retrieves data from TTN using specific API endpoints.
  - `parse_json_data()`: Parses JSON formatted data from TTN into a usable format.

#### `web_app.py`
- **Purpose**: A Flask web application to visualize location data on a map.
- **Key Functions**:
  - `set_point()`: Updates a map with a new location point from received JSON data.

#### `web_test.py`
- **Purpose**: Tests the functionality of the web application.
- **Key Functions**:
  - Simulates sending a location update to the web application and prints the response.

## Setup and Configuration

### Prerequisites

1. **Python Installation**: Ensure Python 3.7 or higher is installed on your system.
2. **Clone the Repository**: Clone the project repository to your local machine using Git:
   ```
   git clone <repository-url>
   cd <project-directory>
   ```
3. **Dependencies**: Install required Python libraries using pip:
   ```
   pip install -r requirements.txt
   ```

### Configuration

- Ensure that all API keys and necessary credentials are set up as follows.
    - Create a "secrets_folder" folder in the root of the project directory.
    - Inside "secrets_folder" folder, create a file named secrets_file.py.
    - Define the TTN credentials in secrets_file.py as follows.
      ```
      ttn_apikey = <your-ttn-api-key>
      WEB_APP_URL = <your-web-app-url>
      TTN_URL = <your-ttn-uplink-message-url>
      DOWNLINK_DEV1_URL = <your-ttn-downlink-message-url-dev1>
      DOWNLINK_DEV2_URL = <your-ttn-downlink-message-url-dev2>
      ```
- For web applications, ensure the Flask app is properly configured to run on your local environment or server.

### Running the Scripts

To run any of the provided scripts, navigate to the script directory and run:
```
python <script_name>.py
```

## Related Repositories

This project leverages and extends various existing open-source projects related to IoT device management and data visualization.

### [TTN](https://www.thethingsnetwork.org/)
**Description**: The Things Network provides a set of open tools and a global, open network to build your next IoT application at low cost, featuring maximum security and ready to scale.

### [Matplotlib](https://github.com/matplotlib/matplotlib)
**Description**: Matplotlib is a comprehensive library for creating static, animated, and interactive visualizations in Python.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. This includes all scripts, documentation, and other associated content.
