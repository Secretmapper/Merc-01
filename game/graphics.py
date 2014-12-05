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
        self.ax = 0

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

    def star_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        x = (self._track.x + self._offset[1]) / float(CONSTS.win_width / 3)
        y = (self._track.y + self._offset[0]) / float(CONSTS.win_height / 3)
        glTranslatef(x, y, self.z)
        gluOrtho2D(
            0, self.win.width,
            0, self.win.height)

    def game_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glTranslatef(self.x, self.y, self.z)
        gluOrtho2D(
            0, self.win.width,
            0, self.win.height)

    def hud_project(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(
            0, self.win.width,
            0, self.win.height)

    def hud_projection(self):
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # glTranslatef(self.x, self.y, self.z)
        gluOrtho2D(
            0, self.win.width,
            0, self.win.height)
        """

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(
            40.0, CONSTS.win_width / float(CONSTS.win_height), 0.1, 2000.0)
        glTranslatef(0, 0, -800)
        ang = min(15, (1 - float(self.ax) / (CONSTS.win_width / 2)) * 30)
        # print ang
        if ang >= 0:
            glRotatef(ang, 0, CONSTS.win_height / 2, 0)
        glTranslatef(-400, -300, 0)
        glMatrixMode(GL_MODELVIEW)


class ParticleSystem():

    def __init__(self, x, y, life=0, rate=30, speed=2, speed_var=1, particle_life=60, particles=90, angle=45, rgb=[0.7 * 255, 0.25 * 255, 0.1 * 255]):
        speed_var = random.randint(0, 5)
        pic = pyglet.image.load(
            'fire-particle.png', file=pyglet.resource.file('fire-particle.png'))
        self.texture = pic.get_texture()

        self.total_life = particle_life

        self.x, self.y = 0, 0
        self.total_particles = particles
        self.size = 16

        self.infi_life = False
        self.emit_rate = self.total_life
        self.emit_counter = 0
        if life < 0:
            self.infi_life = True
            self.emit_counter = self.emit_rate * 2
        elif life == 0:
            life = particle_life

        self.life = life
        self.particle_life_i = particle_life
        self.particle_life = particle_life

        self.dead = False
        self.alpha_delta = 1 / float(self.particle_life)
        self.angle = angle

        self.particle_pos = sum([[x, y]
                                 for i in xrange(0, self.total_particles)], [])
        self.particle_rad = []
        self.particle_color = []

        rand = lambda: random.random() * 2 - 1
        for i in xrange(0, self.total_particles):

            if self.infi_life:
                # If infi_life, linear angle
                a = math.radians(angle)
                v_x, v_y = math.cos(a), math.sin(a)

                sp = 1 * random.random()  # rand()
                self.particle_rad.append(v_x * sp)
                self.particle_rad.append(v_y * sp)
            else:
                x_v, y_v = utils.normalize(1 * rand(), 1 * rand())
                self.particle_rad.append(x_v * rand() * (speed + speed_var))
                self.particle_rad.append(y_v * rand() * (speed + speed_var))

            self.particle_color.append(rgb[0] / 255.0)
            self.particle_color.append(rgb[1] / 255.0)
            self.particle_color.append(rgb[2] / 255.0)
            self.particle_color.append(1.0)

        self.particle_life = [
            particle_life for i in xrange(0, self.total_particles)]

        self.emission_rate = 75

    def add_particle(self):
        self._init_particle(self)
        self.total_particles += 1

    def _init_particles(self):
        self.particle_pos[uid][0] = self.x
        self.particle_pos[uid][1] = self.y

    def update(self):
        self.update_particles()

    def update_particles(self):

        self.emit_counter += 120

        while self.emit_counter > self.emit_rate:
            ix = -1
            for i in range(len(self.particle_life)):
                if self.particle_life[i] <= 0:
                    ix = i
                    break

            if ix == -1:
                break

            self.emit_counter = 0
            self.particle_pos[ix * 2] = self.x
            self.particle_pos[ix * 2 + 1] = self.y
            self.particle_life[ix] = self.particle_life_i

            rand = lambda: random.random() * 2 - 1
            a = math.radians((180 - self.angle) + 10 * rand())
            v_x, v_y = math.cos(a), math.sin(a)

            sp = 1 * rand()
            self.particle_rad[ix * 2] = v_x + sp
            self.particle_rad[ix * 2 + 1] = v_y + sp

            self.particle_color[ix * 4] = 0.7
            self.particle_color[ix * 4 + 1] = 0.2
            self.particle_color[ix * 4 + 2] = 0.1
            self.particle_color[ix * 4 + 3] = 1.0

            self.emit_counter -= self.emit_rate

        self.life -= 1
        if self.life <= 0 and not self.infi_life:
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


class Drawer():

    @staticmethod
    def draw(particle_pos, colors, size=5):
        pic = pyglet.image.load(
            'bit.png', file=pyglet.resource.file('bit.png'))
        texture = pic.get_texture()

        total_particles = len(particle_pos)

        glPushMatrix()
        glPushAttrib(GL_CURRENT_BIT)

        glPointSize(size)

        # Enable States
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture.id)
        glEnable(GL_POINT_SPRITE)
        glTexEnvi(GL_POINT_SPRITE, GL_COORD_REPLACE, GL_TRUE)

        # Vertices Data
        glEnableClientState(GL_VERTEX_ARRAY)
        vertex_ptr = particle_pos
        vertex_ptr = (GLfloat * len(vertex_ptr))(*vertex_ptr)
        glVertexPointer(2, GL_FLOAT, 0, vertex_ptr)

        # Color Data
        glEnableClientState(GL_COLOR_ARRAY)
        color_ptr = colors
        color_ptr = (GLfloat * len(color_ptr))(*color_ptr)
        glColorPointer(4, GL_FLOAT, 0, color_ptr)

        # Color Buffer for Blend
        glPushAttrib(GL_COLOR_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)

        # Actual Draw
        glDrawArrays(GL_POINTS, 0, total_particles)

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


class Starfield():

    @staticmethod
    def create(seed=None, min_x=-50, max_x=50, min_y=-50, max_y=50, size=4, particles=50):
        pic = pyglet.image.load(
            'star.png', file=pyglet.resource.file('star.png'))
        texture = pic.get_texture()

        total_particles = particles
        particle_pos = []
        if seed:
            myrand = random.Random(seed)
        else:
            myrand = random.Random()
        for x in range(0, total_particles):
            particle_pos.append(myrand.randint(min_x, max_x))
            particle_pos.append(myrand.randint(min_y, max_y))
        glPushMatrix()
        glPushAttrib(GL_CURRENT_BIT)

        glPointSize(size)

        # Enable States
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture.id)
        glEnable(GL_POINT_SPRITE)
        glTexEnvi(GL_POINT_SPRITE, GL_COORD_REPLACE, GL_TRUE)

        # Vertices Data
        glEnableClientState(GL_VERTEX_ARRAY)
        vertex_ptr = particle_pos
        vertex_ptr = (GLfloat * len(vertex_ptr))(*vertex_ptr)
        glVertexPointer(2, GL_FLOAT, 0, vertex_ptr)

        particle_color = []

        rand = lambda: random.random() * 2 - 1
        for i in xrange(0, total_particles):

            particle_color.append(1.0 - myrand.random())
            particle_color.append(1.0 - myrand.random())
            particle_color.append(1.0 - myrand.random())
            particle_color.append(1.0 - myrand.random())

        # Color Data
        glEnableClientState(GL_COLOR_ARRAY)
        color_ptr = particle_color
        color_ptr = (GLfloat * len(color_ptr))(*color_ptr)
        glColorPointer(4, GL_FLOAT, 0, color_ptr)

        # Color Buffer for Blend
        glPushAttrib(GL_COLOR_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)

        # Actual Draw
        glDrawArrays(GL_POINTS, 0, total_particles)

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
