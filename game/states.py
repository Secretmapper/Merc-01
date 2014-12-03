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
import locale

fps_display = pyglet.clock.ClockDisplay()


class Menu_State(object):

    def __init__(self):
        1


class Play_State(object):

    def __init__(self, win, width, height):
        super(Play_State, self).__init__()
        self.width, self.height = width, height
        self.main_batch = game.graphics.Layer()
        self.hud_batch = game.graphics.Layer()

        self.camera = game.graphics.Camera(self, zoom=500.0)
        self.camera.track(self.main_batch)
        self.camera.shake(50)

        self.spatial_grid = Spatial_Grid()
        for i in range(CONSTS.CB_TYPES):
            self.spatial_grid.cb_type()
        self.BULLET_CB_TYPE = CONSTS.BULLET_CB_TYPE
        self.ENEMY_CB_TYPE = CONSTS.ENEMY_CB_TYPE
        self.ENEMY_LINE_CB_TYPE = CONSTS.ENEMY_LINE_CB_TYPE

        self.health_bars = []

        health_bars = {'batch': self.hud_batch}
        health_bar_coords = [{'img': res.health_bar, 'x': res.health_bar.width / 2 + 50,
                              'y': CONSTS.win_height - res.health_bar.height / 2 - 50},
                             {'img': res.health_bar, 'x': res.health_bar.width / 2 + 75,
                              'y': CONSTS.win_height - res.health_bar.height / 2 - 50},
                             {'img': res.health_bar, 'x': res.health_bar.width / 2 + 100,
                              'y': CONSTS.win_height - res.health_bar.height / 2 - 50},
                             {'img': res.health_bar_un, 'x': res.health_bar.width / 2 + 125,
                              'y': CONSTS.win_height - res.health_bar.height / 2 - 50},
                             {'img': res.health_bar_un, 'x': res.health_bar.width / 2 + 150,
                              'y': CONSTS.win_height - res.health_bar.height / 2 - 50}]
        [self.health_bars.append(pyglet.sprite.Sprite(
            **dict(health_bars.items() + coords.items()))) for coords in health_bar_coords]

        locale.setlocale(locale.LC_ALL, 'en_US')
        self.score = 0
        self.target_score = 0
        self.score_text = pyglet.text.Label(text=locale.format("%d", self.score, grouping=True),
                                            font_name='04b03',
                                            font_size=18,
                                            anchor_x='left',
                                            batch=self.hud_batch,
                                            color=(87, 198, 211, 200),
                                            x=50, y=CONSTS.win_height - 100)

        self.ship = Ship(img=res.player, x=200, y=300, batch=self.main_batch)
        self.bullets = []
        self.enemies = []
        self.enemy_bullets = []

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

        def prini(dt):
            print pyglet.clock.get_fps()
        pyglet.clock.schedule_once(prini, 10)

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

        self.spawner.update(dt)
        for enemy in self.spawner.enemies:
            self.enemies.append(enemy)

        if self.ship.shoot and CONSTS.DEBUG_MODE_VAR('shoot'):
            if self.ship.shoot_type == 1:
                for i in [-1, 0, 1]:
                    bullet = Bullet(behaviours=[[behaviours.by_angle, self.ship.rotation + i * 10]], on_bounds_kill=True, img=res.bullet, x=self.ship.x,
                                    y=self.ship.y, batch=self.main_batch, rotation=self.ship.rotation)
                    self.spatial_grid.add_entity(bullet, self.BULLET_CB_TYPE)
                    self.bullets.append(bullet)
            if self.ship.shoot_type == 2:
                if len(self.enemies) >= 1 and self.enemies[0].trackable:
                    bullet = Bullet(behaviours=[[behaviours.chase]], on_bounds_kill=True, img=res.bullet, x=self.ship.x,
                                    y=self.ship.y, batch=self.main_batch, track=self.enemies[0], rotation=self.ship.rotation)
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
            self.camera.ax = self.ship.x
        if not(CONSTS.win_height == CONSTS.game_height):
            self.main_batch.y = utils.lerp(self.main_batch.y,
                                           utils.trunc((CONSTS.win_height / 2 - self.ship.y), max_y, 40), 0.5)
            self.camera.ay = self.ship.x

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

        for enemy in [b for b in self.enemies if b.dead or b.is_outside_of_screen]:
            self.enemies.remove(enemy)
            enemy.kill()
            if enemy.dead:
                self.emitter_list.append(
                    game.graphics.ParticleSystem(enemy.x, enemy.y, **enemy.particle_data))
                self.camera.shake(10)
                self.dead_enemies.append(enemy)
                if enemy.split:
                    self.enemies.append(EnemyShip(behaviours=[[behaviours.follow_player]], img=res.tracker, particle_data={'rgb': res.tracker_colors}, track=self.ship,
                                                  x=enemy.x + enemy.image.width * 2, y=enemy.y + enemy.image.height * 2, batch=self.main_batch, cb_type=self.ENEMY_CB_TYPE))
                    self.enemies.append(EnemyShip(behaviours=[[behaviours.follow_player]], img=res.tracker, particle_data={'rgb': res.tracker_colors}, track=self.ship,
                                                  x=enemy.x + enemy.image.width * -2, y=enemy.y + enemy.image.height * -2, batch=self.main_batch, cb_type=self.ENEMY_CB_TYPE))

                self.target_score += 100
            else:
                enemy.delete()

        if self.target_score > self.score:
            self.score = utils.lerp(self.score, self.target_score, 0.2)
            self.score_text.text = locale.format(
                "%d", round(self.score), grouping=True)

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
            if enemy.bullets:
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

        self.camera.star_projection()
        game.graphics.Starfield.create(
            max_x=CONSTS.game_width + 50, max_y=CONSTS.game_height + 50, size=16, seed=10293, particles=100)

        self.camera.game_projection()

        game.graphics.Starfield.create(
            min_x=-100, min_y=-100, max_x=CONSTS.game_width + 100, max_y=CONSTS.game_height + 100, size=12, seed=99023, particles=200)
        if CONSTS.DEBUG_MODE:
            CONSTS.debug_batch.draw()
        self.main_batch.draw()
        for emitter in self.emitter_list:
            emitter.draw()

        for emitter in [b for b in self.emitter_list if b.dead]:
            self.emitter_list.remove(emitter)

        self.camera.hud_project()
        particle_pos = []
        colors = []

        ratio = 0.3

        max_x = CONSTS.win_width - 20
        max_y = CONSTS.win_height - 20

        min_x = max_x - int(CONSTS.win_width * ratio)
        min_y = max_y - int(CONSTS.win_height * ratio)

        minimap = (min_x, min_y,
                   min_x, max_y,
                   max_x, max_y,
                   max_x, min_y)

        pyglet.graphics.draw_indexed(4, pyglet.gl.GL_TRIANGLES,
                                     [0, 1, 2, 0, 2, 3],
                                     ('v2i', minimap),
                                     ('c4B', (88, 198, 211, 30) * 4))

        """
        We initialize our positions, colors through a double for list comprehension
        We need this part of the code to be VERY fast
        """

        # for i in self.enemies:
        # particle_pos.append(
        #    (max_x + ((234.0 / CONSTS.game_width) * i.x) - 234) - 2.5)
        # particle_pos.append(
        #    max_y + ((180.0 / CONSTS.game_height) * i.y) - 180)
        particle_pos = [
            pos for enemy in self.enemies if enemy.show_on_radar for pos in [(max_x + ((234.0 / CONSTS.game_width) * enemy.x) - 234) - 2.5,
                                                                             max_y + ((180.0 / CONSTS.game_height) * enemy.y) - 180]]
        colors = [c for enemy in self.enemies if enemy.show_on_radar for c in [
            1.0, 0.0, 0.0, 1.0]]

        particle_pos.append(
            (max_x + ((234.0 / CONSTS.game_width) * self.ship.x) - 234) - 2.5)
        particle_pos.append(
            max_y + ((180.0 / CONSTS.game_height) * self.ship.y) - 180)
        colors.extend([0, 1.0, 0, 1.0])

        game.graphics.Drawer().draw(particle_pos, colors)

        glBlendFunc(GL_ONE, GL_ONE_MINUS_SRC_COLOR)

        if CONSTS.DEBUG_MODE:
            pyglet.graphics.draw_indexed(4, pyglet.gl.GL_TRIANGLES,
                                         [0, 1, 2, 0, 2, 3],
                                         ('v2i', (0, 0,
                                                  0, CONSTS.win_height,
                                                  CONSTS.win_width, CONSTS.win_height,
                                                  CONSTS.win_width, 0)),
                                         ('c4B', (50, 50, 50, 255) * 4))
        fps_display.draw()
        self.camera.hud_projection()
        self.hud_batch.draw()
