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

        self.camera.update(dt)

        for emitter in self.emitter_list:
            emitter.update()

        for bullet in [b for b in self.bullets if b.dead]:
            self.bullets.remove(bullet)
            self.spatial_grid.remove_entity(bullet, self.BULLET_CB_TYPE)
            if bullet.bounds_death:
                self.emitter_list.append(
                    game.graphics.ParticleSystem(bullet.x, bullet.y, life=20, particles=20 + randint(0, 30)))
            bullet.delete()

        for bullet in [b for b in self.enemy_bullets if b.dead]:
            self.enemy_bullets.remove(bullet)
            if bullet.bounds_death:
                self.emitter_list.append(
                    game.graphics.ParticleSystem(bullet.x, bullet.y, life=20, particles=1 + randint(0, 30)))
            bullet.delete()

        for enemy in [b for b in self.enemies if b.dead]:
            self.emitter_list.append(
                game.graphics.ParticleSystem(enemy.x, enemy.y, **enemy.particle_data))
            self.enemies.remove(enemy)
            enemy.kill()
            self.camera.shake(5)
            if enemy.split:
                self.enemies.append(EnemyShip(behaviours=[[behaviours.follow_player]], img=res.tracker, track=self.ship,
                                              x=enemy.x + enemy.image.width * 2, y=enemy.y + enemy.image.height * 2, batch=self.main_batch, cb_type=self.ENEMY_CB_TYPE))
                self.enemies.append(EnemyShip(behaviours=[[behaviours.follow_player]], img=res.tracker, track=self.ship,
                                              x=enemy.x + enemy.image.width * -2, y=enemy.y + enemy.image.height * -2, batch=self.main_batch, cb_type=self.ENEMY_CB_TYPE))

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

        pyglet.graphics.draw_indexed(4, pyglet.gl.GL_TRIANGLES,
                                     [0, 1, 2, 0, 2, 3],
                                     ('v2i', (0, 0,
                                              0, CONSTS.game_height,
                                              CONSTS.game_width, CONSTS.game_height,
                                              CONSTS.game_width, 0)),
                                     ('c4B', (50, 50, 50, 255) * 4))

        self.camera.hud_projection()
        fps_display.draw()

        self.camera.game_projection()
        if CONSTS.DEBUG_MODE:
            CONSTS.debug_batch.draw()
        self.main_batch.draw()
        for emitter in self.emitter_list:
            emitter.draw()

        for emitter in [b for b in self.emitter_list if b.dead]:
            self.emitter_list.remove(emitter)
