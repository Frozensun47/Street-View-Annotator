from OpenGL.GL import *
from OpenGL.GLU import *
import base64
import os
from PyQt5.QtOpenGL import QGLWidget
from PyQt5 import QtCore
from PIL import Image, ImageDraw
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QCursor
import math
import numpy as np
from utils.processor import *
from utils.utils import get_new_coords
class GLWidget(QGLWidget):
    def __init__(self, parent, sidebar_widget, image, depth, heading,lat,lng):
        super().__init__(parent)
        
        self.lat,self.lng = lat,lng
        self.image = image
        self.depth = depth
        self.image_width, self.image_height = self.image.size
        self.output_directory = 'Output'
        self.yaw = 270
        self.heading = heading
        self.pitch = 0
        self.prev_dx = 0
        self.prev_dy = 0
        self.fov = 90
        self.direction = 0
        self.moving = False
        
        self.coordinates_stack = []
        self.markers_stack = []
        
        self.sidebar_widget = sidebar_widget
        #street view params
        self.stroke_width = 25
        self.transparency = 50 #in range 0-100
        self.color = (255,0,0,128)
        #map params
        self.map_color = (255,0,0,128)
        self.map_transparency = 0.5 # in range 0-1
        self.map_color_name = 'Red'
    
    def initializeGL(self):
        glEnable(GL_TEXTURE_2D)
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.image_width, self.image_height, 0, GL_RGB, GL_UNSIGNED_BYTE, self.image.tobytes())
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        self.sphere = gluNewQuadric()
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(90, self.width() / self.height(), 0.1, 1000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glRotatef(self.pitch, 1, 0, 0)
        glRotatef(self.yaw, 0, 1, 0)
        glRotatef(90, 1, 0, 0)
        glRotatef(-90, 0, 0, 1)
        gluQuadricTexture(self.sphere, True)
        gluSphere(self.sphere, 1, 100, 100)
        glPopMatrix()

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.width() / self.height(), 0.1, 1000)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.handle_left_button_press(event)
        elif event.button() == QtCore.Qt.RightButton:
            self.handle_right_button_press(event)

    def handle_left_button_press(self, event):
        self.mouse_x, self.mouse_y = event.pos().x(), event.pos().y()
        self.moving = True

    def handle_right_button_press(self, event):
        self.mouse_x, self.mouse_y = event.pos().x(), event.pos().y()
        pixel_x, pixel_y = self.screen_to_pixel_coordinates()
        heading_offset = 0 - 270
        cal_yaw = (self.yaw - heading_offset) % 360
        cal_pitch = (self.pitch + 90) % 180
        image_pixel_x, image_pixel_y = self.calculate_image_pixel_coordinates(cal_yaw, cal_pitch, pixel_x, pixel_y)
        index_y, index_x = self.calculate_depth_indices(image_pixel_x, image_pixel_y)
        depth = self.depth[index_y][index_x]

        distance, self.direction = self.calculate_distance_and_direction(depth, cal_pitch, cal_yaw)

        if depth > 0 and distance > 0:
            print(f"depth = {depth}, Distance = {distance}, Heading = {self.heading}, Direction = {int(self.direction)}")
            lat, lng = self.calculate_new_coords(depth, self.direction)
            self.draw_point(image_pixel_x, image_pixel_y)
            self.markers_stack.append((image_pixel_x, image_pixel_y))
            self.coordinates_stack.append((lat, lng))
            self.sidebar_widget.update_coordinates_label()
        else:
            print("Inf")

    def calculate_distance_and_direction(self, depth, cal_pitch, cal_yaw):
        distance = depth * math.sin((180 - cal_pitch) / 360)
        direction = self.calculate_direction(cal_yaw)
        return distance, direction

    def screen_to_pixel_coordinates(self):
        pixel_x = int(self.mouse_x / self.width() * self.image_width)
        pixel_y = int((self.height() - self.mouse_y) / self.height() * self.image_height)
        return pixel_x, pixel_y

    def calculate_image_pixel_coordinates(self, cal_yaw, cal_pitch, pixel_x, pixel_y):
        image_pixel_x = cal_yaw * (self.image_width / 360)
        image_pixel_y = cal_pitch * (self.image_height / 180)
        return image_pixel_x, image_pixel_y

    def calculate_depth_indices(self, image_pixel_x, image_pixel_y):
        index_y = int(image_pixel_y * (self.depth.shape[0] / self.image_height))
        index_x = int(image_pixel_x * (self.depth.shape[1] / self.image_width)) * (-1)
        return index_y, index_x

    def calculate_distance(self, depth, cal_pitch):
        return depth * math.sin((180 - cal_pitch) / 360)

    def calculate_direction(self, cal_yaw):
        direction = (self.yaw) - 270 + self.heading
        if direction < 0:
            direction += 360
        return direction

    def calculate_new_coords(self, depth, direction):
        return get_new_coords(self.lat, self.lng, depth, int(direction))

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.moving = False
        elif event.button() == QtCore.Qt.RightButton:
            try:
                self.draw_polygon(self.markers_stack)
            except:
                print('more than markers required')

    def mouseMoveEvent(self, event):
        if self.moving:
            center_x = self.width() // 2
            center_y = self.height() // 2
            dx = event.pos().x() - center_x
            dy = event.pos().y() - center_y
            dx *= 0.1
            dy *= 0.1
            self.yaw += dx
            self.pitch += dy
            if self.yaw >= 360:
                self.yaw %= 360
            elif self.yaw < 0:
                self.yaw = 360 + (self.yaw % 360)
            self.pitch = min(max(self.pitch, -90), 90)
            QCursor.setPos(self.mapToGlobal(QPoint(center_x, center_y)))
            self.update()


    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.fov -= delta * 0.1
        self.fov = max(30, min(self.fov, 90))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.width() / self.height(), 0.1, 1000)
        self.update()

    def set_stroke_width(self, width):
        self.stroke_width = width
        self.update()
    def set_stroke_color(self, color):
        self.color = color
        self.update()

    def set_map_transparency(self, map_transparency):
        self.map_transparency = map_transparency
        self.update()
    def set_map_color(self, map_color, map_color_name):
        self.map_color = map_color
        self.map_color_name=map_color_name
        self.update()

    def draw_point(self, x, y):
        draw = ImageDraw.Draw(self.image,'RGBA') # 'RGBA' for transparency
        half_size = self.stroke_width
        center = (x, y)
        radius = half_size
        point_color = self.color
        draw.ellipse([(center[0] - radius, center[1] - radius), (center[0] + radius, center[1] + radius)], fill=point_color)
        glDeleteTextures(1, [self.texture])
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.image_width, self.image_height, 0, GL_RGB, GL_UNSIGNED_BYTE, self.image.tobytes())
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        self.update()

    def draw_polygon(self,markers_stack):
        
        draw = ImageDraw.Draw(self.image,'RGBA') # 'RGBA' for transparency
        draw.polygon(markers_stack,self.color)

        glDeleteTextures(1, [self.texture])
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.image_width, self.image_height, 0, GL_RGB, GL_UNSIGNED_BYTE, self.image.tobytes())
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        self.update()

    def save_image(self):
        ''' 
            - Latitude
            - Longitude
            - Aerial (0) / Street-view (1)
            - Zoom Level (for aerial) / FOV (for street view)
            - Direction/Pitch (-1 for Aerial)
            - Yaw (-1 for Aerial)
            - Panorma (0) / Current-View (1) / Aerial View (-1)
        '''
        filename = f'{self.lat},{self.lng},1,{self.fov},{self.pitch},{self.yaw},{0}'

        encoded_filename = base64.b64encode(filename.encode()).decode()
        full_path = os.path.join(self.output_directory, f'{encoded_filename}.png')
        self.image.save(full_path)
        print(f"Street-view Image saved")