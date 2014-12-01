import pyglet
import math
import utils
import resources as res
import constants as CONSTS
from pyglet.window import key
from random import randint
import behaviours


class Sprite(pyglet.sprite.Sprite):

    uid = 0

    def __init__(self, on_bounds_kill=False, cb_type=-1, *args, **kwargs):
        Sprite.uid += 1
        self.id = Sprite.uid

        if 'batch' in kwargs:
            self.layer = kwargs['batch']

        self.cb_type = cb_type

        super(Sprite, self).__init__(**kwargs)
        self.dead = False
        self.on_bounds_kill = on_bounds_kill

        self.min_x = self.image.width / 2
        self.min_y = self.image.height / 2
        self.max_x = CONSTS.game_width
        self.max_y = CONSTS.game_height

        self.half_width = self.image.width / 2
        self.half_height = self.image.width / 2

        self.debug_vertex_list = []
        self.bounds_death = False
        self.remove = False

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

    def __init__(self, behaviours=None, speed=10, track=None, rotation=0, *args, **kwargs):
        super(Bullet, self).__init__(**kwargs)
        self.track = track
        self.speed = speed
        self.first_x, self.first_y = self.x, self.y
        self.behaviours = []
        for behaviour in behaviours:
            # behaviour is an array, function, **kwargs
            self.behaviours.append(behaviour[0](self, *behaviour[1:]))
        rotation *= -math.pi / 180
        self.vel_x = math.cos(rotation) * 10
        self.vel_y = math.sin(rotation) * 10
        self.des_vx = self.des_vy = 0

    def update(self, dt):
        Sprite.update(self, dt)

        for behaviour in self.behaviours:
            behaviour.next()

        self.x = utils.trunc(self.x + self.vel_x, 0, CONSTS.game_width)
        self.y = utils.trunc(self.y + self.vel_y, 0, CONSTS.game_height)


class AbstractEnemy(Sprite):

    def __init__(self, *args, **kwargs):
        super(AbstractEnemy, self).__init__(**kwargs)
        self.bullets = False
        self.split = False
        self.sensor = False
        self.trackable = True


class Sensor(AbstractEnemy):

    def __init__(self, callbacks, track, *args, **kwargs):
        super(Sensor, self).__init__(**kwargs)
        self.opacity = 0
        self.callbacks = callbacks
        self.particle_data = {'particles': 0, 'particle_life': 20}
        self.bullets = False
        self.sensor = True
        self.trackable = False

    def trigger(self, *args, **kwargs):
        for i in self.callbacks:
            i(self, **kwargs)

    def kill(self):
        self.opacity = 0


class EnemyShip(AbstractEnemy):

    def __init__(self, behaviours, track, particle_data={}, *args, **kwargs):
        super(EnemyShip, self).__init__(**kwargs)

        self.min_x = self.image.width / 2
        self.min_y = self.image.height / 2
        self.max_x = CONSTS.game_width - self.half_width
        self.max_y = CONSTS.game_height - self.half_height

        self.vel_x = self.vel_y = 0

        self.behaviours = []
        for behaviour in behaviours:
            # behaviour is an array, function, **kwargs
            self.behaviours.append(behaviour[0](self, *behaviour[1:]))
        self.particle_data = particle_data
        self.track = track
        self.near_player = False
        self.bullets = []
        self.neighbors = 1
        self.v_sx = self.v_sy = 0
        self.des_vx = self.des_vy = 0
        self.evade_list = []
        self.death_vx = False
        self.trackable = True

    def shot(self, x, y):
        death_theta = math.atan2(
            self.y - y, self.x - x)
        self.death_vx = math.cos(death_theta) * 0.2
        self.death_vy = math.sin(death_theta) * 0.2

    def kill(self):
        # Let's call behaviours one last time for cleanup callbacks when dead
        # i.e. Circle Detect
        for behaviour in self.behaviours:
            behaviour.next()

        self.opacity = 75
        for i in self.debug_vertex_list:
            i.delete()
        self.debug_vertex_list = []

    def update(self, dt):
        if self.dead:
            # if positional death (because of bullets, fade)
            if self.death_vx:
                self.x += self.death_vx
                self.y += self.death_vy
                self.scale *= 0.999
                if self.scale <= 0.3:
                    self.remove = True
            # else if non-positional death (i.e., line enemy, out of bounds),
            # just remove
            else:
                self.remove = True
            return

        self.bullets = []

        self.xdt = dt / CONSTS.game_iter

        Sprite.update(self, dt)

        last_x, last_y = self.x, self.y

        for behaviour in self.behaviours:
            behaviour.next()

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
        self.neighbors = 1
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
        self.keys = dict(spacebar=False, W=False, A=False, S=False, D=False, shift=False,
                         left=False, right=False, up=False, down=False)
        self.shoot = False
        self.shoot_type = 1
        self.shoot_timer = 10
        self.i_shoot = self.shoot_timer
        self.speed_x, self.speed_y = 0, 0
        self.speed = 0.3
        self.boost = False

    def on_mouse_motion(self, x, y, dx, dy):
        self.rotation = -\
            math.atan2(
                y - (self.y + self.layer.y), x - (self.x + self.layer.x)) * 180 / math.pi

    def hit(self):
        1
        #self.opacity = 0

    def update(self, dt):
        Sprite.update(self, dt)
        xdt = dt / CONSTS.game_iter
        self.shoot = False
        self.i_shoot -= 1
        if self.i_shoot < 0:
            self.shoot = True
            self.i_shoot = self.shoot_timer

        if self.keys['shift']:
            self.speed = 1.0
            self.boost = True
        else:
            self.speed = 0.3
            self.boost = False

        if self.keys['W']:
            self.speed_y += self.speed * xdt
        if self.keys['S']:
            self.speed_y -= self.speed * xdt
        if self.keys['A']:
            self.speed_x -= self.speed * xdt
        if self.keys['D']:
            self.speed_x += self.speed * xdt

        if self.keys['D']:
            self.rotation = 0
        if self.keys['S']:
            self.rotation = 90
        if self.keys['A']:
            self.rotation = 180
        if self.keys['W']:
            self.rotation = 270

        if self.keys['S'] and self.keys['A']:
            self.rotation = 135
        if self.keys['S'] and self.keys['D']:
            self.rotation = 45
        if self.keys['W'] and self.keys['A']:
            self.rotation = 225
        if self.keys['W'] and self.keys['D']:
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
        if symbol == key._1:
            self.shoot_type = 1
        if symbol == key._2:
            self.shoot_type = 2
        if symbol == key.SPACE:
            self.keys['spacebar'] = True
        if symbol == key.LSHIFT:
            self.keys['shift'] = True
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
        if symbol == key.LSHIFT:
            self.keys['shift'] = False
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
