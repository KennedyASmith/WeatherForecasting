import random
import math
import csv
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
import PySimpleGUI as sg
from geopy.distance import geodesic

########################################################################
#
#   Project: Weather Forecasting GUI
#
#   Author: Kennedy Smith
#   Class: CS458
#   Email: kennedy.smith@yale.edu
#
#   Acknowledgements:
#
#   1) The weather data used in this project is provided by the 
#   National Centers for Environmental Information (NCEI https://www.ncei.noaa.gov/).
#
#   2) This script also uses data from the GeoNames public API (http://www.geonames.org).
#   GeoNames is a free geographic database that provides
#   data and web services for place names, coordinates, and other
#   geographic information.
#       
########################################################################

# Files & Folders
WEATHER_DATA_FOLDER = 'weather_database'
ZIP_CODE_FILE = 'zip_codes.csv'
ELEVATION_FILE = 'elevations.csv'

# Constants
AVG_ELR = -6.5  # Global average environmental lapse rate in °C/km
DISTANCE_FACTOR = 0.003  # Change in temperature per kilometer from equator (global average)
REFERENCE_ALTITUDE = 0 # Reference altitude in meters (sea level)

def predict_temperature(user_latitude, user_longitude, current_temp, current_day, current_weather_state):
    print(f"Calculating temperature prediction for {current_day} at ({user_latitude}, {user_longitude})")
    # Find elevation from user latitude and longitude
    elevation = get_elevation(user_latitude, user_longitude)
    print(f"Elevation at ({user_latitude}, {user_longitude}): {elevation} meters")

    # Convert types
    user_latitude = float(user_latitude)
    user_longitude = float(user_longitude)

    # Import the weather data into a pandas DataFrame
    weather_data = pd.read_csv('averages/average.csv')

    # Split the user_date string into month and day
    month, day = current_day.split('-')
    user_month_day = f'{int(month)}-{int(day)}'

    # Filter the DataFrame to only include the rows that correspond to the user's date
    filtered_data = weather_data.loc[weather_data['Month-Day'] == user_month_day]
    average_temperature_change = filtered_data['Average Temperature Change'].mean() # Calculate the average temperature for the filtered rows
    count = filtered_data['Count'].mean() # Calculate the average temperature for the filtered rows

    print(f"First, we will find the global average temperature change for {user_month_day} through reference of data gathered through NCEI historical databases. This data is averaged from over {count} sources, from weather stations around the world.")
    print(f"The average global temperature change for {user_month_day}: {average_temperature_change}°C")

    midpoint_latitude = filtered_data['Midpoint Latitude'].iloc[0] # Midpoint coordinates = average lat/longitude 
    midpoint_longitude = filtered_data['Midpoint Longitude'].iloc[0]

    delta_z = elevation - REFERENCE_ALTITUDE
    delta_T_due_to_elevation = AVG_ELR * (delta_z / 1000)

    print(f"Next, we need calculate how much the altitude at {user_latitude}, {user_longitude} affects the temperature change.")
    print(f"Each estimated temp change is associated with a midpoint latitude and longitude value for all stations that contributed to the average. For this particular day, that midpoint latitude is {midpoint_latitude} and {midpoint_longitude}")
    print(f"The temperature decreases with increasing altitude at a rate known as the environmental lapse rate (ELR). ")

    # Adjust predicted temperature change based on elevation
    average_temperature_change = average_temperature_change - delta_T_due_to_elevation

    print(f"Therefore, we can estimate the temperature change due to elevation by multiplying the average ELR ({AVG_ELR}) by the difference in elevation from the reference altitude (sea level)({delta_z:.2f}°C) to arrive at {average_temperature_change:.2f}°C")

    # Calculation of distance between two locations using Haversine formula
    radius = 6371  # Radius of the earth in kilometers
    delta_latitude = math.radians(user_latitude - midpoint_latitude)
    delta_longitude = math.radians(user_longitude - midpoint_longitude)
    a = (math.sin(delta_latitude / 2) ** 2
        + math.cos(math.radians(midpoint_latitude)) * math.cos(math.radians(user_latitude))
        * math.sin(delta_longitude / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = radius * c

    print(f"It is important to note that the calculated change in temperature at ({midpoint_latitude}, {midpoint_longitude}) is {distance:.2f} km from your location ({user_latitude}, {user_longitude}). This means actual temperature change will likely vary based on local geographical differences.")

    # Calculation of temperature change due to distance from equator using inverse square law of radiation
    # The amount of solar radiation that reaches the earth's surface varies with latitude, with more radiation hitting the equator than the poles. 
    delta_T_due_to_distance = -DISTANCE_FACTOR * (math.sin(math.radians(user_latitude)) ** 2)

    # Calculation of total temperature change
    delta_T_total = delta_T_due_to_elevation + delta_T_due_to_distance

    # Adjust predicted temperature change based on elevation and distance from equator
    average_temperature_change = (average_temperature_change - delta_T_total) * 0.10

    print(f"The amount of solar radiation that reaches the earth's surface varies with latitude by a factor of {DISTANCE_FACTOR}° per kilometer, with more radiation hitting the equator than the poles. Therefore, the temperature change due to distance from equator: {delta_T_due_to_distance}°C")

    print("Next, we have to account for the current weather state at your location:")
    if current_weather_state == 'Clear':
        average_temperature_change += 0.0
        print("The current weather state is Clear. This weather state will likely have no effect on the temperature tomorrow.")
    elif current_weather_state == 'Cloudy':
        average_temperature_change -= 0.2
        print("The current weather state is Cloudy, which will decrease the temperature very slightly.")
    elif current_weather_state == 'Rainy':
        average_temperature_change -= 0.5
        print("The current weather state is Rainy, which will decrease the temperature tomorrow slightly.")
    elif current_weather_state == 'Snowy':
        average_temperature_change -= 1.0
        print("The current weather state is Snowy, which will decrease the temperature tomorrow.")

    final_prediction = current_temp + average_temperature_change
    print(f"Therefore, the final predicted temperature is {final_prediction:.2f}°C.")
    return final_prediction

def get_elevation(lat, lon):
    with open(ELEVATION_FILE, newline='') as f:
        reader = csv.reader(f)
        next(reader)  # skip header row
        for row in reader:
            if row[0] == f'{lat},{lon}':
                return float(row[1])
    # If no matching row was found, return None
    return None

def choose_weather(current_weather, elevation, temperature):
    # Initialize weather choices
    weather_choices = ['Clear', 'Cloudy', 'Rainy', 'Snowy']
    
    # Set default probability of each weather type
    clear_prob = 0.6
    cloudy_prob = 0.25
    rainy_prob = 0.1
    snowy_prob = 0.05
    
    # Adjust probabilities based on current weather
    if current_weather == 'Clear':
        cloudy_prob += 0.1
        rainy_prob += 0.05
        snowy_prob += 0.025
    elif current_weather == 'Cloudy':
        clear_prob += 0.04
        rainy_prob += 0.05
        snowy_prob += 0.05
    elif current_weather == 'Rainy':
        clear_prob += 0.025
        cloudy_prob += 0.05
        snowy_prob += 0.025
        rainy_prob += 0.025
    elif current_weather == 'Snowy':
        clear_prob += 0.01
        cloudy_prob += 0.025
        rainy_prob += 0.05
        snowy_prob += 0.1
    
    # Adjust probabilities based on elevation
    if elevation > 2000:
        snowy_prob += 0.1
        rainy_prob += 0.05
        clear_prob -= 0.05
        explanation = "The elevation is high, which increases the likelihood of snow and decreases the likelihood of clear weather."
    elif elevation > 1000:
        snowy_prob += 0.05
        rainy_prob += 0.025
        clear_prob -= 0.025
        explanation = "The elevation is moderate, which increases the likelihood of snow and decreases the likelihood of clear weather."
    else:
        explanation = "The elevation is low, so the weather is not affected much by it."
    
    # Adjust probabilities based on temperature
    if temperature < 0:
        snowy_prob += 0.1
        rainy_prob = 0.0
        clear_prob -= 0.05
        explanation += " The temperature is below freezing, so there is a high chance of snow and no chance of rain."
    elif temperature > 0:
        snowy_prob = 0.0
        explanation += " The temperature is above freezing, so there is no chance of snow."
    elif temperature < 10:
        rainy_prob += 0.025
        clear_prob -= 0.025
        explanation += " The temperature is cool, which increases the likelihood of rain and decreases the likelihood of clear weather."
    else:
        explanation += " The temperature is mild, so the weather is not affected much by it."
    
    # Choose the next day's weather
    weather_probs = [clear_prob, cloudy_prob, rainy_prob, snowy_prob]
    chosen_weather = random.choices(weather_choices, weights=weather_probs)[0]
    
    explanation += f" The predicted weather for tomorrow is {chosen_weather}."
    print(explanation)
    return chosen_weather

def get_coordinates(zip_code):
    # Open the CSV file
    with open(ZIP_CODE_FILE, newline='') as csvfile:
        # Create a CSV reader
        reader = csv.DictReader(csvfile)
        
        # Loop through each row in the CSV file
        for row in reader:
            # If the zip code in the current row matches the query zip code
            if row["ZIP"] == zip_code:
                # Extract the latitude and longitude from the row
                latitude = row["LAT"]
                longitude = row["LNG"]
                return latitude, longitude
    return "Invalid Zip", "Invalid Zip"


def main():
    # Get the current system date and format it as yyyy-mm-dd
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Use the default theme
    sg.theme('Default 1')

    # Set up GUI layout
    layout = [
        [sg.Text('Enter current temperature (Celcius):'), sg.Input(key='current_temp')],
        [sg.Text('Enter your zip code:'), sg.Input(key='zip_c')],
        [sg.Text('Select current weather state:'), sg.Combo(['Clear', 'Cloudy', 'Rainy', 'Snowy'], key='current_weather', default_value='Clear')],
        [sg.Text('Select current day:'), sg.Text(current_date, key='c_day'),
        sg.In(key='date_selected', enable_events=True, visible=False, default_text=current_date), 
        sg.CalendarButton('Select', target='date_selected', format='%Y-%m-%d', key='current_day')],
        [sg.Button('Predict')],
        [sg.Table(values=[], headings=['Date', 'Temperature', 'Weather'], auto_size_columns=False, num_rows=7, key='temp_table')],
        [(sg.Text('Latitude: '), sg.Text('---', key='lat')), (sg.Text('Longitude: '), sg.Text('---', key='long'))]
    ]
    window = sg.Window('Temperature Forecast', layout)
    
    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break

        if event == 'date_selected':
            selected_date = values['date_selected']
            window['c_day'].update(f'{selected_date}')  # Update the text next to the calendar button with the selected date
            window.Refresh()  # Force the window to update
            continue;

        if event == 'Predict':
            current_temp = values['current_temp']
            if current_temp == '':
                # If the user hasn't entered a temperature, display an error message
                sg.popup('Please enter a temperature', title='Error')
                continue
            current_temp = float(current_temp)
            current_zip = values['zip_c']
            latitude, longitude = get_coordinates(current_zip)
            if current_zip == '':
                # If the user hasn't entered a temperature, display an error message
                sg.popup('Please enter a zip code.', title='Error')
                continue
            if latitude == 'Invalid Zip':
                # If the user hasn't entered a temperature, display an error message
                sg.popup('Please enter a valid zip code.', title='Error')
                continue

            current_day = values['date_selected']
            if current_day == '':
                # If the user hasn't selected a date, display an error message
                sg.popup('Please select a date', title='Error')
                continue

            current_weather = values['current_weather']

            window['lat'].update(values)
            window['lat'].update(f'{latitude}')
            window['long'].update(f'{longitude}')

            # Clear any existing data in the table
            table_data = [['', '', ''] for _ in range(7)]
            window['temp_table'].update(values=table_data)

            date_object = datetime.strptime(current_day, '%Y-%m-%d')
            # Loop over the next 6 days and predict the temperature
            for i in range(1, 7):

                # Calculate the date for the current iteration
                date = (date_object + timedelta(days=i))
                date_string = date.strftime('%m-%d')

                print (f"\n\n\n --------- Forecast for Day: {date_string} ---------")

                # Predict the temperature for the current date
                temperature = predict_temperature(latitude, longitude, current_temp, date_string, current_weather)
                elevation = get_elevation(latitude, longitude)
                print("For tomorrow's potential weather patterns: ")
                current_weather = choose_weather(current_weather, elevation, current_temp)
                current_temp = temperature

                # Add the date and temperature to the table data
                table_data[i - 1][0] = date.strftime('%Y-%m-%d')
                table_data[i - 1][1] = f'{temperature:.2f}°'
                table_data[i - 1][2] = f'{current_weather}°'
            
            window['temp_table'].update
            window['temp_table'].update(values=table_data)
            #table_data = [[date.strftime('%Y-%m-%d'), str(temp) + '°'] for date, temp in temp_predictions]
            #window['temp_table'].update(values=table_data)]
            
    window.close()

if __name__ == '__main__':
    main()
