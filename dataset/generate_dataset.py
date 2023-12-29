import numpy as np
import pandas as pd
import random
from geopy.distance import great_circle
from math import atan2, radians, degrees, sin, cos, asin, sqrt
from datetime import datetime

# Load the airports data from CSV
airports_df = pd.read_csv('airports.csv')
airlines_df = pd.read_csv('airlines.csv')
aircraft_df = pd.read_csv('aircraft.csv')

# Data-generator parameters # generates 1,000,000 records
num_airports = 300
num_airlines = 30
num_aircraft = 20
num_flights = 1000 
data_points_per_flight = 1000
flight_date = datetime(2023, 12, 14)

# Pick random airports
iata_codes = airports_df['apt_iata_code'].sample(n=num_airports, random_state=1).tolist()
# ["DOH", "FRA", "LHR", "JFK", "CDG", "DXB", "AMS", "SIN", "HKG", "ICN", "NRT", "LAX", "SFO", "ORD", "MIA"]  # Replace with your list of IATA codes
# Pick random airlines
airline_codes = airlines_df['airline_code'].sample(n=num_airlines, random_state=1).to_list()
# ["QR", "BA", "LH", "AF", "EK", "KL", "SQ", "CX", "KE", "JL", "AA", "UA", "DL", "SW", "RY"]
# Pick random aircraft types
aircraft_types = aircraft_df['ac_type'].sample(n=num_aircraft, random_state=1).to_list()
# ["Boeing 777", "Airbus A320", "Airbus A330", "Boeing 737", "Airbus A380", "Boeing 787"]  # Example list of aircraft types

# Function to get coordinates for a single airport
def get_airport_coordinates(iata_code):
    airport = airports_df[airports_df['apt_iata_code'] == iata_code]
    if not airport.empty:
        lat = airport.iloc[0]['latitude']
        lon = airport.iloc[0]['longitude']
        return {iata_code: (lat, lon)}
    else:
        return {iata_code: (None, None)}

# Function to get coordinates for multiple airports
def get_airports_coordinates(iata_codes):
    coordinates_dict = {}
    for code in iata_codes:
        coordinates_dict.update(get_airport_coordinates(code))
    return coordinates_dict

all_coordinates = get_airports_coordinates(iata_codes)

# The function to calculate the heading:
def calculate_bearing(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Calculate heading
    x = atan2(sin(lon2 - lon1) * cos(lat2), cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(lon2 - lon1))
    bearing = (degrees(x) + 360) % 360  # Normalize to 0-360
    return bearing

def calculate_distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of Earth in kilometers
    return c * r

def interpolate_coordinates(lat1, lon1, lat2, lon2, steps):
    lats = np.linspace(lat1, lat2, steps)
    lons = np.linspace(lon1, lon2, steps)
    return list(zip(lats, lons))

def create_realistic_flight_dataset(dep_stn, arr_stn, flight_number, aircraft_type, num_rows, flight_date, all_coordinates):
    dep_lat, dep_lon = all_coordinates.get(dep_stn, (None, None))
    arr_lat, arr_lon = all_coordinates.get(arr_stn, (None, None))

    if None in (dep_lat, dep_lon, arr_lat, arr_lon):
        raise ValueError("Invalid IATA code or coordinates not found.")

    # Generate waypoints
    waypoints = interpolate_coordinates(dep_lat, dep_lon, arr_lat, arr_lon, num_rows)
    latitudes, longitudes = zip(*waypoints)

    # Generate other flight data
    altitudes = np.linspace(3000, 35000, num_rows//2).tolist() + np.linspace(35000, 3000, num_rows//2).tolist()
    speeds = np.linspace(250, 550, num_rows//2).tolist() + np.linspace(550, 250, num_rows//2).tolist()
    timestamps = pd.date_range(flight_date, periods=num_rows, freq="1min")

    # Calculate headings
    headings = [calculate_bearing(latitudes[i], longitudes[i], latitudes[i+1], longitudes[i+1]) if i < num_rows - 1 else calculate_bearing(latitudes[i-1], longitudes[i-1], latitudes[i], longitudes[i]) for i in range(num_rows)]

    # Create the dataframe
    flight_data = pd.DataFrame({
        "timestamp": timestamps,
        "flight_number": flight_number,
        "ac_type": aircraft_type,
        "dep_stn": dep_stn,
        "arr_stn": arr_stn,
        "latitude": latitudes,
        "longitude": longitudes,
        "altitude": altitudes,
        "speed": speeds,
        "heading": headings,
    })
    return flight_data

# Creating the dataset for multiple flights
def create_full_dataset(num_flights, data_points_per_flight, flight_date, all_coordinates, airline_codes, aircraft_type="Boeing 777"):
    all_flights_data = pd.DataFrame()
    generated_flight_numbers = set()  # Set to keep track of generated flight numbers


    for _ in range(num_flights):
        # Randomly select departure and arrival airports
        dep_stn, arr_stn = random.sample(list(all_coordinates.keys()), 2)
        # Generate a unique flight number and randomly select an aircraft type
        # Ensure unique flight number
        while True:
            flight_number = random.choice(airline_codes) + str(random.randint(1, 8000)).zfill(3)
            if flight_number not in generated_flight_numbers:
                generated_flight_numbers.add(flight_number)
                break

        aircraft_type = random.choice(aircraft_types)

        # Create dataset for this flight
        flight_data = create_realistic_flight_dataset(dep_stn, arr_stn, flight_number, aircraft_type, data_points_per_flight, flight_date, all_coordinates)
        
        # Append to the full dataset
        all_flights_data = pd.concat([all_flights_data, flight_data], ignore_index=True)

    return all_flights_data

# Generate the full dataset
full_dataset = create_full_dataset(num_flights, data_points_per_flight, flight_date, all_coordinates, airline_codes)
# print(full_dataset.head(30))

# Sort the dataset by timestamp and then by flight number
sorted_dataset = full_dataset.sort_values(by=['timestamp', 'flight_number'])

# Saving the sorted dataset to a CSV file on the mounted shared volume
sorted_dataset.to_csv('/shared_data/ADSB_dataset.csv', mode='w', index=False)