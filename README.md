
This project is a GUI-based weather forecasting application. It uses historical weather data from the National Centers for Environmental Information (NCEI) and elevation data from the GeoNames public API to predict the temperature for the next six days at a given location. The application also predicts the next day's weather condition (Clear, Cloudy, Rainy or Snowy) based on current weather state, elevation, and temperature. ``All explanations for decisions made by the application are printed to the console.``

The application is written in Python 3.10 and uses the following external libraries:

- random
- math
- csv
- datetime
- pandas
- numpy
- PySimpleGUI
- geopy

## Files and Folders
The project includes the following files and folders:

- **weather_database**: A folder containing data files for each weather station. 
- **data_collector.py** Averages temperature data from *weather_database.* to create *average.csv*
- **average.csv**: The average global data used for temperature prediction
- **zip_codes.csv**: A CSV file containing a mapping of latitude and longitude data for zip codes
- **elevation_collector.py** Uses *GeoNames API* to map coordinates to elevation to create *elevations.csv*
- **elevations.csv**: A CSV file containing elevation data for geographic coordinates of zip codes

## Constants
The following constants are used in the program:

- **AVG_ELR**: The global average environmental lapse rate in °C/km
- **DISTANCE_FACTOR**: The change in temperature per kilometer from the equator (global average)
- **REFERENCE_ALTITUDE**: The reference altitude in meters (sea level)

## Functions

- `predict_temperature(user_latitude, user_longitude, current_temp, current_day, current_weather_state)`: Calculates the predicted temperature for a given location and date
- `get_elevation(lat, lon)`: Returns the elevation for a given latitude and longitude
- `choose_weather(current_weather, elevation, temperature)`: Chooses the next day's weather condition based on the current weather, elevation, and temperature
- `get_coordinates(zip_code)`: Returns the latitude and longitude for a given zip code
- `main()`: The main function that runs the GUI and coordinates the temperature and weather prediction

## Usage
To use the program, run the main() function in weather.py.

A PySimpleGUI window will open, prompting the user to enter the current temperature, zip code, and current weather state. The user can also select the current day using a calendar widget. Clicking the "Predict" button will generate the predicted temperature and weather for the next six days. The predicted temperature and weather data are displayed in a table below the "Predict" button. **All explanations for the weather prediction are printed to the console.**

## Example Output
``` 
 --------- Forecast for Day: 05-15 ---------
Calculating temperature prediction for 05-15 at (44.940425,  -93.292639)
Elevation at (44.940425,  -93.292639): 260.0 meters

First, we will find the global average temperature change for 5-15 through reference of data gathered through NCEI historical databases. This particular data is averaged over 70438 sources through weather stations from around the world.
The average global temperature change for 5-15: -0.07861523609416°C
Next, we need calculate how much the altitude at 44.940425, -93.292639 affects the temperature change.
Each estimated temp change is associated with a midpoint latitude and longitude value for all stations that contributed to the average. For this particular day, that midpoint latitude is 36.37661362412288 and -38.21404134349831
The temperature decreases with increasing altitude at a rate known as the environmental lapse rate (ELR). 
Therefore, we can estimate the temperature change due to elevation by multiplying the average ELR (-6.5) by the difference in elevation from the reference altitude to arrive at 1.61°C
It is important to note that the calculated change in temperature at (36.37661362412288, -38.21404134349831) is 4650.71 km from your location (44.940425, -93.292639). This means actual temperature change will likely vary based on local geographical differences.
The amount of solar radiation that reaches the earth's surface varies with latitude by a factor of 0.003° per kilometer, with more radiation hitting the equator than the poles. Therefore, the temperature change due to distance from equator: -0.001496°C
Next, we have to account for the current weather state at your location:
The current weather state is Clear. This weather state will likely have no effect on the temperature tomorrow.
Therefore, the final predicted temperature is 22.87°C.
For tomorrow's potential weather patterns: 
The elevation is low, so the weather is not affected much by it. The temperature is above freezing, so there is no chance of snow. The predicted weather for tomorrow is Clear.
```

## Acknowledgements 
The following APIs were used for data throughout this project:
- National Centers for Environmental Information (NCEI https://www.ncei.noaa.gov/) for weather data and constants.
- GeoNames (http://www.geonames.org) for elevation, coordinates, and other geographic information.
