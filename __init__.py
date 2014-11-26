from itertools import repeat
import pyglet
import math
import utils
import game.resources as res
import game.constants as CONSTS
import game.globals as GLBS
from game.physics import Spatial_Grid
from pyglet.window import key
from pyglet.graphics import glMatrixMode, GL_PROJECTION, glLoadIdentity, gluOrtho2D, glClear, GL_COLOR_BUFFER_BIT, GL_MODELVIEW, glTranslatef
import game.graphics
from game.objects import Ship, EnemyShip, Bullet, Sprite
import game.behaviours as behaviours
from random import randint
import math

fps_display = pyglet.clock.ClockDisplay()


class Game_Window(pyglet.window.Window):

    def __init__(self, width, height):
        super(Game_Window, self).__init__(width, height)
        self.main_batch = game.graphics.Layer()

        self.camera = game.graphics.Camera(self, zoom=500.0)
        self.camera.track(self.main_batch)
        self.camera.shake(50)

        self.spatial_grid = Spatial_Grid()
        for i in range(3):
            self.spatial_grid.cb_type()
        self.BULLET_CB_TYPE = CONSTS.BULLET_CB_TYPE
        self.ENEMY_CB_TYPE = CONSTS.ENEMY_CB_TYPE
        self.ENEMY_LINE_CB_TYPE = CONSTS.ENEMY_LINE_CB_TYPE

        self.ship = Ship(img=res.player, x=400, y=300, batch=self.main_batch)
        self.bullets = []
        self.enemies = []

        for i in range(50):
            enemy = EnemyShip(behaviours=[behaviours.follow_player], img=res.tracker, track=self.ship, x=randint(
                50, self.width - 50), y=randint(50, self.height - 50), batch=self.main_batch)
            self.spatial_grid.add_entity(enemy, self.ENEMY_CB_TYPE)
            self.enemies.append(enemy)

        pyglet.clock.set_fps_limit(60)
        pyglet.clock.schedule(self.on_update)

        self.push_handlers(self.ship)
        self.emitter_list = []

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
        if self.ship.shoot and CONSTS.DEBUG_MODE_VAR('shoot'):
            bullet = Bullet(on_bounds_kill=True, img=res.bullet, x=self.ship.x,
                            y=self.ship.y, r=self.ship.rotation, batch=self.main_batch)
            self.spatial_grid.add_entity(bullet, self.BULLET_CB_TYPE)
            self.bullets.append(bullet)
        self.ship.update(dt)

        max_y = CONSTS.win_height / 2 - \
            (CONSTS.game_height - (CONSTS.win_height / 2 - 40))
        max_x = CONSTS.win_width / 2 - \
            (CONSTS.game_width - (CONSTS.win_width / 2 - 40))
        self.main_batch.x = utils.lerp(self.main_batch.x,
                                       utils.trunc((CONSTS.win_width / 2 - self.ship.x), max_x, 40), 0.5)
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

        for enemy in [b for b in self.enemies if b.dead]:
            self.emitter_list.append(
                game.graphics.ParticleSystem(enemy.x, enemy.y))
            self.enemies.remove(enemy)
            enemy.kill()
            self.camera.shake(5)
            self.spatial_grid.remove_entity(enemy, self.ENEMY_CB_TYPE)

        self.spatial_grid.clear()

        for bullet in self.bullets:
            bullet.update(dt)
            self.spatial_grid.add(bullet, self.BULLET_CB_TYPE)

        for enemy in self.enemies:
            enemy.update(dt)
            self.spatial_grid.add(enemy, self.ENEMY_CB_TYPE)

        self.spatial_grid.update()

    def on_draw(self, ):
        glClear(GL_COLOR_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
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

game_window = Game_Window(800, 600)

if __name__ == '__main__':
    pyglet.app.run()
