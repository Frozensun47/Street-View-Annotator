from math import radians, sin, cos, degrees
import os ,base64
from PyQt5.QtWebEngineWidgets import QWebEngineView
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

def save_image(image, lat, lng, fov_zoom=90, pitch=0, yaw=0,street=False,folder_path='Output'):
    ''' 
        - Latitude
        - Longitude
        - Aerial (0) / Street-view (1)
        - Zoom Level (for aerial currently -1) / FOV (for street view)
        - Direction/Pitch (-1 for Aerial)
        - Yaw (-1 for Aerial)
        - Panorama (0) / Current-View (1) / Aerial View (-1)
    '''
    if street :
        filename = f'{lat},{lng},1,{fov_zoom},{pitch},{yaw},{0}'
        encoded_filename = base64.b64encode(filename.encode()).decode()
        full_path = os.path.join(folder_path, f'{encoded_filename}.png')
        image.save(full_path)
        print(f"Street-view Image saved as PNG")
    else:
        filename = f'{lat},{lng},0,-1,-1,-1,-1'
        encoded_filename = base64.b64encode(filename.encode()).decode()
        full_path = os.path.join(folder_path, f'{encoded_filename}.png')

        image.grab().save(full_path)
        print(f"Map saved as PNG")