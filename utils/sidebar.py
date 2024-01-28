from PyQt5 import QtWidgets, QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QSlider, QColorDialog, QPushButton, QListWidget, QListWidgetItem, QInputDialog

from utils.processor import *


class SidebarWidget(QtWidgets.QWidget):
    def __init__(self, gl_widget):
        super().__init__()
        self.gl_widget = gl_widget
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        #stroke slider
        stroke_label = QLabel("Stroke Width:")
        self.stroke_slider = QSlider(QtCore.Qt.Horizontal)
        self.stroke_slider.setMinimum(10)
        self.stroke_slider.setMaximum(90)
        self.stroke_slider.setValue(self.gl_widget.stroke_width)
        self.stroke_slider.valueChanged.connect(self.on_stroke_width_change)
        self.stroke_label_value = QLabel(f"Current Width: {self.gl_widget.stroke_width}")

        # Color Palette
        color_label = QLabel("Color:")
        self.color_button = QPushButton("Choose Color")
        self.color_button.clicked.connect(self.on_color_button_click)

        # Coordinates List Widget
        self.coordinates_list_widget = QListWidget()
        self.coordinates_list_widget.setSortingEnabled(False)

        layout.addWidget(stroke_label)
        layout.addWidget(self.stroke_slider)
        layout.addWidget(self.stroke_label_value)
        layout.addWidget(color_label)
        layout.addWidget(self.color_button)
        layout.addWidget(self.coordinates_list_widget)
        self.setLayout(layout)

    def on_stroke_width_change(self, value):
        self.stroke_label_value.setText(f"Current Width: {value}")
        self.gl_widget.set_stroke_width(value)

    def on_color_button_click(self):
        color = QColorDialog.getColor()
        self.gl_widget.set_stroke_color(color.getRgb()[:-1])
        self.color_button.setStyleSheet(f"background-color: {color.name()};")

    def update_coordinates_label(self):
        self.update_coordinates_list()

    def update_coordinates_list(self, First=True):
        self.coordinates_list_widget.clear()
        for x, y in self.gl_widget.coordinates_stack:
            item = QListWidgetItem(f"({x}, {y})")
            self.coordinates_list_widget.addItem(item)
        if First:
            self.coordinates_list_widget.itemDoubleClicked.connect(self.edit_coordinate)

    def edit_coordinate(self, item):
        current_text = item.text()
        menu = QtWidgets.QMenu(self)
        edit_action = menu.addAction("Edit Coordinate")
        delete_action = menu.addAction("Delete Coordinate")
        action = menu.exec_(QtGui.QCursor.pos())

        if action == edit_action:
            new_text, ok = QInputDialog.getText(self, "Edit Coordinate", "Enter new coordinate:", text=current_text)

            if ok:
                item.setText(new_text)

        elif action == delete_action:
            coordinates_text = current_text.strip("()")
            x, y = map(int, coordinates_text.split(", "))
            coordinate = (x, y)

            if coordinate in self.gl_widget.coordinates_stack:
                self.gl_widget.coordinates_stack.remove(coordinate)
                self.update_coordinates_list(First=False)
                pass