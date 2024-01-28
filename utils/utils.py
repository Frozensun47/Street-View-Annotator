from math import radians, sin, cos, degrees

def get_new_coords(lat, lon, distance, direction):
    earth_radius = 6378137 #meters

    # Convert latitude and longitude from degrees to radians
    lat_rad = radians(lat)
    lon_rad = radians(lon)

    # Convert direction from degrees to radians
    direction_rad = radians(direction)

    # Calculate new latitude
    new_lat_rad = lat_rad + (distance / earth_radius) * cos(direction_rad)

    # Calculate new longitude
    new_lon_rad = lon_rad + (distance / earth_radius) * sin(direction_rad) / cos(lat_rad)

    # Convert new latitude and longitude back to degrees
    new_lat = degrees(new_lat_rad)
    new_lon = degrees(new_lon_rad)

    return new_lat, new_lon