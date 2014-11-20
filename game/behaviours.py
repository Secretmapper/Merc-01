def bounce(self):
    speed = 10
    while(True):
        self.x += self.dir_x * speed * self.xdt
        self.y += self.dir_y * speed * self.xdt

        if self.y <= self.min_y or self.y >= self.max_y:
            self.dir_y = -self.dir_y
        elif self.x <= self.min_x or self.x >= self.max_x:
            self.dir_x = -self.dir_x
        yield 0


def follow_player(self):
    speed = 0.05
    while(True):
        self.x += (self.track.x - self.x) * speed * self.xdt
        self.y += (self.track.y - self.y) * speed * self.xdt
        yield 0
