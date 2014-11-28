from random import randint
import math
import utils
import pyglet
import resources as res
import constants as CONSTS


def rotate(self):
    while(True):
        self.rotation += 5
        yield 0


def bounce(self):
    speed = 10
    r = -randint(0, 360) * math.pi / 180
    self.dir_x = math.cos(r)
    self.dir_y = math.sin(r)
    while(True):
        if self.y <= self.min_y or self.y >= self.max_y:
            self.dir_y = -self.dir_y
        elif self.x <= self.min_x or self.x >= self.max_x:
            self.dir_x = -self.dir_x

        self.vel_x = self.dir_x * speed
        self.vel_y = self.dir_y * speed
        yield 0


def move_square(self):
    f = 30
    speed = 1
    while(True):
        for i in xrange(f):
            self.vel_x += speed
            yield 0
        for i in xrange(f):
            self.vel_y -= speed
            yield 0
        for i in xrange(f):
            self.vel_x -= speed
            yield 0
        for i in xrange(f):
            self.vel_y += speed
            yield 0


def follow_player(self):
    speed = 5
    while(True):
        vx, vy = utils.normalize(self.track.x - self.x, self.track.y - self.y)
        vx *= speed
        vy *= speed
        self.des_vx = vx
        self.des_vy = vy
        yield 0


def rotate_to_player(self):
    i = 0
    amplitude = 5
    speed = 2
    while(True):
        i += amplitude
        vx, vy = utils.normalize(self.track.x - self.x, self.track.y - self.y)
        self.des_vy = amplitude * math.cos(i * math.pi / 180) + vy * speed
        self.des_vx = amplitude * math.sin(i * math.pi / 180) + vx * speed
        yield 0


def zip(self):
    x_active = False

    friction = 0.98
    iter_i = 0
    while(True):
        iter_i -= 1
        if iter_i <= 0:
            iter_i = 240
            x_active = not x_active
            self.vel_x = self.vel_y = self.des_vx = self.des_vy = 0
            vx = 10 if self.track.x > self.x else -10
            vy = 10 if self.track.y > self.y else -10

        if x_active:
            vx *= friction
            self.des_vx = vx
        else:
            vy *= friction
            self.des_vy = vy
        yield 0


def evade(self):
    speed = 50
    while(True):
        aneighbors = 0
        vx = vy = 0
        for other in self.evade_list:
            aneighbors += 1

            vx += (other.x + other.vel_x) - self.x
            vy += (other.y + other.vel_y) - self.y

        vx *= speed
        vy *= speed

        vx /= self.aneighbors
        vy /= self.aneighbors
        vx, vy = utils.normalize(vx, vy)
        vx *= -2
        vy *= -2

        self.vel_x += vx
        self.vel_y += vy
        yield 0


def flee(self):
    speed = 0.5
    while(True):
        vx, vy = utils.normalize(self.x - self.track.x, self.y - self.track.y)
        vx *= speed
        vy *= speed
        self.des_vx += vx
        self.des_vy += vy
        yield 0


def link_sensor(self):
    """
    Callback when link sensor is collided to
    """
    self.link_enemy.link_collide()


def split(self):
    while(True):
        self.split = True
        yield 0


def link(self, pair=None, sensors=None):

    if not pair == None:
        self.pair = pair
        init_dists = []
        # Get the initial distances for the sensors (radial movement)
        for sensor in sensors:
            init_dists.append(sensor.x - pair.x)
            sensor.link_enemy = self
        init_dist = self.x - pair.x

        """
        Kill the whole Line when collided with sensor
        """
        def link_collide():
            if self.dead == False:
                self.dead = True
                pair.dead = True
                for sensor in sensors:
                    sensor.dead = True
                    sensor.kill()

        self.link_collide = link_collide
    while(True):
        if pair == None:
            self.rotation -= 1
        else:
            self.y = pair.y + init_dist * \
                math.sin(-pair.rotation * math.pi / 180)
            self.x = pair.x + init_dist * \
                math.cos(-pair.rotation * math.pi / 180)

            for i in xrange(len(sensors)):
                sensors[i].y = pair.y + init_dists[i] * \
                    math.sin(-pair.rotation * math.pi / 180)
                sensors[i].x = pair.x + init_dists[i] * \
                    math.cos(-pair.rotation * math.pi / 180)

            self.rotation = pair.rotation - 180
            self.debug_vertex_list.append(self.layer.add(2, pyglet.gl.GL_LINES,
                                                         None,
                                                         ('v2f', (
                                                             self.x, self.y, pair.x, pair.y)),
                                                         ('c4B', (255,
                                                                  0, 0, 255) * 2)
                                                         ))
        yield 0


def shoot_circle(self, timer=60):
    from game.objects import Bullet
    timer_i = 10
    while(True):
        timer_i -= 1
        if timer_i <= 0:
            timer_i = timer
            for i in range(0, 360, 15):
                bullet = Bullet(behaviours=[[by_angle, i]], x=self.x, y=self.y, speed=2,
                                img=res.fire_particle, batch=self.batch, on_bounds_kill=True)
                self.bullets.append(bullet)
        yield 0


def shoot_fire(self, angle=90, mod_dist=5):
    from game.objects import Bullet

    timer_i = 10
    mod_dist = mod_dist
    a_i = angle
    mod = True

    while(True):
        timer_i -= 1
        if timer_i <= 0:
            timer_i = 20

            a_i += mod_dist

            bullet = Bullet(behaviours=[[by_angle, a_i]], x=self.x, y=self.y, speed=2,
                            img=res.fire_particle, batch=self.batch, on_bounds_kill=True)
            self.bullets.append(bullet)

        yield 0
"""
Bullet Behaviours
"""


def spiral(self, i):
    wait = 60
    while(True):
        wait -= 1
        if wait < 0:
            i += 0.4
        r = i * -math.pi / 180
        self.vel_x = math.cos(r) * self.speed
        self.vel_y = -2  # math.sin(r) * self.speed

        yield 0


def by_angle(self, r):
    r *= -math.pi / 180
    self.vel_x = math.cos(r) * self.speed
    self.vel_y = math.sin(r) * self.speed
    while(True):
        yield 0


def penrose(self):
    r = 0
    while(True):
        r += 5
        r_pi = r * -math.pi / 180
        k = 6 / float(5)
        self.x = math.cos(k * r_pi) * math.sin(r_pi) * 100 + self.first_x
        self.y = math.sin(k * r_pi) * math.sin(r_pi) * 100 + self.first_y
        yield 0
