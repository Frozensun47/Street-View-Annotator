from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import  QHBoxLayout, QWidget
from PyQt5.QtWidgets import QApplication, QMainWindow
import numpy as np
from utils.processor import *
from utils.sidebar import SidebarWidget
from utils.map import FoliumWidget
from utils.streetview import GLWidget
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Street View Annotator")
        self.setWindowIcon(QtGui.QIcon("utils\icon.png"))
        # self.image = 'utils/demo_image.jpg'
        # self.depth = 'utils/demo_depth.npy'
        self.latitude ,self.longitude = 30.71979998667062, 76.72142742674824
        self.clipboard_lat, self.clipboard_lng = 30.71979998667062, 76.72142742674824
        self.image, self.depth, self.heading,self.latitude ,self.longitude = process_location(self.latitude ,self.longitude) # comment for offline
        # self.heading = 0 # uncomment for offline
        # self.image = Image.open('utils/demo_image.jpg') # uncomment for offline
        # self.depth = np.load('utils/demo_depth.npy') # uncomment for offline
        self.sidebar_widget=None
        self.folium_widget = None
        self.create_gl_widget()
        self.sidebar_widget = SidebarWidget(self.gl_widget)
        self.gl_widget.sidebar_widget = self.sidebar_widget
        self.folium_widget = FoliumWidget(self,self.gl_widget)
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.on_clipboard_change)

        self.setup_ui()

    def setup_ui(self):
        self.central_layout = QHBoxLayout()
        self.central_layout.addWidget(self.sidebar_widget)
        self.central_layout.addWidget(self.gl_widget, stretch=1) 
        self.central_layout.addWidget(self.folium_widget, stretch=1)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.central_layout)
        self.setCentralWidget(self.central_widget)

    def create_gl_widget(self):
        self.gl_widget = GLWidget(self, image=self.image, depth=self.depth,heading = self.heading,
                                  sidebar_widget=None,lat=self.latitude ,lng=self.longitude)
        self.gl_widget.sidebar_widget = self.sidebar_widget
        if self.folium_widget is not None and self.sidebar_widget is not None:
            self.folium_widget.gl_widget = self.gl_widget
            self.sidebar_widget.gl_widget = self.gl_widget
    def get_panorama(self):
        self.image, self.depth, self.heading,self.latitude ,self.longitude = process_location(self.clipboard_lat, self.clipboard_lng)

        # Remove and recreate GL widget
        self.central_layout.removeWidget(self.gl_widget)
        self.gl_widget.deleteLater()
        self.create_gl_widget()
        # Insert the updated GL widget back into the layout
        self.centralWidget().layout().insertWidget(1, self.gl_widget, stretch=1)

        # Update Folium widget with the new markers
        self.folium_widget.markers.append((self.clipboard_lat, self.clipboard_lng))
    def on_clipboard_change(self):
        mime_data = self.clipboard.mimeData()

        if mime_data.hasText():
            clipboard_text = mime_data.text()
            try:
                self.clipboard_lat, self.clipboard_lng = eval(clipboard_text)
            except:
                pass

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    offset = 20
    window.setGeometry(0 + offset, 20 + offset, 1300 + offset, 900 + offset)
    window.show()
    app.exec_()
