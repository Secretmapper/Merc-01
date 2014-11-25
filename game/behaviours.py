from random import randint
import math
import utils


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
        vx *= -5
        vy *= -5

        self.vel_x += utils.trunc(vx, -2, 2)
        self.vel_y += utils.trunc(vy, -2, 2)
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
