# Annotator

## Table of Contents
- [Installation and Run](#installation-and-run)
- [App Overview](#app-overview)
  - [Side Bar](#side-bar)
  - [Street View Display](#street-view-display)
  - [Right Side Buttons](#right-side-buttons)
  - [Aerial View Map](#aerial-view-map)
  - [Tutorial](#tutorial)

## Installation and Run

```bash
# Open a terminal and clone the repository
git clone https://github.com/Frozensun47/Street-View-Annotator.git
# Change directory to the cloned repository
cd Street-View-Annotator

# If you have Conda installed, create and activate the environment
# If you don't want to use Conda, skip these two lines
conda create --name annotator python=3.10.10
conda activate annotator

# Install dependencies from requirements.txt
pip install -r requirements.txt

# To Run the annotator
python -m gui
```

# App Overview

The app consists of three main components:

## Side Bar
On the left, there is a side bar containing stroke width and color selection tools, and a display area for visualizing and editing the coordinates of points being plotted.

## Street View Display

<img src="https://github.com/Frozensun47/Street-View-Annotator/blob/main/utils/Readme/street_view_marker.gif" alt="App Overview GIF" width="400" height="200">

In the middle, there is the street view display with functionalities:

- **Navigate:** Left-click inside the street view display area and move the mouse.
- **Add Markers:** Right-click to add markers.

## Right Side Buttons
On the right side, there are various buttons:

- **Text Input Box:** Paste latitude and longitude for quick marker placement.
- **Update Map:** Press to update the map with the entered coordinates.
- **Remove Marker:** Removes all markers on the map.
- **Remove Polygon:** Removes all drawn polygons on the map.
- **Get Polygon:** Draws polygons on the aerial view map corresponding to markers in the street view map.
- **Get Panorama Image:** Fetches the panorama of the last placed marker on the map.

## Aerial View Map
Functionalities:

- Left-click and drag to move the map.
- Scroll to zoom in and out.
- Left-click to place a marker.
- Double-click a marker to remove it.
- Click once on a marker to get its latitude and longitude.
- Use + and - symbols to zoom in and out.

## Tutorial
![App Overview Image](utils/Readme/App_full_image.png)

After opening the app, follow these steps:

1. Go to the aerial view map and position it.
2. Left-click to drop a marker on the aerial view map.
3. Click the "Get Panorama Image" button to load the corresponding street view panorama.
4. In the street view display, left-click, move the mouse, and right-click to drop markers.
5. After dropping markers, click the "Get Polygon" button to show polygons on the map.

Feel free to adjust the headings and content as needed.
