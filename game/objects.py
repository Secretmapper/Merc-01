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

    @property
    def is_outside(self):
        return self.x < self.min_x or self.x >= self.max_x or self.y < self.min_y or self.y >= self.max_y

    @property
    def is_outside_of_screen(self):
        return self.x < self.min_x - 50 or self.x >= self.max_x + 50 or self.y < self.min_y - 50 or self.y >= self.max_y + 50

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
        self._des_vx = self._des_vy = 0

    def update(self, dt):
        Sprite.update(self, dt)
        self.black_hole_checks = {}

        for behaviour in self.behaviours:
            behaviour.next()

        self.x = utils.trunc(self.x + self.vel_x, 0, CONSTS.game_width)
        self.y = utils.trunc(self.y + self.vel_y, 0, CONSTS.game_height)

    def black_hole(self, hole):
        if hole.uid not in self.black_hole_checks:
            self.black_hole_checks[hole.uid] = True
            diff = self.x - hole.x, self.y - hole.y
            l = math.sqrt((self.x - hole.x) ** 2 + (self.y - hole.y) ** 2)

            self.vel_x += utils.normalize(diff[0], diff[1])[0] * 1.5
            self.vel_y += utils.normalize(diff[0], diff[1])[1] * 2


class AbstractEnemy(Sprite):

    def __init__(self, callbacks=[], *args, **kwargs):
        super(AbstractEnemy, self).__init__(**kwargs)
        self.bullets = False
        self.split = False
        self.sensor = False
        self.show_on_radar = False     # Should be shown on radar?
        self.trackable = True          # Trackable by Homing Missles?
        self.collidable = True
        self.callbacks = callbacks

    def trigger(self, *args, **kwargs):
        for i in self.callbacks:
            i(self, **kwargs)

    def shot(self, x=0, y=0):
        pass


class Sensor(AbstractEnemy):

    def __init__(self, callbacks, track, *args, **kwargs):
        super(Sensor, self).__init__(**kwargs)
        self.opacity = 0
        self.callbacks = callbacks
        self.particle_data = {'particles': 0, 'particle_life': 20}
        self.bullets = False
        self.sensor = True
        self.trackable = False

    def update(self, dt):
        AbstractEnemy.update(self, dt)
        if CONSTS.DEBUG_MODE:
            self.opacity = 100
        else:
            self.opacity = 0

    def kill(self):
        pass


class EnemyShip(AbstractEnemy):

    def __init__(self, behaviours, track, particle_data={}, max_vel=5, *args, **kwargs):
        super(EnemyShip, self).__init__(**kwargs)

        self.max_vel = max_vel

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
        self.bullets = []

        # who to follow/track
        self.track = track
        self.trackable = True
        self.show_on_radar = False

        # nonactive if enemy is still entering map
        self.nonactive = True

        # neighbors for evasion/separation
        self._neighbors = 1
        self._aneighbors = 1

        # destination and separation velocities
        self._des_vx = self._des_vy = 0
        self._sep_vx = self._sep_vy = 0
        self._blackhole_sep_v = 3.0

        self.evade_list = []  # evasion list

        # death velocities
        self._death_vx = self._death_vy = False

        # enemy exists from map
        self._exits = False

        self._init_behaviour()

    def _init_behaviour(self):
        self._enter_behaviour = behaviours.enter(self)
        self._exit_behaviour = behaviours.dying(self)

    @property
    def is_outside_of_screen(self):
        margin = 50
        return (not self.nonactive) and (self.x < self.min_x - margin or self.x >= self.max_x + margin or self.y < self.min_y - margin or self.y >= self.max_y + margin)

    def shot(self, x, y):
        death_theta = math.atan2(
            self.y - y, self.x - x)
        self.killer_pos = (x, y)
        self._death_vx = math.cos(death_theta) * 0.2
        self._death_vy = math.sin(death_theta) * 0.2

    def kill(self):
        # Let's call behaviours one last time for cleanup callbacks when dead
        # i.e. Circle Detect
        for behaviour in self.behaviours:
            behaviour.next()

        self.opacity = 75
        for i in self.debug_vertex_list:
            i.delete()
        self.debug_vertex_list = []
        self.trigger()

    def update(self, dt):
        self.black_hole_checks = {}
        if self.nonactive and not self._enter_behaviour.next():
            return
        if self.dead:
            self._exit_behaviour.next()
            return

        self.bullets = []

        self.xdt = dt / CONSTS.game_iter

        Sprite.update(self, dt)

        last_x, last_y = self.x, self.y

        for behaviour in self.behaviours:
            behaviour.next()

        steer_x = steer_y = 0
        # friction if no desired velocity
        if self._des_vx == 0 and self._des_vy == 0:
            self.vel_x *= 0.9
            self.vel_y *= 0.9
        else:
            steer_x, steer_y = self._des_vx - \
                self.vel_x, self._des_vy - self.vel_y
            # truncate
            steer_x = utils.trunc(self._des_vx - self.vel_x, 0.5)
            steer_y = utils.trunc(self._des_vy - self.vel_y, 0.5)

            self.vel_x += steer_x
            self.vel_y += steer_y

        """
        Separation
        """
        self._sep_vx /= self._neighbors
        self._sep_vy /= self._neighbors
        self._sep_vx, self._sep_vy = utils.normalize(
            self._sep_vx, self._sep_vy)
        self._sep_vx *= -2
        self._sep_vy *= -2

        self.vel_x += self._sep_vx
        self.vel_y += self._sep_vy

        self.vel_x = utils.trunc(self.vel_x, -self.max_vel, self.max_vel)
        self.vel_y = utils.trunc(self.vel_y, -self.max_vel, self.max_vel)

        if self._exits:
            self.x = self.x + self.vel_x
            self.y = self.y + self.vel_y
            if self.show_on_radar and self.is_outside:
                self.show_on_radar = False
        else:
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

        self._sep_vx = self._sep_vy = 0
        self.evade_list = []
        self._neighbors = 1

    def type_overlap_cb(self, other):
        """ Push self away when colliding with another object
        This prevents overlapping of enemies.
        """
        self._neighbors += 1

        self._sep_vx += other.x - self.x
        self._sep_vy += other.y - self.y

    def near_by_cb(self, others):
        """Callback when bullets are near_player
            Used for Evasion Behaviour
        """
        self.evade_list = sum(others, [])

    def black_hole(self, hole):
        if hole.uid not in self.black_hole_checks:
            diff = hole.x - self.x, hole.y - self.y
            l = math.sqrt((hole.x - self.x) ** 2 + (hole.y - self.y) ** 2)

            self.vel_x += utils.normalize(diff[0],
                                          diff[1])[0] / self._blackhole_sep_v
            self.vel_y += utils.normalize(diff[0],
                                          diff[1])[1] / self._blackhole_sep_v


class Ship(Sprite):

    def __init__(self, *args, **kwargs):
        super(Ship, self).__init__(**kwargs)
        self.mouse_pos = (0, 0)
        self.keys = dict(spacebar=False, W=False, A=False, S=False, D=False, shift=False,
                         left=False, right=False, up=False, down=False)
        self.shoot = False
        self.shoot_type = 1
        self.shoot_timer = 8
        self.i_shoot = self.shoot_timer
        self.speed_x, self.speed_y = 0, 0
        self.speed = 0.75
        self.boost = False
        self.shoot_rotation = 0

        self.invinsible = False
        self._invinsible_i = 0

        self.black_hole_checks = {}

    def black_hole(self, hole):
        if hole.uid not in self.black_hole_checks:
            self.black_hole_checks[hole.uid] = True
            diff = hole.x - self.x, hole.y - self.y
            l = math.sqrt((hole.x - self.x) ** 2 + (hole.y - self.y) ** 2)

            self.speed_x += utils.normalize(diff[0], diff[1])[0] / 2.0
            self.speed_y += utils.normalize(diff[0], diff[1])[1] / 2.0

    def on_mouse_motion(self, x, y, dx, dy):
        self.shoot_rotation = -\
            math.atan2(
                y - (self.y + self.layer.y), x - (self.x + self.layer.x)) * 180 / math.pi

    def hit(self):
        1
        #self.opacity = 0

    def respawn(self):
        self.opacity = 255
        self._invinsible_i = 20
        self.invinsible = True
        self.dead = False

    def update(self, dt):
        Sprite.update(self, dt)
        self.black_hole_checks = {}

        if self._invinsible_i >= 0:
            self._invinsible_i -= 1
            if self._invinsible_i <= 0:
                self.invinsible = False

        xdt = dt / CONSTS.game_iter
        self.shoot = False
        self.i_shoot -= 1
        if self.i_shoot < 0:
            self.shoot = True
            self.i_shoot = self.shoot_timer

        # if self.keys['shift']:
        #    self.speed = 1.0
        #    self.boost = True
        # else:
        #    self.speed = 0.3
        #    self.boost = False

        if self.keys['W']:
            self.speed_y += self.speed * xdt
        if self.keys['S']:
            self.speed_y -= self.speed * xdt
        if self.keys['A']:
            self.speed_x -= self.speed * xdt
        if self.keys['D']:
            self.speed_x += self.speed * xdt

        if not self.keys['shift']:
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

        if self.keys['right']:
            self.shoot_rotation = 0
        if self.keys['down']:
            self.shoot_rotation = 90
        if self.keys['left']:
            self.shoot_rotation = 180
        if self.keys['up']:
            self.shoot_rotation = 270

        if self.keys['down'] and self.keys['left']:
            self.shoot_rotation = 135
        if self.keys['down'] and self.keys['right']:
            self.shoot_rotation = 45
        if self.keys['up'] and self.keys['left']:
            self.shoot_rotation = 225
        if self.keys['up'] and self.keys['right']:
            self.shoot_rotation = 315

        self.speed_x *= 0.9
        self.speed_y *= 0.9
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
