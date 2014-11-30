from itertools import repeat
import pyglet
import math
import utils
import game.resources as res
import game.constants as CONSTS
import game.globals as GLBS
from game.physics import Spatial_Grid
from pyglet.window import key
from pyglet.graphics import *
import game.graphics
from game.objects import Ship, EnemyShip, Bullet, Sprite, Sensor
import game.behaviours as behaviours
from random import randint
import random
import math
import logic


fps_display = pyglet.clock.ClockDisplay()


class Menu_State(object):

    def __init__(self):
        1


class Play_State(object):

    def __init__(self, win, width, height):
        super(Play_State, self).__init__()
        self.width, self.height = width, height
        self.main_batch = game.graphics.Layer()

        self.camera = game.graphics.Camera(self, zoom=500.0)
        self.camera.track(self.main_batch)
        self.camera.shake(50)

        self.spatial_grid = Spatial_Grid()
        for i in range(CONSTS.CB_TYPES):
            self.spatial_grid.cb_type()
        self.BULLET_CB_TYPE = CONSTS.BULLET_CB_TYPE
        self.ENEMY_CB_TYPE = CONSTS.ENEMY_CB_TYPE
        self.ENEMY_LINE_CB_TYPE = CONSTS.ENEMY_LINE_CB_TYPE

        self.ship = Ship(img=res.player, x=400, y=300, batch=self.main_batch)
        self.bullets = []
        self.enemies = []
        self.enemy_bullets = []

        def spawn_line(x, y):
            # spawn the first enemy of the line (the anchor)
            enemy1 = EnemyShip(behaviours=[[behaviours.link]], img=res.liner, track=self.ship,
                               x=x, y=y, batch=self.main_batch, cb_type=self.ENEMY_LINE_CB_TYPE)
            # start sensor spawn
            sensors = []
            for d in xrange(1, 5):
                sensors.append(Sensor(callbacks=[behaviours.link_sensor], img=res.liner, track=self.ship,
                                      x=x + res.tracker.width * d, y=y, batch=self.main_batch, cb_type=CONSTS.SENSOR_CB_TYPE))
                [self.enemies.append(sensor) for sensor in sensors]

            enemy2 = EnemyShip(behaviours=[[behaviours.link, enemy1, sensors]], img=res.liner, track=self.ship,
                               x=x + 100, y=y, batch=self.main_batch, cb_type=self.ENEMY_LINE_CB_TYPE)
            # end sensor spawn
            self.spatial_grid.add_entity(enemy1, self.ENEMY_LINE_CB_TYPE)
            self.spatial_grid.add_entity(enemy2, self.ENEMY_LINE_CB_TYPE)
            self.enemies.append(enemy1)
            self.enemies.append(enemy2)

        pyglet.clock.set_fps_limit(60)
        pyglet.clock.schedule(self.on_update)

        win.push_handlers(self.ship)
        self.emitter_list = []
        self.spawner = logic.Enemy_Spawner(self)

        p_y = math.sin(self.ship.rotation * math.pi / 180) * \
            self.ship.half_height + self.ship.y
        p_x = -math.cos(self.ship.rotation * math.pi / 180) * \
            self.ship.half_width + self.ship.x
        self.ship_emitter = game.graphics.ParticleSystem(
            p_x, p_y, angle=180 - self.ship.rotation, life=-1, particle_life=50, particles=90)
        self.emitter_list.append(self.ship_emitter)
        self.dead_enemies = []

    def on_mouse_motion(self, x, y, dx, dy):
        self.last_mouse_pos = (x, y)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.TAB:
            CONSTS.DEBUG_MODE = not CONSTS.DEBUG_MODE
        if CONSTS.DEBUG_MODE and symbol == key.GRAVE:
            CONSTS.DEBUG_MODE_OBJ['shoot'] = not CONSTS.DEBUG_MODE_OBJ['shoot']
        if CONSTS.DEBUG_MODE and symbol == key.SPACE:
            CONSTS.DEBUG_MODE_OBJ['play'] = not CONSTS.DEBUG_MODE_OBJ['play']
        if CONSTS.DEBUG_MODE and symbol == key.G:
            if len(GLBS.grid_lst) == 0:
                for i in xrange(int(CONSTS.game_width / CONSTS.cell_size)):
                    GLBS.grid_lst.append(CONSTS.debug_batch.add(2, pyglet.gl.GL_LINES,
                                                                None,
                                                                ('v2f', (
                                                                    i * CONSTS.cell_size, 0, i * CONSTS.cell_size, CONSTS.game_height)),
                                                                ))

                for i in xrange(int(CONSTS.game_height / CONSTS.cell_size)):
                    GLBS.grid_lst.append(CONSTS.debug_batch.add(2, pyglet.gl.GL_LINES,
                                                                None,
                                                                ('v2f', (
                                                                    0, i * CONSTS.cell_size, CONSTS.game_width, i * CONSTS.cell_size)),
                                                                ))
            else:
                for i in GLBS.grid_lst:
                    i.delete()
                    GLBS.grid_lst = []

    def on_update(self, dt):
        if not CONSTS.DEBUG_MODE_OBJ['play']:
            return

        self.spawner.update()
        for enemy in self.spawner.enemies:
            self.enemies.append(enemy)

        if self.ship.shoot and CONSTS.DEBUG_MODE_VAR('shoot'):
            bullet = Bullet(behaviours=[[behaviours.by_angle, self.ship.rotation]], on_bounds_kill=True, img=res.bullet, x=self.ship.x,
                            y=self.ship.y, batch=self.main_batch)
            self.spatial_grid.add_entity(bullet, self.BULLET_CB_TYPE)
            self.bullets.append(bullet)
        self.ship.update(dt)

        max_y = CONSTS.win_height / 2 - \
            (CONSTS.game_height - (CONSTS.win_height / 2 - 40))
        max_x = CONSTS.win_width / 2 - \
            (CONSTS.game_width - (CONSTS.win_width / 2 - 40))
        if not(CONSTS.win_width == CONSTS.game_width):
            self.main_batch.x = utils.lerp(self.main_batch.x,
                                           utils.trunc((CONSTS.win_width / 2 - self.ship.x), max_x, 40), 0.5)
        if not(CONSTS.win_height == CONSTS.game_height):
            self.main_batch.y = utils.lerp(self.main_batch.y,
                                           utils.trunc((CONSTS.win_height / 2 - self.ship.y), max_y, 40), 0.5)

        p_y = math.sin(self.ship.rotation * math.pi / 180) * \
            self.ship.half_height + self.ship.y
        p_x = -math.cos(self.ship.rotation * math.pi / 180) * \
            self.ship.half_width + self.ship.x
        self.ship_emitter.x = p_x
        self.ship_emitter.y = p_y
        self.ship_emitter.angle = self.ship.rotation

        self.camera.update(dt)

        for emitter in self.emitter_list:
            emitter.update()

        for bullet in [b for b in self.bullets if b.dead]:
            self.bullets.remove(bullet)
            self.spatial_grid.remove_entity(bullet, self.BULLET_CB_TYPE)
            if bullet.bounds_death:
                self.emitter_list.append(
                    game.graphics.ParticleSystem(bullet.x, bullet.y, particle_life=20, particles=20 + randint(0, 30)))
            bullet.delete()

        for bullet in [b for b in self.enemy_bullets if b.dead]:
            self.enemy_bullets.remove(bullet)
            if bullet.bounds_death:
                self.emitter_list.append(
                    game.graphics.ParticleSystem(bullet.x, bullet.y, particle_life=20, particles=1 + randint(0, 30)))
            bullet.delete()

        for enemy in [b for b in self.enemies if b.dead]:
            self.emitter_list.append(
                game.graphics.ParticleSystem(enemy.x, enemy.y, **enemy.particle_data))
            self.enemies.remove(enemy)
            enemy.kill()
            self.camera.shake(10)
            self.dead_enemies.append(enemy)
            if enemy.split:
                self.enemies.append(EnemyShip(behaviours=[[behaviours.follow_player]], img=res.tracker, particle_data={'rgb': res.tracker_colors}, track=self.ship,
                                              x=enemy.x + enemy.image.width * 2, y=enemy.y + enemy.image.height * 2, batch=self.main_batch, cb_type=self.ENEMY_CB_TYPE))
                self.enemies.append(EnemyShip(behaviours=[[behaviours.follow_player]], img=res.tracker, particle_data={'rgb': res.tracker_colors}, track=self.ship,
                                              x=enemy.x + enemy.image.width * -2, y=enemy.y + enemy.image.height * -2, batch=self.main_batch, cb_type=self.ENEMY_CB_TYPE))

        for dead in self.dead_enemies:
            dead.update(dt)
        for removal in [b for b in self.dead_enemies if b.remove]:
            self.dead_enemies.remove(removal)
            removal.delete()

        self.spatial_grid.clear()

        self.spatial_grid.add(self.ship, CONSTS.PLAYER_CB_TYPE)

        for bullet in self.bullets:
            bullet.update(dt)
            self.spatial_grid.add(bullet, self.BULLET_CB_TYPE)

        for enemy in self.enemies:
            enemy.update(dt)
            self.enemy_bullets += enemy.bullets
            self.spatial_grid.add(enemy, enemy.cb_type)

        for enemy_bullet in self.enemy_bullets:
            enemy_bullet.update(dt)

            self.spatial_grid.add(enemy_bullet, CONSTS.ENEMY_BULLET_CB_TYPE)

        self.spatial_grid.update()

    def on_draw(self, ):
        glClear(GL_COLOR_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glLoadIdentity()

        self.camera.hud_projection()
        fps_display.draw()

        self.camera.star_projection()
        game.graphics.Starfield.create(
            max_x=CONSTS.game_width + 50, max_y=CONSTS.game_height + 50, size=12, seed=10293, particles=100)

        self.camera.game_projection()

        game.graphics.Starfield.create(
            min_x=-100, min_y=-100, max_x=CONSTS.game_width + 100, max_y=CONSTS.game_height + 100, size=8, seed=99023, particles=200)
        if CONSTS.DEBUG_MODE:
            CONSTS.debug_batch.draw()
        self.main_batch.draw()
        for emitter in self.emitter_list:
            emitter.draw()

        for emitter in [b for b in self.emitter_list if b.dead]:
            self.emitter_list.remove(emitter)
