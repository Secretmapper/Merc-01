import random
import behaviours
from objects import EnemyShip
import resources as res
import constants as CONSTS


def get_bouncer(self, x=False, y=False, spawn=False, delay=0):
    if not x:
        x, y = self.get_spawn_pos()
    behaviours_list = [[behaviours.bounce], [behaviours.delay, delay]]
    enemy = EnemyShip(x=x, y=y, score=25,
                      img=res.splitter,
                      particle_data={'rgb': res.splitter_colors},
                      track=self.ship, batch=self.main_batch, cb_type=CONSTS.ENEMY_CB_TYPE,
                      behaviours=behaviours_list)
    if spawn:
        self.enemies.append(enemy)

    return enemy


def get_tracker(self, x=False, y=False, spawn=False, delay=0):
    if not x:
        x, y = self.get_spawn_pos()
    behaviours_list = [[behaviours.follow_player], [behaviours.delay, delay]]

    enemy = EnemyShip(x=x, y=y, score=50,
                      img=res.tracker,
                      particle_data={'rgb': res.tracker_colors},
                      track=self.ship, batch=self.main_batch, cb_type=CONSTS.ENEMY_CB_TYPE,
                      behaviours=behaviours_list,)
    if spawn:
        self.enemies.append(enemy)

    return enemy


def get_evader(self, x=False, y=False, spawn=False, delay=0):
    if not x:
        x, y = self.get_spawn_pos()
    behaviours_list = [
        [behaviours.follow_player], [behaviours.evade], [behaviours.delay, delay]]

    enemy = EnemyShip(x=x, y=y, score=100,
                      img=res.evader,
                      particle_data={'rgb': res.evader_colors},
                      track=self.ship, batch=self.main_batch, cb_type=CONSTS.ENEMY_CB_TYPE,
                      behaviours=behaviours_list,)
    if spawn:
        self.enemies.append(enemy)

    return enemy


def spawn_corner(self):

    for i in xrange(1, 10):
        self.callbacks.append(
            [get_tracker, 5, {'spawn': True, 'self': self, 'x': 10, 'y': 10, 'delay': i * 10}])
    for i in xrange(1, 10):
        self.callbacks.append(
            [get_tracker, 5, {'spawn': True, 'self': self, 'x': 10, 'y': CONSTS.game_height - 10, 'delay': i * 10}])
    for i in xrange(1, 10):
        self.callbacks.append(
            [get_tracker, 5, {'spawn': True, 'self': self, 'x': CONSTS.game_width, 'y': CONSTS.game_height - 10, 'delay': i * 10}])
    for i in xrange(1, 10):
        self.callbacks.append(
            [get_tracker, 5, {'spawn': True, 'self': self, 'x': CONSTS.game_width, 'y': 10, 'delay': i * 10}])


def clear_spawn(lst):
    for dead in [b for b in lst if b.dead]:
        lst.remove(dead)


def get_spawn_list(points, choice):
    weight_sum = sum(i[2] for i in choice)

    to_spawn = []
    while(points > 0 and len(choice) > 0):
        random.randint(0, weight_sum)
        # create a list of indexes with weights. use that index for choice
        ind = random.choice(
            sum([[i] * choice[i][2] for i in xrange(len(choice))], []))

        # use spec, remove points
        spec = choice[ind]
        to_spawn.append(spec[0])
        points -= spec[1]

        # remove from tail choices with lower points
        lchoice = len(choice)
        choice = filter(lambda x: x[1] <= points, choice)
        # if len is unequal, then choice is changed, hence weight is changed
        if not lchoice == len(choice):
            weight_sum = sum(i[2] for i in choice)
    return to_spawn


def one(self):

    spawned = [get_bouncer(self)]
    self.enemies.extend(spawned)
    while(len(spawned) > 0):
        clear_spawn(spawned)
        yield True
    spawned = [get_bouncer(self) for i in xrange(2)]
    self.enemies.extend(spawned)

    points = 100

    # type - points - weight
    choice = [
        (get_bouncer, 25, 50),
        (get_tracker, 50, 30),
        (get_evader,  100, 20)
    ]
    to_spawn = get_spawn_list(points, choice)

    rate = 1.0
    while(True):
        if random.randint(0, 100) <= random.expovariate(1 / rate):
            x, y = self.get_spawn_pos()
            fn = to_spawn.pop()
            self.enemies.append(fn(self, x, y))
        yield True if len(to_spawn) > 0 else False


def two(self):
    spawn_corner(self)
    while(True):

        yield True
