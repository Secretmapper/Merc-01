import pyglet
import math
import utils
import resources as res
import constants as CONSTS
from pyglet.window import key
from random import randint


class Sprite(pyglet.sprite.Sprite):

    uid = 0

    def __init__(self, on_bounds_kill=False, *args, **kwargs):
        Sprite.uid += 1
        self.id = Sprite.uid

        if 'batch' in kwargs:
            self.layer = kwargs['batch']
        super(Sprite, self).__init__(**kwargs)
        self.dead = False
        self.on_bounds_kill = on_bounds_kill

        self.min_x = self.image.width / 2
        self.min_y = self.image.height / 2
        # todo -hardcoded windows
        self.max_x = CONSTS.game_width + self.image.width / 2
        self.max_y = CONSTS.game_height + self.image.height / 2

        self.half_width = self.image.width / 2
        self.half_height = self.image.width / 2

        self.debug_vertex_list = []
        self.bounds_death = False

    def pos_vertices(self):
        return [self.y - self.height / 2, self.x - self.width / 2, self.y + self.height / 2, self.x + self.width / 2]

    def update(self, dt):
        for i in self.debug_vertex_list:
            i.delete()
        self.debug_vertex_list = []

        if self.on_bounds_kill:
            self.check_bounds()

    def check_bounds(self):
        if self.x < self.min_x or self.x >= self.max_x or self.y < self.min_y or self.y >= self.max_y:
            if not self.dead:
                self.bounds_death = True
            self.dead = True


class Bullet(Sprite):

    def __init__(self, r, *args, **kwargs):
        super(Bullet, self).__init__(**kwargs)
        r *= -math.pi / 180
        self.speed = 20
        self.vel_x = math.cos(r) * self.speed
        self.vel_y = math.sin(r) * self.speed

    def update(self, dt):
        Sprite.update(self, dt)
        self.x = utils.trunc(self.x + self.vel_x, 0, self.max_x)
        self.y = utils.trunc(self.y + self.vel_y, 0, self.max_y)


class EnemyShip(Sprite):

    def __init__(self, behaviours, track, *args, **kwargs):
        super(EnemyShip, self).__init__(**kwargs)
        self.hit = True

        self.min_x = self.image.width / 2
        self.min_y = self.image.height / 2
        self.max_x = CONSTS.game_width - self.half_width
        self.max_y = CONSTS.game_height - self.half_height

        self.vel_x = self.vel_y = 0

        self.track = track
        self.behaviours = []
        for behaviour in behaviours:
            self.behaviours.append(behaviour(self))
        self.near_player = False
        self.neighbors = 1
        self.v_sx = self.v_sy = 0
        self.aneighbors = 1
        self.av_sx = self.av_sy = 0
        self.des_vx = self.des_vy = 0
        self.evade_list = []

    def kill(self):
        self.opacity = 50
        for i in self.debug_vertex_list:
            i.delete()

    def update(self, dt):
        self.xdt = dt / CONSTS.game_iter

        Sprite.update(self, dt)

        for behaviour in self.behaviours:
            behaviour.next()

        last_x, last_y = self.x, self.y

        steer_x = steer_y = 0
        steer_x, steer_y = self.des_vx - self.vel_x, self.des_vy - self.vel_y
        # truncate
        steer_x = utils.trunc(self.des_vx - self.vel_x, 0.5)
        steer_y = utils.trunc(self.des_vy - self.vel_y, 0.5)

        self.vel_x += steer_x
        self.vel_y += steer_y

        """
        Separation
        """
        self.v_sx /= self.neighbors
        self.v_sy /= self.neighbors
        self.v_sx, self.v_sy = utils.normalize(self.v_sx, self.v_sy)
        self.v_sx *= -2
        self.v_sy *= -2

        self.vel_x += self.v_sx
        self.vel_y += self.v_sy
        """
        self.av_sx /= self.aneighbors
        self.av_sy /= self.aneighbors
        self.av_sx, self.av_sy = utils.normalize(self.av_sx, self.av_sy)
        self.av_sx *= -5
        self.av_sy *= -5

        self.vel_x += utils.trunc(self.av_sx, -2, 2)
        self.vel_y += utils.trunc(self.av_sy, -2, 2)
        """
        self.x = utils.trunc(self.x + self.vel_x, 0, CONSTS.game_width)
        self.y = utils.trunc(self.y + self.vel_y, 0, CONSTS.game_height)

        if not self.vel_x == 0:
            theta = math.atan2(self.y - last_y, self.x - last_x)
        else:
            theta = 5

        if CONSTS.DEBUG_MODE:
            self.debug_vertex_list.append(CONSTS.debug_batch.add(2, pyglet.gl.GL_LINES,
                                                                 None,
                                                                 ('v2f', (
                                                                     self.x, self.y, self.x + math.cos(theta) * 50, self.y + math.sin(theta) * 50)),
                                                                 ('c4B', (0, 255,
                                                                          0, 255) * 2)
                                                                 ))
            self.debug_vertex_list.append(CONSTS.debug_batch.add(2, pyglet.gl.GL_LINES,
                                                                 None,
                                                                 ('v2f', (
                                                                     self.x, self.y, self.x + steer_x * 100, self.y + steer_y * 100)),
                                                                 ('c4B', (255,
                                                                          0, 0, 255) * 2)
                                                                 ))

        self.v_sx = self.v_sy = 0
        self.evade_list = []
        self.av_sx = self.av_sy = 0
        self.neighbors = 1
        self.aneighbors = 1
        self.near_player = False

    def type_overlap_cb(self, other):
        """ Push self away when colliding with another object
        This prevents overlapping of enemies.
        """
        self.neighbors += 1

        self.v_sx += other.x - self.x
        self.v_sy += other.y - self.y

    def near_by_cb(self, others):
        """Callback when bullets are near_player
            Used for Evasion Behaviour
        """
        self.evade_list = sum(others, [])


class Ship(Sprite):

    def __init__(self, *args, **kwargs):
        super(Ship, self).__init__(**kwargs)
        self.mouse_pos = (0, 0)
        self.keys = dict(spacebar=False, W=False, A=False, S=False, D=False,
                         left=False, right=False, up=False, down=False)
        self.shoot = False
        self.shoot_timer = 10
        self.i_shoot = self.shoot_timer
        self.speed_x, self.speed_y = 0, 0
        self.speed = 0.5

    def on_mouse_motion(self, x, y, dx, dy):
        self.rotation = -\
            math.atan2(
                y - (self.y + self.layer.y), x - (self.x + self.layer.x)) * 180 / math.pi

    def update(self, dt):
        Sprite.update(self, dt)
        xdt = dt / CONSTS.game_iter
        self.shoot = False
        self.i_shoot -= 1
        if self.i_shoot < 0:
            self.shoot = True
            self.i_shoot = self.shoot_timer

        if self.keys['W']:
            self.speed_y += self.speed * xdt
        if self.keys['S']:
            self.speed_y -= self.speed * xdt
        if self.keys['A']:
            self.speed_x -= self.speed * xdt
        if self.keys['D']:
            self.speed_x += self.speed * xdt

        if self.keys['right']:
            self.rotation = 0
        if self.keys['down']:
            self.rotation = 90
        if self.keys['left']:
            self.rotation = 180
        if self.keys['up']:
            self.rotation = 270

        if self.keys['down'] and self.keys['left']:
            self.rotation = 135
        if self.keys['down'] and self.keys['right']:
            self.rotation = 45
        if self.keys['up'] and self.keys['left']:
            self.rotation = 225
        if self.keys['up'] and self.keys['right']:
            self.rotation = 315

        self.speed_x *= 0.95
        self.speed_y *= 0.95
        self.x += self.speed_x
        self.y += self.speed_y

        if self.x > CONSTS.game_width - self.half_width:
            self.x = CONSTS.game_width - self.half_width
        if self.x < self.half_width:
            self.x = self.half_width
        if self.y > CONSTS.game_height - self.half_height:
            self.y = CONSTS.game_height - self.half_height
        if self.y < self.half_height:
            self.y = self.half_height

    def on_key_press(self, symbol, modifiers):
        if symbol == key.SPACE:
            self.keys['spacebar'] = True
        if symbol == key.W:
            self.keys['W'] = True
        if symbol == key.A:
            self.keys['A'] = True
        if symbol == key.S:
            self.keys['S'] = True
        if symbol == key.D:
            self.keys['D'] = True

        if symbol == key.UP:
            self.keys['up'] = True
        if symbol == key.LEFT:
            self.keys['left'] = True
        if symbol == key.RIGHT:
            self.keys['right'] = True
        if symbol == key.DOWN:
            self.keys['down'] = True

    def on_key_release(self, symbol, modifiers):
        if symbol == key.SPACE:
            self.keys['spacebar'] = False
        if symbol == key.W:
            self.keys['W'] = False
        if symbol == key.A:
            self.keys['A'] = False
        if symbol == key.S:
            self.keys['S'] = False
        if symbol == key.D:
            self.keys['D'] = False

        if symbol == key.UP:
            self.keys['up'] = False
        if symbol == key.LEFT:
            self.keys['left'] = False
        if symbol == key.RIGHT:
            self.keys['right'] = False
        if symbol == key.DOWN:
            self.keys['down'] = False
