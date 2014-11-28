import constants as CONSTS
from pyglet.graphics import *
import pyglet
import math
import utils
import random
import resources


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
            self._angle += 180 if random.randint(0, 1) == 0 else 60
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
        self._angle = random.randint(0, 360)
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
        # glTranslatef(self.x, self.y, self.z)
        gluOrtho2D(
            0, self.win.width,
            0, self.win.height)


class ParticleSystem():

    def __init__(self, x, y, life=60, particles=90):
        pic = pyglet.image.load(
            'fire-particle.png', file=pyglet.resource.file('fire-particle.png'))
        self.texture = pic.get_texture()

        self.x, self.y = 0, 0
        self.total_particles = particles
        self.size = 16
        self.life = life
        self.dead = False
        self.alpha_delta = 1 / float(self.life)

        self.particle_pos = sum([[x, y]
                                 for i in xrange(0, self.total_particles)], [])
        self.particle_rad = []
        self.particle_color = []

        rand = lambda: random.random() * 2 - 1
        for i in xrange(0, self.total_particles):
            x_v, y_v = utils.normalize(10 * rand(), 10 * rand())
            self.particle_rad.append(x_v * rand() * 5)
            self.particle_rad.append(y_v * rand() * 5)

            self.particle_color.append(0.7)
            self.particle_color.append(0.2)
            self.particle_color.append(0.1)
            self.particle_color.append(1.0)

        self.particle_life = [
            self.life for i in xrange(0, self.total_particles)]

    def add_particle(self):
        self._init_particle(self)
        self.total_particles += 1

    def _init_particles(self):
        self.particle_pos[uid][0] = self.x
        self.particle_pos[uid][1] = self.y

    def update(self):
        self.update_particles()

    def update_particles(self):

        self.life -= 1
        if self.life <= 0:
            self.dead = True

        for i in xrange(0, len(self.particle_pos), 2):
            x = self.particle_pos[i]
            y = self.particle_pos[i + 1]

            posx, posy = utils.normalize(x, y)

            self.particle_rad[i]
            self.particle_rad[i + 1]

            vel = [self.particle_rad[i], self.particle_rad[i + 1]]

            self.particle_pos[
                i] = utils.trunc(self.particle_pos[i] + vel[0], 0, CONSTS.game_width)
            self.particle_pos[
                i + 1] = utils.trunc(self.particle_pos[i + 1] + vel[1], 0, CONSTS.game_height)

            if self.particle_pos[i + 1] == 0 or self.particle_pos[i + 1] == CONSTS.game_height:
                self.particle_rad[i + 1] *= -1
            if self.particle_pos[i] == 0 or self.particle_pos[i] == CONSTS.game_width:
                self.particle_rad[i] *= -1

            self.particle_life[(i / 2)] -= 1
            self.particle_color[(i / 2) * 4 + 3] -= self.alpha_delta

    def draw(self):
        glPushMatrix()
        glPushAttrib(GL_CURRENT_BIT)

        glPointSize(self.size)

        # Enable States
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture.id)
        glEnable(GL_POINT_SPRITE)
        glTexEnvi(GL_POINT_SPRITE, GL_COORD_REPLACE, GL_TRUE)

        # Vertices Data
        glEnableClientState(GL_VERTEX_ARRAY)
        vertex_ptr = self.particle_pos
        vertex_ptr = (GLfloat * len(vertex_ptr))(*vertex_ptr)
        glVertexPointer(2, GL_FLOAT, 0, vertex_ptr)

        # Color Data
        glEnableClientState(GL_COLOR_ARRAY)
        color_ptr = self.particle_color
        color_ptr = (GLfloat * len(color_ptr))(*color_ptr)
        glColorPointer(4, GL_FLOAT, 0, color_ptr)

        # Color Buffer for Blend
        glPushAttrib(GL_COLOR_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)

        # Actual Draw
        glDrawArrays(GL_POINTS, 0, self.total_particles)

        # Pop Buffer Blend
        glPopAttrib()
        # Pop Color Preserve
        glPopAttrib()

        # Disable States
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisable(GL_POINT_SPRITE)
        glDisable(GL_TEXTURE_2D)

        glPopMatrix()
