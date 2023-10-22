import csv
import json
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Write dictionary to text file at path given by file name if mode == 'w'
# Read the content of the text file at file_name into data_dict if mode == 'r'
def readwrite_dict(data_dict, file_name, mode):
    if mode not in ('r', 'w'):
        raise ValueError("Mode must be 'r' (read) or 'w' (write).")

    file_name = os.path.join(os.getcwd(),file_name)
    if mode == 'r':
        # Read from the file and update the dictionary
        try:
            with open(file_name, 'r') as file:
                loaded_data = json.load(file)
                data_dict.update(loaded_data)
        except FileNotFoundError:
            print(f"File '{file_name}' not found. Dictionary remains unchanged.")
    elif mode == 'w':
        # Write the dictionary to the file
        with open(file_name, 'w') as file:
            json.dump(data_dict, file)

def getLocationCapacityMap(year):
    with open(f'daily-shelter-overnight-occupancy-{year}.csv', mode='r', newline='') as file:
        locationCapacityMap = {}
        reader = csv.DictReader(file)
        for row in reader:
            if locationCapacityMap.get(row["LOCATION_ID"]) == None:
                locationCapacityMap[row["LOCATION_ID"]] = row["CAPACITY_TYPE"]

        readwrite_dict(locationCapacityMap,f'Data\\Program-Based-Time-Series\\{year}\\location-capacity-map.txt','w')
        return locationCapacityMap
    
def getProgramMap(year):
    with open(f'daily-shelter-overnight-occupancy-{year}.csv', mode='r', newline='') as file:
        programIdNameMap = {}
        reader = csv.DictReader(file)
        for row in reader:
            if programIdNameMap.get(row["PROGRAM_ID"]) == None:
                programIdNameMap[row["PROGRAM_ID"]] = row["PROGRAM_NAME"]

        readwrite_dict(programIdNameMap,f'Data\\Program-Based-Time-Series\\{year}\\programs.txt','w')
        return programIdNameMap

def get_time_series_for_program(program_id,year,locationCapacityMap,programMap,statType):
    timeSeries = {};
    print(f"Getting time series - {year} - {program_id} - {statType}")
    with open(f'daily-shelter-overnight-occupancy-{year}.csv', mode='r', newline='') as file:
        reader = csv.DictReader(file)
        capacityType = ''
        locationId = None
        for row in reader:
            if (row['PROGRAM_ID'] != str(program_id)):
                continue

            currentDay = row['OCCUPANCY_DATE']

            if (locationId == None):
                locationId = row['LOCATION_ID']

            if (capacityType == '' and locationId != None):
                capacityType = locationCapacityMap[locationId]
            
            currentStat = ''
            if capacityType == 'Room Based Capacity' and statType == 'NumberBased':
                currentStat = row["UNOCCUPIED_ROOMS"]
            elif capacityType == 'Room Based Capacity' and statType == 'RateBased':
                currentStat = row["OCCUPANCY_RATE_ROOMS"]
            elif capacityType == 'Bed Based Capacity' and statType == 'NumberBased':
                currentStat = row["UNOCCUPIED_BEDS"]
            elif capacityType == 'Bed Based Capacity' and statType == 'RateBased':
                currentStat = row["OCCUPANCY_RATE_BEDS"]

            currentStatInt = ''
            try:
                currentStatInt = int(currentStat)
            except ValueError:
                continue;
            
            timeSeries[currentDay] = currentStatInt

        temp = 'ROOMS' if capacityType == 'Room Based Capacity' else 'BEDS'
        fileName = f"Data\\Program-Based-Time-Series\\{year}\\{statType}\\DataSeries\\{program_id}_{temp}.txt"
        readwrite_dict(timeSeries,fileName,'w')

def plot_data(x_values, y_values, x_label, y_label,save_location,title):
    y_values_floats = [float(y) for y in y_values]
    plt.figure(figsize=(8, 6))
    plt.plot(x_values, y_values_floats, marker='o', linestyle='-')
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    # Set the locator
    locator = mdates.MonthLocator()  # every month
    # Specify the format - %b gives us Jan, Feb...
    fmt = mdates.DateFormatter('%b')
    X = plt.gca().xaxis
    X.set_major_locator(locator)
    # Specify formatter
    X.set_major_formatter(fmt)

    plt.title(title)
    plt.grid(True)
    plt.savefig(save_location)

    plt.close()
    print(f"Saved plot - {title}")

def get_data_series_and_plot(year,statType):
    data_series_path = os.path.join(os.getcwd(),f"Data\\Program-Based-Time-Series\\{year}\\{statType}\\DataSeries")
    
    locationCapacityMap = getLocationCapacityMap(year)
    programMap = getProgramMap(year)
    # readwrite_dict(programMap,f'Data\\Program-Based-Time-Series\\{year}\\programs.txt','r')

    # for programId in programMap:
    #     get_time_series_for_program(programId,year,locationCapacityMap,programMap,statType)

    for file_path in os.listdir(data_series_path):
        fileNameWithoutExt = file_path.split('.')[0]
        type = file_path.split('_')[1].split('.')[0]
        dataSeriesDict = {}
        readwrite_dict(dataSeriesDict,f'Data\\Program-Based-Time-Series\\{year}\\{statType}\\DataSeries\\{file_path}','r')
        
        markRemove = list()
        for key in dataSeriesDict:
            try:
                result = int(dataSeriesDict[key])
            except ValueError:
                markRemove.append(key)
        
        for badKey in markRemove:
            dataSeriesDict.pop(badKey)

        title = programMap[file_path.split('_')[0]]
        plot_data(dataSeriesDict.keys(),dataSeriesDict.values(),'Date',f'Unoccupied {type}',f'Data\\Program-Based-Time-Series\\{year}\\{statType}\\Plots\\{fileNameWithoutExt}.png',title)


get_data_series_and_plot(2022,'NumberBased')