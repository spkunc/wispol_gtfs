import time
import csv
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def get_gps_coordinates(stop_name, max_results=5):
    try:
        geolocator = Nominatim(user_agent="bus_stop_locator")
        locations = geolocator.geocode(stop_name, exactly_one=False, limit=max_results)
        if locations:
            return [(location.latitude, location.longitude) for location in locations]
    except GeocoderTimedOut:
        return get_gps_coordinates(stop_name, max_results)
    return None

def fetch_bus_stops_coordinates(bus_stops, max_results=5):
    all_coordinates = {}
    for stop in bus_stops:
        coords = get_gps_coordinates(stop, max_results)
        if coords:
            all_coordinates[stop] = coords
        time.sleep(1)  # Add delay to avoid overwhelming the API
    return all_coordinates

def write_to_gtfs_format(bus_stops_coordinates, output_file='stops.txt'):
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 'location_type'])
        
        stop_id = 1
        for stop_name, locations in bus_stops_coordinates.items():
            if locations:
                # First location is considered as the station
                station_lat, station_lon = locations[0]
                writer.writerow([stop_id, stop_name, station_lat, station_lon, 1])
                stop_id += 1

                # Remaining locations are considered stops
                for lat, lon in locations[1:]:
                    writer.writerow([stop_id, stop_name + " (Stop)", lat, lon, 0])
                    stop_id += 1

def load_bus_stops_from_csv(input_file):
    bus_stops = []
    with open(input_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            bus_stops.append(row['stop_name'])
    return bus_stops

# Load bus stops from CSV file
bus_stops = load_bus_stops_from_csv('bus_stops_names.csv')

# Fetch coordinates and write to GTFS stops.txt file
coordinates = fetch_bus_stops_coordinates(bus_stops)
write_to_gtfs_format(coordinates)

print("GTFS stops.txt file has been generated.")
