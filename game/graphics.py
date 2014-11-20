import pyglet
import math
import constants as CONSTS
from pyglet.graphics import glMatrixMode, GL_PROJECTION, glLoadIdentity, gluOrtho2D, glClear, GL_COLOR_BUFFER_BIT, GL_MODELVIEW, glTranslatef
from random import randint


class Layer(pyglet.graphics.Batch):

    def __init__(self, *args, **kwargs):
        super(Layer, self).__init__(**kwargs)
        self.x = 0
        self.y = 0
        self.z = 0


class Camera(object):

    def __init__(self, win, x=0, y=0, z=0, zoom=1.0):
        self.win = win
        self.zoom = zoom
        self.x, self.y, self.z = x, y, z

        self._offset = [0, 0]
        self._track = type('obj', (object,), {'x': 0, 'y': 0})
        self._radius = 0
        self._shake_dec = 0  # how much the shake dies down every update

    def update(self, dt):
        if self._radius > 0:
            self._radius *= self._shake_dec
            self._angle += 180 if randint(0, 1) == 0 else 60
            self._offset = [
                math.sin(self._angle) * self._radius, math.cos(self._angle) * self._radius]
            if math.floor(self._radius) == 0.0:
                self._radius = 0

        self.x = (
            self._track.x + self._offset[1]) / float(CONSTS.win_width / 2)
        self.y = (
            self._track.y + self._offset[0]) / float(CONSTS.win_height / 2)

    def track(self, track):
        self._track = track

    def shake(self, r, dec=0.9):
        self._radius = r
        self._shake_dec = dec
        self._angle = randint(0, 360)
        self._offset = [
            math.sin(self._angle) * self._radius, math.cos(self._angle) * self._radius]

    def game_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glTranslatef(self.x, self.y, self.z)
        gluOrtho2D(
            0, self.win.width,
            0, self.win.height)

    def hud_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        #glTranslatef(self.x, self.y, self.z)
        gluOrtho2D(
            0, self.win.width,
            0, self.win.height)
