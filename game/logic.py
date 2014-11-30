import random
from objects import EnemyShip
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
        if self.spwn_chance >= random.randint(0, 100) and len(self.state.enemies) <= 0:
            self.spwn_chance = 0
            self.spawn_circle()

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
                [behaviours.follow_player, 1 + float(a) / 1000], [behaviours.split], [behaviours.delay, a * 2, float(a) / angles_ln]]
            enemy = EnemyShip(behaviours=behaviours_list, img=res.splitter, particle_data={'rgb': res.splitter_colors}, track=self.ship,
                              x=x, y=y, batch=self.main_batch, cb_type=CONSTS.ENEMY_CB_TYPE)
            self.enemies.append(enemy)
