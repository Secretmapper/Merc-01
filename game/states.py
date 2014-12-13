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
        self.main_batch = pyglet.graphics.Batch()
        self.title_text = pyglet.text.Label(text="Merc - 01",
                                            font_name='04b03',
                                            font_size=96,
                                            anchor_x='center',
                                            batch=self.main_batch,
                                            color=(255, 255, 255, 200),
                                            x=CONSTS.win_width / 2, y=CONSTS.win_height - 200)

        self.selected_i = 0
        self.title_text = pyglet.text.Label(text="Start",
                                            font_name='04b03',
                                            font_size=24,
                                            anchor_x='center',
                                            anchor_y='center',
                                            batch=self.main_batch,
                                            color=(255, 255, 255, 200),
                                            x=CONSTS.win_width / 2, y=200)

        self.title_text = pyglet.text.Label(text="Options",
                                            font_name='04b03',
                                            font_size=24,
                                            anchor_x='center',
                                            anchor_y='center',
                                            batch=self.main_batch,
                                            color=(255, 255, 255, 200),
                                            x=CONSTS.win_width / 2, y=150)

        self.title_text = pyglet.text.Label(text="Quit",
                                            font_name='04b03',
                                            font_size=24,
                                            anchor_x='center',
                                            anchor_y='center',
                                            batch=self.main_batch,
                                            color=(255, 255, 255, 200),
                                            x=CONSTS.win_width / 2, y=100)

        self.title_text = pyglet.text.Label(text="W, A, S, D to move",
                                            font_name='04b03',
                                            font_size=18,
                                            anchor_x='left',
                                            anchor_y='center',
                                            batch=self.main_batch,
                                            color=(255, 255, 255, 200),
                                            x=100, y=350)

        self.title_text = pyglet.text.Label(text="Cursor Keys to shoot",
                                            font_name='04b03',
                                            font_size=18,
                                            anchor_x='left',
                                            anchor_y='center',
                                            batch=self.main_batch,
                                            color=(255, 255, 255, 200),
                                            x=100, y=310)
        self.title_text = pyglet.text.Label(text="Space to use bomb (3 bombs)",
                                            font_name='04b03',
                                            font_size=18,
                                            anchor_x='left',
                                            anchor_y='center',
                                            batch=self.main_batch,
                                            color=(255, 255, 255, 200),
                                            x=400, y=350)

        self.title_text = pyglet.text.Label(text="Music by David Kracht",
                                            font_name='04b03',
                                            font_size=12,
                                            anchor_x='left',
                                            anchor_y='bottom',
                                            batch=self.main_batch,
                                            color=(255, 255, 255, 200),
                                            x=100, y=50)

        self.selector = pyglet.sprite.Sprite(img=res.selector, batch=self.main_batch,
                                             x=CONSTS.win_width / 2 - 75, y=200)
        self.selected_i = 0
        self.selector_i = 0
        self.enter = False
        self.game = False
        self.ang = 1
        self.target_ang = -15
        self.ang = -15

        self.performance_i = 0
        self.performance_text = pyglet.text.Label(text="Fancy Mode" if CONSTS.fancy else "Performance Mode",
                                                  font_name='04b03',
                                                  font_size=18,
                                                  anchor_x='right',
                                                  anchor_y='bottom',
                                                  batch=self.main_batch,
                                                  color=(255, 255, 255, 255),
                                                  x=700, y=50)

    def on_key_press(self, symbol, modifiers):
        last = self.selected_i
        if symbol == key.UP or symbol == key.W:
            self.selected_i = max(0, self.selected_i - 1)
        if symbol == key.DOWN or symbol == key.S:
            self.selected_i = min(2, self.selected_i + 1)
        if symbol == key.ENTER:
            self.enter = True
            if self.selected_i == 1:
                self.performance_i = 60
                CONSTS.fancy = not CONSTS.fancy
                self.performance_text.text = "Fancy Mode" if CONSTS.fancy else "Performance Mode"
        if not last == self.selected_i:
            self.target_ang = [-15, 0, 15][self.selected_i]
        pass

    def on_key_release(self, symbol, modifiers):
        if symbol == key.ENTER:
            print 'enter flase'
            self.enter = False

    def on_update(self, dt):
        if self.performance_i > 0:
            self.performance_i -= 1
            self.performance_text.color = (
                255, 255, 255, min(0, self.performance_text.color[3] - 10))
            # print self.performance_text.color
            # print self.performance_i

        self.selector.y = 200 - 50 * self.selected_i
        self.selector_i += 1
        if self.selector_i % 30 == 0:
            self.selector.opacity = 255 if self.selector.opacity == 0 else 0
        if self.enter:
            if self.selected_i == 0:
                self.game = True
            if self.selected_i == 2:
                quit()

    def on_draw(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glLoadIdentity()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(
            40.0, CONSTS.win_width / float(CONSTS.win_height), 0.1, 2000.0)
        glTranslatef(0, 0, -800)
        # print ang
        self.ang = utils.lerp(self.ang, self.target_ang, 0.5)
        glRotatef(self.ang,  CONSTS.win_width / 2, 0, 0)
        glTranslatef(-400, -300, 0)
        glMatrixMode(GL_MODELVIEW)

        self.main_batch.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        pass


class Play_State(object):

    def __init__(self, win, width, height):
        super(Play_State, self).__init__()

        self.width, self.height = width, height
        self.main_batch = game.graphics.Layer()
        self.hud_batch = game.graphics.Layer()

        self.camera = game.graphics.Camera(self, zoom=500.0)
        self.camera.track(self.main_batch)
        self.camera.shake(50)

        if CONSTS.fancy:
            music = res.paragon
            music.play()

        self.spatial_grid = Spatial_Grid()
        for i in range(CONSTS.CB_TYPES):
            self.spatial_grid.cb_type()
        self.BULLET_CB_TYPE = CONSTS.BULLET_CB_TYPE
        self.ENEMY_CB_TYPE = CONSTS.ENEMY_CB_TYPE
        self.ENEMY_LINE_CB_TYPE = CONSTS.ENEMY_LINE_CB_TYPE

        self.health = 3
        dead_health_bars = []
        active_health_bars = []

        health_bars = {'batch': self.hud_batch}

        health_bar_coords = [{'img': res.health_bar_un, 'x': res.health_bar.width / 2 + (50 + i),
                              'y': CONSTS.win_height - res.health_bar.height / 2 - 50} for i in xrange(0, 125, 25)]

        [dead_health_bars.append(pyglet.sprite.Sprite(
            **dict(health_bars.items() + coords.items()))) for coords in health_bar_coords]

        health_bar_coords = [{'img': res.health_bar, 'x': res.health_bar.width / 2 + (50 + i),
                              'y': CONSTS.win_height - res.health_bar.height / 2 - 50} for i in xrange(0, 125, 25)]

        [active_health_bars.append(pyglet.sprite.Sprite(
            **dict(health_bars.items() + coords.items()))) for coords in health_bar_coords]

        active_health_bars[-1].opacity = 0
        active_health_bars[-2].opacity = 0

        self.health_bars = [dead_health_bars, active_health_bars]
        self.update_health(-1)

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

        self.ship = Ship(img=res.player, x=400, y=300, batch=self.main_batch)
        self.bullets = []
        self.enemies = []
        self.enemy_bullets = []

        win.push_handlers(self.ship)
        self.emitter_list = []
        self.spawner = logic.Enemy_Spawner(self)

        p_y = math.sin(self.ship.rotation * math.pi / 180) * \
            self.ship.half_height + self.ship.y
        p_x = -math.cos(self.ship.rotation * math.pi / 180) * \
            self.ship.half_width + self.ship.x
        self.ship_emitter = game.graphics.ParticleSystem(
            p_x, p_y, angle=180 - self.ship.rotation, life=-1, particle_life=50, particles=90)
        self.dead_enemies = []

        self._ship_died = False
        self._died_timer = False

        self.bomb = False
        self.multiplier = 1
        self.quit_dead = False

    def on_key_release(self, symbol, modifiers):
        pass

    def update_health(self, mod):
        self.health += mod
        for i in xrange(5):
            if i > self.health:
                self.health_bars[1][i].opacity = 0
            else:
                self.health_bars[1][i].opacity = 255

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

        self.camera.update(dt)

        for emitter in self.emitter_list:
            emitter.update()

        for dead in self.dead_enemies:
            dead.update(dt)
        for removal in [b for b in self.dead_enemies if b.remove]:
            self.dead_enemies.remove(removal)
            removal.delete()

        if self._died_timer > 0:
            self._ship_died = False
            self._died_timer -= 1

            killer = False
            if len(self.enemies) >= 1:
                killer = self.enemies[0]
            elif len(self.enemy_bullets) >= 1:
                killer = self.enemy_bullets[0]

            # blink enemy killer
            if self._died_timer % 15 == 0:
                if killer:
                    if killer.opacity == 0:
                        killer.opacity = 255
                    else:
                        killer.opacity = 0
            if self._died_timer == 0:
                if self.health <= -1:
                    self.quit_dead = True
                    return
                self.ship.respawn()
                if killer:
                    killer.dead = True
            else:
                return

        # do not spawn enemies when bomb is used
        if self.bomb:
            self.bomb.scale += 0.05
            if self.bomb.scale >= 5:
                self.bomb.delete()
                self.bomb = False
        else:
            self.spawner.update(dt)
            for enemy in self.spawner.enemies:
                self.enemies.append(enemy)

        if self.ship.shoot and CONSTS.DEBUG_MODE_VAR('shoot'):
            if self.ship.shoot_type == 1:
                self.bullets.extend(self.ship.bullets)
                for bullet in self.ship.bullets:
                    self.spatial_grid.add_entity(bullet, self.BULLET_CB_TYPE)
            if self.ship.shoot_type == 2:
                if len(self.enemies) >= 1 and self.enemies[0].trackable:
                    bullet = Bullet(behaviours=[[behaviours.chase]], on_bounds_kill=True, img=res.bullet, x=self.ship.x,
                                    y=self.ship.y, batch=self.main_batch, track=self.enemies[0], rotation=self.ship.rotation)
                    self.spatial_grid.add_entity(bullet, self.BULLET_CB_TYPE)
                    self.bullets.append(bullet)
            self.ship.bullets = []

        if self.ship.bomb_i > 0 and self.ship.bomb:
            self.ship.bomb_i -= 1
            self.camera.shake(300)
            self.bomb = pyglet.sprite.Sprite(
                img=res.bomb, batch=self.main_batch)
            self.bomb.x = self.ship.x
            self.bomb.y = self.ship.y
            self.bomb.scale = 0.0
            for enemy in self.enemies:
                enemy.dead = True
                enemy.shot(self.ship.x, self.ship.y)
            for bullet in self.enemy_bullets:
                bullet.dead = True

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

        self._ship_died = False
        if self.ship.dead:
            self.update_health(-1)
            self.camera.shake(100)
            for enemy in self.enemies:
                if not self.ship.dead == enemy:
                    enemy.dead = True
                    enemy.shot(self.ship.x, self.ship.y)
            for enemy in self.enemy_bullets:
                if not self.ship.dead == enemy:
                    enemy.dead = True

            self._ship_died = True
            self._died_timer = 120
            self.ship.dead = False
            self.ship.opacity = 0
            self.emitter_list.append(
                game.graphics.ParticleSystem(self.ship.x, self.ship.y, rgb=[255, 255, 255], particle_life=120, particles=100, speed=10, speed_var=5))

        p_y = math.sin(self.ship.rotation * math.pi / 180) * \
            self.ship.half_height + self.ship.y
        p_x = -math.cos(self.ship.rotation * math.pi / 180) * \
            self.ship.half_width + self.ship.x
        self.ship_emitter.x = p_x
        self.ship_emitter.y = p_y
        self.ship_emitter.angle = self.ship.rotation
        self.ship_emitter.update()

        for bullet in [b for b in self.bullets if b.dead]:
            self.bullets.remove(bullet)
            self.spatial_grid.remove_entity(bullet, self.BULLET_CB_TYPE)
            if bullet.bounds_death:
                self.emitter_list.append(
                    game.graphics.ParticleSystem(bullet.x, bullet.y, particle_life=20, particles=20 + randint(0, 30)))
            bullet.delete()

        for enemy in [b for b in self.enemies if b.dead or b.is_outside_of_screen]:
            # if enemy has bullets, add them now (since we are removing the
            # enemy)
            if enemy.bullets:
                self.enemy_bullets += enemy.bullets
            self.enemies.remove(enemy)
            enemy.kill()
            if enemy.sensor or enemy.is_outside_of_screen:
                enemy.dead = True
                enemy.delete()
            elif enemy.dead:
                if not self._ship_died and not self.ship.bomb:
                    self.emitter_list.append(
                        game.graphics.ParticleSystem(enemy.x, enemy.y, **enemy.particle_data))
                    self.camera.shake(10)
                    if enemy.split:
                        behaviour_list = [
                            [behaviours.follow_player, 1], [behaviours.repulse, (self.ship.x, self.ship.y)]]
                        self.enemies.append(EnemyShip(behaviours=behaviour_list, score=12.5, img=res.splitter, particle_data={'rgb': res.splitter_colors}, track=self.ship,
                                                      x=enemy.x + enemy.width * 1, y=enemy.y + enemy.height * 1, batch=self.main_batch, cb_type=self.ENEMY_CB_TYPE))
                        self.enemies.append(EnemyShip(behaviours=behaviour_list, score=12.5, img=res.splitter, particle_data={'rgb': res.splitter_colors}, track=self.ship,
                                                      x=enemy.x + enemy.width * -1, y=enemy.y + enemy.height * -1, batch=self.main_batch, cb_type=self.ENEMY_CB_TYPE))
                        self.enemies[-1].scale = 0.75
                        self.enemies[-2].scale = 0.75
                self.dead_enemies.append(enemy)

                self.target_score += enemy.score * self.multiplier

        for bullet in [b for b in self.enemy_bullets if b.dead]:
            self.enemy_bullets.remove(bullet)
            if bullet._vertex_list:
                bullet.delete()

        if self.target_score > self.score:
            self.score = utils.lerp(self.score, self.target_score, 0.2)
            self.score_text.text = locale.format(
                "%d", round(self.score), grouping=True)

        if self.target_score > 1000:
            self.multiplier = 1.5
        elif self.target_score > 2000:
            self.multiplier = 2.0
        elif self.target_score > 5000:
            self.multiplier = 3.0
        elif self.target_score > 10000:
            self.health = min(self.health + 1, 5)
            self.multiplier = 5.0
        elif self.target_score > 30000:
            self.health = min(self.health + 1, 5)
        elif self.target_score > 100000:
            self.health = min(self.health + 1, 5)

        self.spatial_grid.clear()

        self.spatial_grid.add(self.ship, CONSTS.PLAYER_CB_TYPE)

        for bullet in self.bullets:
            bullet.update(dt)
            self.spatial_grid.add(bullet, self.BULLET_CB_TYPE)

        for enemy in self.enemies:
            enemy.update(dt)
            if enemy.bullets:
                self.enemy_bullets += enemy.bullets
            if enemy.collidable:
                self.spatial_grid.add(enemy, enemy.cb_type)

        for enemy_bullet in self.enemy_bullets:
            enemy_bullet.update(dt)

            self.spatial_grid.add(enemy_bullet, CONSTS.ENEMY_BULLET_CB_TYPE)

        self.spatial_grid.update()
        self.ship.bomb = False

    def on_draw(self, ):
        glClear(GL_COLOR_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glLoadIdentity()

        # self.camera.star_projection()
        # game.graphics.Starfield.create(
        #    max_x=CONSTS.game_width + 50, max_y=CONSTS.game_height + 50, size=16,
        #    seed=10293, particles=100)

        self.camera.game_projection()

        # game.graphics.Starfield.create(
        #    min_x=-100, min_y=-100, max_x=CONSTS.game_width + 100,
        # max_y=CONSTS.game_height + 100, size=12, seed=99023, particles=200)
        if CONSTS.DEBUG_MODE:
            CONSTS.debug_batch.draw()
        self.main_batch.draw()
        self.ship_emitter.draw()
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
