from datetime import datetime, timezone

def time_map_manual():
    """
    Manually create a list of time mappings with place names.
    Prompts the user to enter begin and end times, and the place name for each time interval.
    Outputs:
    - Returns a list of dictionaries with place names and corresponding time tuples.
    """
    times = []
    print("Manual time mapping")
    print("Instructions:")
    print("Type 'B' to enter the begin time")
    print("Type 'E' to enter the end time")
    print("Type 'F' to finish")
    print("Please enter times in the format 'YYYY-mm-ddTHH:MM:SS.ffffffZ'")
    print("Ex. '2024-04-15T09:38:00.000000Z'")
    while True:
        command = input("Command: ").strip().lower()
        if command == 'b':
            begin_time_str = input("Enter begin time 'YYYY-mm-ddTHH:MM:SS.ffffffZ': ")
            try:
                begin = datetime.strptime(begin_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                print(f"Begin time recorded: {begin.strftime("%Y-%m-%dT%H:%M:%S.%fZ")}")
            except ValueError:
                print("Invalid time format. Please try again")
                del begin
        elif command == 'e':
            if 'begin' in locals():
                end_time_str = input("Enter end time 'YYYY-mm-ddTHH:MM:SS.ffffffZ': ")
                try:
                    end = datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                    print(f"End time recorded: {end.strftime("%Y-%m-%dT%H:%M:%S.%fZ")}")
                    place_name = input("Enter place name: ").strip()
                    times.append({"place_name":place_name, "time_tuple":(begin, end)})
                    del begin
                except ValueError:
                    print("Invalid time format. Please try again")
            else:
                print("Error, begin must be first")
        elif command == 'f':
            break
        else:
            print("Unknown command")
    return times

def time_map_current():
    """
    Create a list of time mappings with place names using the current system time.
    Outputs:
    - Returns a list of dictionaries with place names and corresponding time tuples.
    """
    times = []
    print("Current time mapping")
    print("Instructions:")
    print("Type 'B' to take the begin time")
    print("Type 'E' to take the end time")
    print("Type 'F' to finish")
    while True:
        command = input("Command: ").strip().lower()
        if command == 'b':
            begin = datetime.now(tz=timezone.utc)
            print(f"Begin time {begin.strftime("%Y-%m-%dT%H:%M:%S.%fZ")}")
        elif command == 'e':
            if 'begin' in locals():
                end = datetime.now(tz=timezone.utc)
                print(f"End time {end.strftime("%Y-%m-%dT%H:%M:%S.%fZ")}")
                place_name = input("Enter place name: ").strip()
                times.append({"place_name":place_name, "time_tuple":(begin, end)})
                del begin 
            else:
                print("Error, begin must be first.")
        elif command == 'f':
            break
        else:
            print("Unknown command")
    return times

def time_map_csv():
    """
    Create a list of time mappings with place names from CSV-like input.
    Prompts the user to enter time intervals and place names in a CSV-like format.
    Outputs:
    - Returns a list of dictionaries with place names and corresponding time tuples.
    """
    times = []
    print("CSV time mapping")
    print("Instructions:")
    print("Paste all the time marks in a CSV like format. Each line represents a begin-end time tuple and its name.")
    print("Type 'F' to finish")
    print("Ex:")
    print("2024-04-15T09:29:00.000000Z,2024-04-15T09:38:00.000000Z,place1")
    print("2024-04-15T10:38:00.000000Z,2024-04-15T10:00:00.000000Z,place2")
    print("F")
    print("Enter the list:")
    while True:
        line = input().strip().lower()
        if line == 'f':
            break
        else:
            begin_end_place = line.split(",")
            begin_time_str = begin_end_place[0]
            end_time_str = begin_end_place[1]
            place_name = begin_end_place[2]
            try:
                begin = datetime.strptime(begin_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                end = datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                times.append({"place_name":place_name, "time_tuple":(begin, end)})
                del begin 
                del end
            except ValueError:
                print("Invalid time format")
                return []
    return times
    
def time_map():
    """
    Main function to choose the method for creating time mappings.
    This function allows the user to choose between manual input, current time input, or CSV-like input for creating time mappings.
    Outputs:
    - Returns a list of dictionaries with place names and corresponding time tuples.
    """
    print("Time-place mapping tool")
    print("Type 'M' to use the manual time tool")
    print("Type 'C' to use the current time tool")
    print("Type 'V' to use the CSV time tool")
    print("Type 'F' to finish")
    while True:
        command = input("Command: ").strip().lower()
        if command == 'm':
            return time_map_manual()
        elif command == 'c':
            return time_map_current()
        elif command == 'v':
            return time_map_csv()
        elif command == 'f':
            return []
        else:
            print("Unknown command")
    
def main():
    """
    Main function to demonstrate the time mapping tool.
    This function calls the time mapping tool and prints the resulting time mappings.
    """
    times_map = time_map()
    times = []
    for place in times_map:
        times.append(place["time_tuple"])
    print("\nTime mapping:")
    for i, (begin, end) in enumerate(times, 1):
        print(f"Place {i}, Begin: {begin.strftime("%Y-%m-%dT%H:%M:%S.%fZ")} End: {end.strftime("%Y-%m-%dT%H:%M:%S.%fZ")}")

if __name__ == "__main__":
    main()
