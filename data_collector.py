import os
import csv
from datetime import datetime, timedelta


########################################################################
# 
#   Project: Weather Data Collector
#
#   Author: Kennedy Smith   
#   Project Class: CS458
#   Email: kennedy.smith@yale.edu
#
#   Description:
#   This Python script reads weather data from CSV files
#   and calculates the average temperature for each day of each year.  
#   The resulting averages are saved as CSV files.
#  
#   Acknowledgements:
#   The weather data used in this project is provided by the 
#   National Centers for Environmental Information (NCEI).
#
######################################################################

# function to get the month and day from a date string
def get_month_day(date_string):
    date_obj = get_date_obj(date_string)
    return "{:02d}-{:02d}".format(date_obj.month, date_obj.day)

def get_date_obj(date_string):
    date_obj = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
    return date_obj;

# set the path for the weather_database folder
weather_db_path = "weather_database"

# create a dictionary to store the daily average temperature change for each day of the year
daily_averages = {}

# helper variables for storing last temp
last_temp = 0;
last_date_key = "None"

# iterate over each year folder
for year_folder in os.listdir(weather_db_path):
    # get the path for the year folder
    year_folder_path = os.path.join(weather_db_path, year_folder)
    
    # skip any files that are not directories
    if not os.path.isdir(year_folder_path):
        continue
    
    print("Processing year folder:", year_folder_path)
    
    # iterate over each CSV file in the year folder
    for csv_file in os.listdir(year_folder_path):
        # get the path for the CSV file
        csv_file_path = os.path.join(year_folder_path, csv_file)
        
        # skip any files that are not CSV files
        if not csv_file.endswith(".csv"):
            continue
        
        print("Processing CSV file:", csv_file_path)
        
        # open the CSV file and read its contents
        with open(csv_file_path, newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter='\t', lineterminator='\0')
            next(csvreader) # skip the header row
    
            # iterate over each row in the CSV file
            for row in csvreader:
                # check if the row has enough columns
                if len(row) < 1:
                    print("Skipping row with not enough columns:", row)
                    continue

                # extract temperature values
                data = arr = row[0].split(',')
                tmp_str = data[24].replace('"', '')
                quality_code = int(data[25].replace('"', ''))
                temp = float(tmp_str) / 10;

                cur_latitude = float(data[3].replace('"', ''))
                cur_longitude = float(data[4].replace('"', ''))
                cur_elevation = float(data[5].replace('"', ''))

                #Check if the temperature is erroneous
                if(quality_code == 3):
                    continue;

                # extract date values
                date_str = data[1].replace('"', '')
                date_obj = get_date_obj(date_str)
                date_key = str(date_obj.month) + "-" + str(date_obj.day)

                # find temperature change between this day and the last
                if((last_temp == 9999)):
                    change = 0;
                else:
                    change = temp - last_temp

                # replace old last values
                last_date_key = date_key
                last_temp = temp

                # calculate the temperature change from the previous day, if available
                if date_key in daily_averages:
                    prev_total_change_str, prev_lat, prev_long, prev_elev, prev_count = daily_averages[date_key]
                    prev_total_change = float(prev_total_change_str)
                    #print("Prev total: ", prev_total_change)
                    total_change = change + prev_total_change
                    total_latitude = prev_lat + cur_latitude
                    total_longitude = prev_long + cur_longitude
                    total_elevation = prev_elev + cur_elevation
                    count = prev_count + 1
                else:
                    total_change = 0
                    total_latitude = cur_latitude
                    total_longitude = cur_longitude
                    total_elevation = cur_elevation
                    count = 1
                
                # update the daily average temperature change for the current date
                daily_averages[date_key] = (total_change, total_latitude, total_longitude, total_elevation, count)
        
        # after processing the first CSV file
        # break
    
# create the output directory if it doesn't exist
output_dir = "averages"
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

# write the daily average temperature changes to a new CSV file
output_filename = "average.csv";
output_filepath = os.path.join(output_dir, output_filename)

with open(output_filepath, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["Month-Day", "Average Temperature Change", "Midpoint Latitude", "Midpoint Longitude", "Avg Elevation", "Count"])
    for date_ky, (total_change, laditude, longitude, elevation, count) in sorted(daily_averages.items()):
        avg_tmp_change = float(total_change) / count
        avg_latitude = laditude / count
        avg_longitude = longitude / count
        avg_elevation = elevation / count
        csvwriter.writerow([date_ky, avg_tmp_change, avg_latitude, avg_longitude, avg_elevation, count])
