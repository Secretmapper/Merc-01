def bounce(self):
    speed = 10
    while(True):
        self.x += self.dir_x * speed
        self.y += self.dir_y * speed

        if self.y <= self.min_y or self.y >= self.max_y:
            self.dir_y = -self.dir_y
        elif self.x <= self.min_x or self.x >= self.max_x:
            self.dir_x = -self.dir_x
        yield 0


def follow_player(self):
    speed = 0.005
    while(True):
        self.vel_x += (self.track.x - self.x) * speed
        self.vel_y += (self.track.y - self.y) * speed
        yield 0
