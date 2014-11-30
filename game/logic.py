import random
from objects import EnemyShip, Sensor
import behaviours
import resources as res
import constants as CONSTS
import math


class Enemy_Spawner(object):

    def __init__(self, state):
        super(Enemy_Spawner, self).__init__()
        self.enemies = []
        self.spwn_chance = 1
        self.ship = state.ship
        self.main_batch = state.main_batch
        self.state = state

    def update(self):
        self.enemies = []

        def spawn_line(x, y):
            # spawn the first enemy of the line (the anchor)
            enemy1 = EnemyShip(behaviours=[[behaviours.link]], img=res.liner, track=self.ship,
                               x=x, y=y, batch=self.main_batch, cb_type=CONSTS.ENEMY_LINE_CB_TYPE)
            # start sensor spawn
            sensors = []
            for d in xrange(1, 5):
                sensors.append(Sensor(callbacks=[behaviours.link_sensor], img=res.liner, track=self.ship,
                                      x=x + res.tracker.width * d, y=y, batch=self.main_batch, cb_type=CONSTS.SENSOR_CB_TYPE))
                [self.enemies.append(sensor) for sensor in sensors]

            enemy2 = EnemyShip(behaviours=[[behaviours.link, enemy1, sensors]], img=res.liner, track=self.ship,
                               x=x + 100, y=y, batch=self.main_batch, cb_type=CONSTS.ENEMY_LINE_CB_TYPE)
            # end sensor spawn
            self.enemies.append(enemy1)
            self.enemies.append(enemy2)

        if self.spwn_chance >= random.randint(0, 100) and len(self.state.enemies) <= 0:
            self.spwn_chance = 0
            self.spawn_circle()
            spawn_line(random.randint(0, 400), random.randint(0, 300))

        if self.spwn_chance > 20:
            self.spwn_chance += 0.000005

    def spawn_circle(self):
        angles = [a * math.pi / 180 for a in range(1, 360, 20)]
        angles_ln = len(angles) / 100.0

        for a in angles:
            # x2 + y2 = r2
            x = math.cos(a) * 200 + self.ship.x
            y = math.sin(a) * 200 + self.ship.y

            behaviours_list = [
                [behaviours.follow_player, 1 + float(a) / 1000], [behaviours.delay, a * 2, float(a) / angles_ln], [behaviours.split]]
            enemy = EnemyShip(behaviours=behaviours_list, img=res.splitter, particle_data={'rgb': res.splitter_colors}, track=self.ship,
                              x=x, y=y, batch=self.main_batch, cb_type=CONSTS.ENEMY_CB_TYPE)
            self.enemies.append(enemy)
