import random
from objects import EnemyShip, Sensor
import behaviours
import resources as res
import constants as CONSTS
import math
import pyglet
import levels


class Enemy_Spawner(object):

    def __init__(self, state):
        super(Enemy_Spawner, self).__init__()
        self.enemies = []
        self.spwn_chance = 1
        self.ship = state.ship
        self.main_batch = state.main_batch
        self.state = state
        self.callbacks = []
        self.play_time = 0
        self.level = levels.one(self)

    def get_spawn_pos(self, bound=10):
        x, y = self.ship.x, self.ship.y
        while (self.ship.x - x) ** 2 + (self.ship.y - y) ** 2 <= 250:
            x = random.randint(bound, CONSTS.game_width - bound)
            y = random.randint(bound, CONSTS.game_height - bound)
        return (x, y)

    def update(self, dt):
        self.enemies = []

        cb_to_remove = []

        # We are just doing the callbacks here
        # callback is an array containing [callback, delay, parameters]
        for callback in self.callbacks:
            callback[1] = callback[1] - 1
            if callback[1] <= 0:
                if len(callback) >= 3:
                    print callback[2]
                    callback[0](**callback[2])
                else:
                    callback[0]()

        self.callbacks[:] = [cb for cb in self.callbacks if cb[1] > 0]

        self.play_time += 1

        if not self.level.next():
            self.level = levels.two(self)

        sin_params = random.choice([
            {'c_x': -CONSTS.game_width},
            {'c_x': CONSTS.game_width},
            {'c_y': -CONSTS.game_height},
            {'c_y': CONSTS.game_height},
        ])

    def spawn_enemy(self, x, y, e_type, delay=0, alpha=50):
        behaviours_list = [[behaviours.evade],
                           [behaviours.follow_player, 3],
                           [behaviours.delay, delay, alpha]]
        enemy = EnemyShip(x=x, y=y, behaviours=behaviours_list, **e_type)
        self.enemies.append(enemy)

    def spawn_line(self, x=None, y=None):
        if not x:
            x = random.randint(150, CONSTS.game_width - 150)
            y = random.randint(150, CONSTS.game_height - 150)

        # spawn the first enemy of the line (the anchor)
        enemy1 = EnemyShip(behaviours=[[behaviours.link], [behaviours.delay, 0]], img=res.liner, track=self.ship,
                           x=x, y=y, batch=self.main_batch, cb_type=CONSTS.ENEMY_LINE_CB_TYPE)
        # start sensor spawn
        sensors = []
        for d in xrange(1, 4):
            sensors.append(Sensor(callbacks=[behaviours.link_sensor], img=res.liner, track=self.ship,
                                  x=x + res.tracker.width * d, y=y, batch=self.main_batch, cb_type=CONSTS.SENSOR_CB_TYPE))
        for sensor in sensors:
            sensor.scale = 0.5
            self.enemies.append(sensor)

        enemy2 = EnemyShip(behaviours=[[behaviours.link, enemy1, sensors], [behaviours.delay, 0]], img=res.liner, track=self.ship,
                           x=x + 100, y=y, batch=self.main_batch, cb_type=CONSTS.ENEMY_LINE_CB_TYPE)
        # end sensor spawn
        self.enemies.append(enemy1)
        self.enemies.append(enemy2)

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
            enemy = EnemyShip(behaviours=behaviours_list, img=res.evader, particle_data={'rgb': res.evader_colors}, track=self.ship,
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
                [behaviours.follow_player, 1 + float(a) / 1000], [behaviours.delay, a * 10], [behaviours.split]]
            enemy = EnemyShip(behaviours=behaviours_list, img=res.splitter, particle_data={'rgb': res.splitter_colors}, track=self.ship,
                              x=x, y=y, batch=self.main_batch, cb_type=CONSTS.ENEMY_CB_TYPE)
            self.enemies.append(enemy)
