import random
from objects import EnemyShip, Sensor
import behaviours
import resources as res
import constants as CONSTS
import math
import pyglet


class Enemy_Spawner(object):

    def __init__(self, state):
        super(Enemy_Spawner, self).__init__()
        self.enemies = []
        self.spwn_chance = 1
        self.ship = state.ship
        self.main_batch = state.main_batch
        self.state = state
        self.callbacks = []

    def update(self, dt):
        self.enemies = []

        cb_to_remove = []

        # We are just doing the callbacks here
        # callback is an array containing [callback, delay, parameters]
        for callback in self.callbacks:
            callback[1] = callback[1] - 1
            if callback[1] <= 0:
                if callback[2]:
                    callback[0](**callback[2])
                else:
                    callback[0]()

        self.callbacks[:] = [cb for cb in self.callbacks if cb[1] > 0]

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

        if self.spwn_chance >= random.randint(0, 100) and len(self.state.enemies) <= 0 and len(self.callbacks) <= 0:
            self.spwn_chance = 0

            sin_params = random.choice([
                {'c_x': -CONSTS.game_width},
                {'c_x': CONSTS.game_width},
                {'c_y': -CONSTS.game_height},
                {'c_y': CONSTS.game_height},
            ])

            self.callbacks.append(
                [self.spawn_sin, 5, sin_params])

        if self.spwn_chance > 20:
            self.spwn_chance += 0.000005

    def spawn_sin(self, c_x=False, c_y=False):
        angles = [a * math.pi / 180 for a in range(1, 320, 20)]
        angles_ln = len(angles) / 100.0

        sin_dir = 0

        if c_x:
            sin_dir = 180 if c_x >= CONSTS.game_width else 0
        if c_y:
            sin_dir = 90 if c_y >= CONSTS.game_height else 270

        for i in xrange(len(angles)):
            a = angles[i]
            x = i * 50 + c_x if c_x else self.ship.x
            y = i * 50 + c_y if c_y else self.ship.y

            behaviours_list = [
                [behaviours.by_sin, sin_dir], [behaviours.exits]]
            enemy = EnemyShip(behaviours=behaviours_list, img=res.tracker, particle_data={'rgb': res.tracker_colors}, track=self.ship,
                              x=x, y=y, batch=self.main_batch, cb_type=CONSTS.ENEMY_CB_TYPE)
            self.enemies.append(enemy)

    def spawn_circle(self, dt=0):
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
