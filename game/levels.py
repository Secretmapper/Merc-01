import random
import behaviours
from objects import EnemyShip, Sensor
import resources as res
import constants as CONSTS


def spawn_line(self, x=None, y=None):
    x, y = self.get_spawn_pos(150)

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
    return False


def get_bouncer(self, x=False, y=False, spawn=False, delay=0):
    if not x:
        x, y = self.get_spawn_pos()
    behaviours_list = [[behaviours.bounce], [behaviours.delay, delay]]
    enemy = EnemyShip(x=x, y=y, score=25,
                      img=res.bouncer,
                      particle_data={'rgb': res.bouncer_colors},
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


def get_splitter(self, x=False, y=False, spawn=False, delay=0):
    if not x:
        x, y = self.get_spawn_pos()
    behaviours_list = [
        [behaviours.split], [behaviours.follow_player], [behaviours.delay, delay]]

    enemy = EnemyShip(x=x, y=y, score=25,
                      img=res.splitter,
                      particle_data={'rgb': res.splitter_colors},
                      track=self.ship, batch=self.main_batch, cb_type=CONSTS.ENEMY_CB_TYPE,
                      behaviours=behaviours_list,)
    if spawn:
        self.enemies.append(enemy)

    return enemy


def get_squeezer(self, x=False, y=False, spawn=False, delay=0):
    if not x:
        x, y = self.get_spawn_pos()
    behaviours_list = [
        [behaviours.zip], [behaviours.delay, delay]]

    enemy = EnemyShip(x=x, y=y, score=50,
                      img=res.squeezer,
                      particle_data={'rgb': res.squeezer_colors},
                      track=self.ship, batch=self.main_batch, cb_type=CONSTS.ENEMY_CB_TYPE,
                      behaviours=behaviours_list,)
    if spawn:
        self.enemies.append(enemy)

    return enemy


def get_flanker(self, x=False, y=False, spawn=False, delay=0, horizontal=True):
    if not x:
        x, y = self.get_spawn_pos()
    behaviours_list = [
        [behaviours.flank, horizontal], [behaviours.delay, delay]]

    enemy = EnemyShip(x=x, y=y, score=50,
                      img=res.squeezer,
                      particle_data={'rgb': res.squeezer_colors},
                      track=self.ship, batch=self.main_batch, cb_type=CONSTS.ENEMY_CB_TYPE,
                      behaviours=behaviours_list,)
    if spawn:
        self.enemies.append(enemy)

    return enemy


def get_blackhole(self, x=False, y=False, spawn=False, delay=0):
    if not x:
        x, y = self.get_spawn_pos()
    behaviours_list = [
        [behaviours.pulse], [behaviours.attract], [behaviours.black_hole], [behaviours.delay, delay]]

    enemy = EnemyShip(x=x, y=y, score=500,
                      img=res.black_hole,
                      particle_data={'rgb': res.black_hole_colors},
                      track=self.ship, batch=self.main_batch, cb_type=CONSTS.ENEMY_BLACK_HOLE,
                      behaviours=behaviours_list,
                      callbacks=[behaviours.black_hole_cb])

    if spawn:
        self.enemies.append(enemy)

    return enemy


# 1800
def spawn_corner(self, n=8, cb=get_tracker):

    for i in xrange(1, n + 1):
        self.callbacks.append(
            [cb, 5 + i * random.randint(1, 2), {'spawn': True, 'self': self, 'x': 10, 'y': 10, 'delay': i * 10}])
    for i in xrange(1, n + 1):
        self.callbacks.append(
            [cb, 5 + i * random.randint(1, 2), {'spawn': True, 'self': self, 'x': 10, 'y': CONSTS.game_height - 10, 'delay': i * 10}])
    for i in xrange(1, n + 1):
        self.callbacks.append(
            [cb, 5 + i * random.randint(1, 2), {'spawn': True, 'self': self, 'x': CONSTS.game_width, 'y': CONSTS.game_height - 10, 'delay': i * 10}])
    for i in xrange(1, n + 1):
        self.callbacks.append(
            [cb, 5 + i * random.randint(1, 2), {'spawn': True, 'self': self, 'x': CONSTS.game_width, 'y': 10, 'delay': i * 10}])


def spawn_zipping(self):
    x_mod = 100 if self.ship.x > CONSTS.game_width / 2 else -100
    y_mod = 0
    if self.ship.y + 5 * 30 > CONSTS.game_height:
        y_mod -= 5 * 30
    elif self.ship.y + 5 * 30 < 0:
        y_mod -= 5 * 30
    to_spawn = []
    for i in xrange(-5, 5):
        params = {'self': self, 'x': self.ship.x +
                  x_mod, 'y': self.ship.y + y_mod + i * 30, 'delay': (i + 5) * 5}
        to_spawn.append(get_squeezer(**params))
    return to_spawn


def spawn_flanker(self, horizontal=True):
    to_spawn = []
    if horizontal:
        for i in xrange(1, int(CONSTS.game_height / res.squeezer.height)):
            to_spawn.append(
                get_flanker(self, x=res.squeezer.width, y=i * res.squeezer.height, horizontal=horizontal))
    else:
        for i in xrange(1, int(CONSTS.game_width / res.squeezer.width)):
            to_spawn.append(
                get_flanker(self, x=i * res.squeezer.width, y=res.squeezer.height, horizontal=horizontal))
    return to_spawn


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
        to_spawn.append((spec[0], None if len(spec) == 3 else spec[3]))
        points -= spec[1]

        # remove from tail choices with lower points
        lchoice = len(choice)
        choice = filter(lambda x: x[1] <= points, choice)
        # if len is unequal, then choice is changed, hence weight is changed
        if not lchoice == len(choice):
            weight_sum = sum(i[2] for i in choice)
    random.shuffle(to_spawn)
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
        (get_splitter, 50, 30),
        (get_evader,  100, 20),
        (spawn_corner, 400, 10, [1, get_evader]),
    ]
    to_spawn = get_spawn_list(points, choice)

    rate = 1.0
    while(len(to_spawn) > 0):
        if random.randint(0, 100) <= random.expovariate(1 / rate):
            x, y = self.get_spawn_pos()
            fn, params = to_spawn.pop()
            if params:
                fn(self, *params)
            else:
                self.enemies.append(fn(self, x, y))
        yield True
    yield one_mid_two


def one_mid_two(self):
    points = 1000
    choice = [(get_bouncer, 25, 50),
              (get_tracker, 50, 30),
              (get_evader,  100, 20)]
    to_spawn = get_spawn_list(points, choice)

    rate = 1.0
    while(len(to_spawn) > 0):
        if len(to_spawn) > 0 and random.randint(0, 100) <= random.expovariate(1 / rate):
            x, y = self.get_spawn_pos()
            fn, params = to_spawn.pop()
            if params:
                fn(self, *params)
            else:
                self.enemies.append(fn(self, x, y))
        yield True
    yield two


def two(self):
    points = 0
    wave_spawns = []
    c = [[0] * 2 + [1] * 2 + [2]]
    c = random.choice(sum(c, []))
    if c == 0:
        # adds everything to wave_spawns
        def add_to_spawn(horizontal):
            lst = spawn_zipping(self)
            wave_spawns.extend(lst)
            self.state.enemies.extend(lst)

        for x in xrange(3):
            for i in xrange(180):
                yield True
            self.callbacks.append(
                [add_to_spawn, 5, {'horizontal': True if x % 2 == 0 else False}])
        points = 500
    elif c == 1:
        spawn_corner(self)
        for i in xrange(360):
            yield True
        points = 200
    else:
        points = 2000

    def bouncer_bundle(self, x, y):
        x, y = self.get_spawn_pos(50)

        return [get_bouncer(self, x, y) for i in xrange(2)]

    choice = [(bouncer_bundle, 100, 20),
              (get_bouncer, 25, 50),
              (get_tracker, 50, 30),
              (get_evader,  100, 20)]
    to_spawn = get_spawn_list(points, choice)

    rate = 1.0
    while(len(to_spawn) > 0):
        clear_spawn(wave_spawns)
        if len(to_spawn) > 0 and random.randint(0, 100) <= random.expovariate(1 / rate):
            x, y = self.get_spawn_pos()
            fn, params = to_spawn.pop()
            if params:
                fn(self, *params)
            else:
                ret = fn(self, x, y)
                if ret:  # spawn_line hack
                    # incredible hackishness (bundles/list)
                    if hasattr(ret, '__len__'):
                        self.enemies.extend(ret)
                    else:
                        self.enemies.append(ret)
        yield True
    if self.state.target_score >= 7500:
        yield two_mid_three
    else:
        yield two


def two_mid_three(self):
    get_blackhole(self, spawn=True)
    for i in xrange(240):
        yield True
    yield three


def three(self):
    for i in xrange(3):
        get_blackhole(self, spawn=True)
        spawn_line(self)
        points = 500
        choice = [(get_bouncer, 25, 50),
                  (get_tracker, 50, 30),
                  (get_evader,  100, 20)]
        to_spawn = get_spawn_list(points, choice)

        rate = 2.0
        while(len(to_spawn) > 0):
            if len(to_spawn) > 0 and random.randint(0, 100) <= random.expovariate(1 / rate):
                x, y = self.get_spawn_pos()
                fn, params = to_spawn.pop()
                if params:
                    fn(self, *params)
                else:
                    self.enemies.append(fn(self, x, y))
            yield True
        yield True
    yield four


def four(self):
    x, y = self.get_spawn_pos()
    behaviours_list = [[behaviours.delay], [behaviours.spin]] + \
        [[behaviours.shoot_fire, ang] for ang in range(0, 360, 90)]

    enemy = EnemyShip(x=x, y=y, score=300,
                      img=res.cleaner,
                      particle_data={'rgb': res.cleaner_colors},
                      track=self.ship, batch=self.main_batch, cb_type=CONSTS.ENEMY_CB_TYPE,
                      behaviours=behaviours_list)
    self.enemies.append(enemy)
    yield five


def five(self):
    points = 3500

    def bouncer_bundle(self, x, y):
        x, y = self.get_spawn_pos(50)

        return [get_bouncer(self, x, y) for i in xrange(10)]

    choice = [
        (bouncer_bundle, 50, 30),
        (get_tracker, 50, 60),
        (spawn_line, 100, 50),
        (get_splitter, 50, 50),
        (get_evader,  100, 40),
        (get_blackhole, 200, 30),
        (self.spawn_sin, 400, 20, ['old']),  # old not working with append
        (spawn_corner, 800, 21, [5, get_evader]),
    ]
    to_spawn = get_spawn_list(points, choice)

    rate = 1.0
    play_time = 0
    while(len(to_spawn) > 0):
        if random.randint(0, 100) <= random.expovariate(1 / rate) and len(self.state.enemies) <= 30:
            x, y = self.get_spawn_pos()
            fn, params = to_spawn.pop()
            if params:
                if params[0] == 'old':  # hack, for old (spawn_sin)
                    fn()
                else:
                    fn(self, *params)
            else:

                ret = fn(self, x, y)
                if ret:  # spawn_line hack
                    # incredible hackishness (bundles/list)
                    if hasattr(ret, '__len__'):
                        self.enemies.extend(ret)
                    else:
                        self.enemies.append(ret)
        play_time += 1
        yield True
    yield six


def six(self):

    x, y = self.get_spawn_pos()
    behaviours_list = [[behaviours.delay], [behaviours.spin]] + \
        [[behaviours.shoot_fire, ang] for ang in range(0, 360, 90)]

    enemy = EnemyShip(x=x, y=y, score=300,
                      img=res.cleaner,
                      particle_data={'rgb': res.cleaner_colors},
                      track=self.ship, batch=self.main_batch, cb_type=CONSTS.ENEMY_CB_TYPE,
                      behaviours=behaviours_list)
    self.enemies.append(enemy)

    def evader_bundle(self, x, y):
        x, y = self.get_spawn_pos(50)

        return [get_bouncer(self, x, y) for i in xrange(3)]

    choice = [
        (evader_bundle, 75, 30),
        (get_tracker, 50, 60),
        (spawn_line, 100, 50),
        (get_splitter, 50, 50),
        (get_evader,  100, 40),
        (get_blackhole, 200, 30),
        (spawn_corner, 1000, 20, [5, get_evader]),
        # old not working with append
        (self.spawn_sin, 400, 10, ['old'])
    ]
    to_spawn = get_spawn_list(points, choice)

    rate = 1.0
    play_time = 0
    while(len(to_spawn) > 0):
        if random.randint(0, 100) <= random.expovariate(1 / rate) and len(self.state.enemies) <= 30:
            x, y = self.get_spawn_pos()
            fn, params = to_spawn.pop()
            if params:
                if params[0] == 'old':  # hack, for old (spawn_sin)
                    fn()
                else:
                    fn(self, *params)
            else:

                ret = fn(self, x, y)
                if ret:  # spawn_line hack
                    # incredible hackishness (bundles/list)
                    if hasattr(ret, '__len__'):
                        self.enemies.extend(ret)
                    else:
                        self.enemies.append(ret)
        play_time += 1
        yield True
    yield five
