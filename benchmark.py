#Mockup data for testing
from secrets_folder.parsed_data_recorrido import parsed_data_stored

from secrets_folder.secrets_file import ttn_apikey
import matplotlib.pyplot as plt
from maps.disca_map import rss_map, RSS_NULL
from locate import least_squares_classification
import ttn_data
import time_mapping
import random
import copy

def plot_benchmark_accuracy(benchmark_results):
    # Extracting data for plotting
    accuracy = [run["accuracy"] * 100 for run in benchmark_results] 
    zone_accuracy = [run["zone_accuracy"] * 100 for run in benchmark_results]
    floor_accuracy = [run["floor_accuracy"] * 100 for run in benchmark_results]
    # Plotting the data
    plt.figure(figsize=(12, 6))
    plt.plot(accuracy, label='Benchmark Accuracy', marker='o', color='blue')
    plt.plot(zone_accuracy, label='Zone Accuracy', marker='o', color='green')
    plt.plot(floor_accuracy, label='Floor Accuracy', marker='o', color='red')
    plt.title('Benchmark Accuracy Over Multiple Runs')
    plt.xlabel('Benchmark Run')
    plt.ylabel('Accuracy (%)')
    plt.ylim(50, 100)
    plt.legend()
    plt.grid(True)
    plt.show()

def generate_test_set(messages, test_qty):
    random.shuffle(messages)
    test_set = [{} for _ in range(test_qty)]
    for message in messages:
        rnd_test = random.randint(0, test_qty - 1)
        channel = message["channel"] 
        for gateway in message["rx_metadata"]:
            gateway_id = gateway["gateway_id"]
            rssi = gateway["rssi"]
            if gateway_id not in test_set[rnd_test]:
                test_set[rnd_test][gateway_id] = {}
            if channel in test_set[rnd_test][gateway_id]:
                test_set[rnd_test][gateway_id][channel] = (rssi + test_set[rnd_test][gateway_id][channel])/2
            else:
                test_set[rnd_test][gateway_id][channel] = rssi
    return test_set

def generate_benchmark_tests(parsed_data, time_map, test_qty):
    benckmark_tests = {}
    for place in time_map:
        (begin, end) = place["time_tuple"]
        place_name = place["place_name"]
        begin_end_messages = ttn_data.get_time_range_messages(parsed_data, begin, end)
        test_set = generate_test_set(begin_end_messages, test_qty)
        benckmark_tests[place_name] = test_set
    return benckmark_tests

def run_benchmark(benckmark_tests, rss_map, RSS_NULL):
    available_gateways = ["rak7248-grc-pm65","main-gtw-grc","itaca-upv-022"]
    benchmark_total = 0
    benchmark_correct = 0
    benchmark_correct_zone = 0
    benchmark_correct_floor = 0
    for place_name in benckmark_tests.keys():
        test_total = 0
        test_correct = 0
        test_correct_zone = 0
        test_correct_floor = 0
        for test in benckmark_tests[place_name]:
            #Check if test is not empty
            if test:
                test_total += 1
                classification, error_scores = least_squares_classification(rss_map, RSS_NULL, available_gateways, test)
                if place_name == classification:
                    test_correct += 1
                if place_name[1] == classification[1]:
                    test_correct_zone += 1
                if place_name[0] == classification[0]:
                    test_correct_floor += 1
                #print(f"Expected {place_name}, result {classification}")
        benchmark_total += test_total
        benchmark_correct += test_correct
        benchmark_correct_zone += test_correct_zone
        benchmark_correct_floor += test_correct_floor
        #print(f"Accuracy: {100 * test_correct/test_total}%")
    benchmark_result = {
        "accuracy": benchmark_correct/benchmark_total,
        "zone_accuracy": benchmark_correct_zone/benchmark_total,
        "floor_accuracy": benchmark_correct_floor/benchmark_total,
    }
    #print("Benchmark run:")
    #print(f"Benchmark accuracy: {100 * benchmark_correct/benchmark_total}%")
    #print(f"Benchmark zone accuracy: {100 * benchmark_correct_zone/benchmark_total}%")
    #print(f"Benchmark floor accuracy: {100 * benchmark_correct_floor/benchmark_total}%")
    return benchmark_result
            
def get_best_rss_null(rss_begin, rss_end, rss_step, benckmark_tests, rss_map, RSS_NULL):
    rss_null_positions = []
    #Find all RSS_NULL inside rss_map
    for place, gateways in rss_map.items():
        for gateway, rss_values in gateways.items():
            for ch, rss in rss_values.items():
                if rss == RSS_NULL:
                    rss_null_positions.append((place,gateway,ch))
    #Test all RSS_NULL values
    benchmark_results = []
    for rss_null_value in range(rss_begin, rss_end, rss_step):
        #Change all RSS_NULL in map
        rss_map_new = copy.deepcopy(rss_map)
        for (place,gateway,ch) in rss_null_positions:
            rss_map_new[place][gateway][ch] = rss_null_value
        #Run benchmark using new RSS_NULL value
        benchmark_result = run_benchmark(copy.deepcopy(benckmark_tests), rss_map_new, rss_null_value)
        benchmark_results.append((rss_null_value, benchmark_result["accuracy"]))
    #Get best RSS_NULL
    #print(benchmark_results)
    best_result = max(benchmark_results, key=lambda x: x[1])
    return best_result

def main():
    url = "https://eu1.cloud.thethings.network/api/v3/as/applications/tfm-lorawan/packages/storage/uplink_message"
    headers = {
        'Authorization': 'Bearer ' + ttn_apikey
    }
    json_data = []
    print("Benchmark tool")
    print("Type 'R' to use real data")
    print("Type 'M' to use mockup data (for testing)")
    command = input("Command: ").strip().lower()
    if command == 'r':
        json_data = ttn_data.fetch_data(url, headers)
    elif command == 'm':
        json_data = True
    else:
        print("Unknown command. Exit.")
        return
    time_map = time_mapping.time_map()
    if json_data:
        parsed_data = []
        if command == 'r':
            parsed_data = ttn_data.parse_json_data(json_data)
        elif command == 'm':
            parsed_data = parsed_data_stored
        #Get the best RSS_NULL value
        print("Running best RSS_NULL test...")
        rss_null_sum = 0
        rss_null_count = 0
        for _ in range(30):
            benckmark_tests = generate_benchmark_tests(parsed_data, time_map, 5)
            rss_null_result = get_best_rss_null(0, -400, -1, copy.deepcopy(benckmark_tests), copy.deepcopy(rss_map), RSS_NULL)
            rss_null_sum += rss_null_result[0]
            rss_null_count += 1
            #print(rss_null_result)
        print("Best RSS_NULL:",rss_null_sum/rss_null_count)
        
        #Run benchmark using the default RSS_NULL value
        print("Running benchmark...")
        print("This test does not use the calculated RSS_NULL. Using:", RSS_NULL)
        benchmark_results = []
        for _ in range(30):
            benckmark_tests = generate_benchmark_tests(parsed_data, time_map, 5)
            benchmark_result = run_benchmark(copy.deepcopy(benckmark_tests), copy.deepcopy(rss_map), RSS_NULL)
            benchmark_results.append(benchmark_result)
            #print(benchmark_result)
        plot_benchmark_accuracy(benchmark_results)
    else:
        print("No data available")
        
if __name__ == "__main__":
    main()