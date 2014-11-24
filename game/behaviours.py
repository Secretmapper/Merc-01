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
    speed = 0.005
    while(True):
        self.des_vx, self.des_vy = utils.normalize(
            self.track.x - self.x, self.track.y - self.y)
        self.des_vx *= 5
        self.des_vy *= 5
        yield 0
