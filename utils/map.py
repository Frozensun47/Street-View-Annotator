from PyQt5.QtWidgets import QLineEdit,QVBoxLayout, QHBoxLayout, QLabel, QSlider, QColorDialog, QPushButton, QListWidget, QListWidgetItem, QInputDialog, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from utils.processor import *


class FoliumWidget(QWidget):
    def __init__(self,main_window,gl_widget):
        super().__init__()
        self.gl_widget = gl_widget
        self.main_window = main_window
        self.markers = []
        self.Polygons = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        #for entering coordinates
        self.coord_input = QLineEdit(self)
        layout.addWidget(self.coord_input)

        # to trigger the coordinate update
        update_button = QPushButton("Update Map", self)
        update_button.clicked.connect(self.update_map_with_input)
        layout.addWidget(update_button)

        #to trigger marker removal
        remove_button = QPushButton("Remove Markers", self)
        remove_button.clicked.connect(self.remove_markers)
        layout.addWidget(remove_button)

        #to trigger polygon drawing
        polygon_button = QPushButton("Get Polygon", self)
        polygon_button.clicked.connect(self.get_polygon)
        layout.addWidget(polygon_button)

        #to trigger marker removal
        remove_polygons_button = QPushButton("Remove Polygons", self)
        remove_polygons_button.clicked.connect(self.remove_Polygons)
        layout.addWidget(remove_polygons_button)

        panorama_button = QPushButton("Get Panorama", self)
        panorama_button.clicked.connect(self.main_window.get_panorama)
        layout.addWidget(panorama_button)

        #to display the Folium map
        web_view = QWebEngineView()
        web_view.setHtml(open("utils\map_final.html").read())
        layout.addWidget(web_view)

    def update_map_with_input(self):
        coords_text = self.coord_input.text()
        try:
            lat, lng = map(float, coords_text.split(','))
            self.add_marker(lat,lng)
        except ValueError:
            print("Invalid coordinates format. Please enter as 'latitude, longitude'.")

    def add_marker(self,lat,lng):
        update_script = f"updateMapWithCoordinates({lat}, {lng});"
        self.findChild(QWebEngineView).page().runJavaScript(update_script)
        self.markers.append((lat, lng))

    def remove_markers(self):
        remove_script = "removeMarkers();"
        self.findChild(QWebEngineView).page().runJavaScript(remove_script)
        self.markers = []
    
    def remove_Polygons(self):
        remove_script = "removePolygons();"
        self.findChild(QWebEngineView).page().runJavaScript(remove_script)
        self.Polygons = []

    def get_polygon(self):
        if len(self.gl_widget.coordinates_stack) >= 3:
            polygon_vertices = ",".join([f"[{lat},{lng}]" for lat, lng in self.gl_widget.coordinates_stack])
            draw_polygon_script = f"drawPolygon([{polygon_vertices}]);"
            self.findChild(QWebEngineView).page().runJavaScript(draw_polygon_script)
            self.gl_widget.coordinates_stack=[]
        else:
            print("At least 3 markers are required to draw a polygon.")