import csv
import requests

#################################################################################
# 
#   Project: Elevation Collector
#
#   Author: Kennedy Smith   
#   Project Class: CS458
#   Email: kennedy.smith@yale.edu
#
#   Description:
#   This Python script collects all elevations for given
#   zip codes in the file 'zip_codes.csv' in the parent directory and
#   places them in a file 'elevations.csv'
#
#   Requests were throttled by the API, so results may have been incomplete.
#  
#   Acknowledgements:
#   This script uses data from the GeoNames public API (http://www.geonames.org).
#   GeoNames is a free geographic database that provides
#   data and web services for place names, coordinates, and other
#   geographic information.
#
#################################################################################

# define the input data as a list coordinates
input_data = []

with open('zip_codes.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # extract the ZIP code, latitude, and longitude values from the row
        zipcode = row['ZIP']
        latitude = row['LAT']
        longitude = row['LNG']
        input_data.append(f'{latitude},{longitude}')

# divide the input data into batches of 20 coordinates
batch_size = 20
input_batches = [input_data[i:i+batch_size] for i in range(0, len(input_data), batch_size)]


input_batches = input_batches[1190:]

# loop through each input batch and query GeoNames for elevation data
data = []

count = 0
size = len(input_batches)
for batch in input_batches:
    print("Count: ", count, " of ", size)
    latitudes = []
    longitudes = []
    for item in batch:
        lat, lng = item.split(',')
        latitudes.append(lat.strip())
        longitudes.append(lng.strip())
    latitudes_str = ','.join(latitudes).strip()
    longitudes_str = ','.join(longitudes).strip()
    url = 'http://api.geonames.org/srtm1?&username=kkode&lats=' + latitudes_str.strip() + '&lngs=' + longitudes_str.strip()
    response = requests.get(url)

    if 'the hourly limit of 1000 credits' in response.text:
        print("Hourly limit exceeded. Breaking out of loop.")
        break   

    elevation_data = response.text
    
    for i, item in enumerate(batch):
        elevation_value = elevation_data.splitlines()[i]
        data.append({'input': item, 'elevation': elevation_value})

    count = count + 1

# write the input and elevation data to a CSV file
with open('elevations.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['input', 'elevation'])
    for row in data:
        writer.writerow([row['input'], row['elevation']])
