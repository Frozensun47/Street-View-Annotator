from OpenGL.GL import *
from OpenGL.GLU import *
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
        self.yaw = 270
        self.heading = heading
        self.pitch = 0
        self.prev_dx = 0
        self.prev_dy = 0
        self.fov = 90
        self.moving = False
        self.coordinates_stack = []
        self.markers_stack = []
        self.sidebar_widget = sidebar_widget
        self.stroke_width = 25
        self.color = (255,0,0)
    
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
            self.mouse_x, self.mouse_y = event.pos().x(), event.pos().y()
            self.moving = True
        elif event.button() == QtCore.Qt.RightButton:
            self.mouse_x, self.mouse_y = event.pos().x(), event.pos().y()
            pixel_x = int(self.mouse_x / self.width() * self.image_width)
            pixel_y = int((self.height() - self.mouse_y) / self.height() * self.image_height)
            heading_offset = 0 - 270
            # print('Offset',heading_offset)
            cal_yaw = (self.yaw - heading_offset) % 360
            cal_pitch = (self.pitch + 90) % 180
            pixel_x = cal_yaw * (self.image_width / 360)
            pixel_y = cal_pitch * (self.image_height / 180)
            image_pixel_x = pixel_x
            image_pixel_y = pixel_y
            index_y = int(pixel_y * (self.depth.shape[0] / self.image_height))
            index_x = int(pixel_x * (self.depth.shape[1] / self.image_width))*(-1)
            # print('Index',index_x,index_y)
            # print('org_depth',self.depth[index_y][index_x])
            depth = self.depth[index_y][index_x]
            distance = depth*math.sin((180-cal_pitch)/360)  #math.sqrt(((depth)**2 - (1.5)**2))
            direction = (self.yaw)-270 +self.heading
            if direction<0:
                direction+=360
            if depth >0 and distance>0: 
                print(f"depth= {depth},Distance = {distance},Heading = {self.heading}, Direction = {int(direction)}")
                lat,lng=get_new_coords(self.lat, self.lng, depth, int(direction))
                self.draw_point(image_pixel_x, image_pixel_y)
                self.markers_stack.append((image_pixel_x,image_pixel_y))
                self.coordinates_stack.append((lat, lng))
                # print(self.coordinates_stack)
                # print('current')
                # print(self.lat, self.lng)
                # print('new')
                # print(lat,lng)
                self.sidebar_widget.update_coordinates_label()
            else: 
                print(f"Inf")
            # print(f'yaw = {self.yaw}')
            # print(f'pitch = {self.pitch}')



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

    def draw_point(self, x, y):
        draw = ImageDraw.Draw(self.image)
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
        draw = ImageDraw.Draw(self.image)
        draw.polygon(markers_stack,self.color)

        glDeleteTextures(1, [self.texture])
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.image_width, self.image_height, 0, GL_RGB, GL_UNSIGNED_BYTE, self.image.tobytes())
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        self.update()
