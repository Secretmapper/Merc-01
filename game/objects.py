import pyglet
import math
import resources as res
import constants as CONSTS
from pyglet.window import key
from random import randint


class Sprite(pyglet.sprite.Sprite):

    def __init__(self, on_bounds_kill=False, *args, **kwargs):
        if 'batch' in kwargs:
            self.layer = kwargs['batch']
        super(Sprite, self).__init__(**kwargs)
        self.dead = False
        self.on_bounds_kill = on_bounds_kill

        self.min_x = -self.image.width / 2
        self.min_y = -self.image.height / 2
        # todo -hardcoded windows
        self.max_x = CONSTS.game_width + self.image.width / 2
        self.max_y = CONSTS.game_height + self.image.height / 2

        self.half_width = self.image.width / 2
        self.half_height = self.image.width / 2

        self.debug_vertex_list = None

    def pos_vertices(self):
        return [self.y - self.height / 2, self.x - self.width / 2, self.y + self.height / 2, self.x + self.width / 2]

    def update(self, dt):
        if CONSTS.DEBUG_MODE and self.debug_vertex_list:
            self.debug_vertex_list.delete()

        if self.on_bounds_kill:
            self.check_bounds()

    def check_bounds(self):
        if self.x < self.min_x or self.x > self.max_x or self.y < self.min_y or self.y > self.max_y:
            self.dead = True


class Bullet(Sprite):

    def __init__(self, r, *args, **kwargs):
        super(Bullet, self).__init__(**kwargs)
        r *= -math.pi / 180
        self.dir_x = math.cos(r)
        self.dir_y = math.sin(r)
        self.speed = 20

    def update(self, dt):
        Sprite.update(self, dt)
        self.x += self.dir_x * self.speed
        self.y += self.dir_y * self.speed


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

    def kill(self):
        if self.debug_vertex_list:
            self.debug_vertex_list.delete()
            self.opacity = 50

    def update(self, dt):
        Sprite.update(self, dt)
        self.xdt = dt / CONSTS.game_iter
        for behaviour in self.behaviours:
            behaviour.next()

        last_x = self.x
        last_y = self.y
        self.x += self.vel_x * self.xdt
        self.y += self.vel_y * self.xdt
        self.vel_x *= 0.8 * self.xdt
        self.vel_y *= 0.8 * self.xdt

        if not self.vel_x == 0:
            theta = math.atan2(self.y - last_y, self.x - last_x)
        else:
            theta = 5

        if CONSTS.DEBUG_MODE:
            self.debug_vertex_list = CONSTS.debug_batch.add(2, pyglet.gl.GL_LINES,
                None,
                ('v2f', (self.x, self.y, self.x+math.cos(theta)*50, self.y+math.sin(theta)*50))
            )

    def type_overlap_cb(self, other):
        """ Push self away when colliding with another object
        This prevents overlapping of enemies.

        Currently Limited to ~70 objects until weird things happen
        """
        #vector subtraction
        v_x, v_y = self.x - other.x, self.y - other.y

        #vector magnitude
        v_mag = (v_x * v_x + v_y * v_y) + 1

        #push enemy away
        self.vel_x += 1*(v_x/v_mag)
        self.vel_y += 1*(v_y/v_mag)


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
        self.rotation = - \
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

