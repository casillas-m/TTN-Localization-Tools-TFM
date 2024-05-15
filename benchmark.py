from secrets_folder.secrets_file import ttn_apikey
from secrets_folder.parsed_data_recorrido import parsed_data_stored
from maps.disca_map import rss_map
from locate import least_squares_classification
import ttn_data
import time_mapping
import random

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

def run_benchmark(benckmark_tests):
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
                classification, error_scores = least_squares_classification(rss_map, available_gateways, test)
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
    print("Benchmark run:")
    print(f"Benchmark accuracy: {100 * benchmark_correct/benchmark_total}%")
    print(f"Benchmark zone accuracy: {100 * benchmark_correct_zone/benchmark_total}%")
    print(f"Benchmark floor accuracy: {100 * benchmark_correct_floor/benchmark_total}%")
            
    

def main():
    url = "https://eu1.cloud.thethings.network/api/v3/as/applications/tfm-lorawan/packages/storage/uplink_message"
    headers = {
        'Authorization': 'Bearer ' + ttn_apikey
    }
    time_map = time_mapping.time_map()
    json_data = ttn_data.fetch_data(url, headers)
    if json_data:
        #parsed_data = ttn_data.parse_json_data(json_data)
        parsed_data = parsed_data_stored
        for i in range(30):
            benckmark_tests = generate_benchmark_tests(parsed_data, time_map, 5)
            run_benchmark(benckmark_tests)      
    else:
        print("No data available")
        
if __name__ == "__main__":
    main()