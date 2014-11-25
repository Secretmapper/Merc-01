from itertools import repeat
import pyglet
import math
import utils
import game.resources as res
import game.constants as CONSTS
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
        self.BULLET_CB_TYPE = self.spatial_grid.cb_type()
        self.ENEMY_CB_TYPE = self.spatial_grid.cb_type()

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

    def on_mouse_motion(self, x, y, dx, dy):
        self.last_mouse_pos = (x, y)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.TAB:
            CONSTS.DEBUG_MODE = not CONSTS.DEBUG_MODE
        if CONSTS.DEBUG_MODE and symbol == key.GRAVE:
            CONSTS.DEBUG_MODE_OBJ['shoot'] = not CONSTS.DEBUG_MODE_OBJ['shoot']

    def on_update(self, dt):
        if self.ship.shoot and CONSTS.DEBUG_MODE_VAR('shoot'):
            bullet = Bullet(on_bounds_kill=True, img=res.bullet, x=self.ship.x,
                            y=self.ship.y, r=self.ship.rotation, batch=self.main_batch)
            self.spatial_grid.add_entity(bullet, self.BULLET_CB_TYPE)
            self.bullets.append(bullet)
        self.ship.update(dt)

        self.main_batch.x = (CONSTS.win_width / 2 - self.ship.x)
        self.main_batch.y = (CONSTS.win_height / 2 - self.ship.y)

        self.camera.update(dt)

        for bullet in [b for b in self.bullets if b.dead]:
            self.bullets.remove(bullet)
            self.spatial_grid.remove_entity(bullet, self.BULLET_CB_TYPE)

        for enemy in [b for b in self.enemies if b.dead]:
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
        self.main_batch.draw()

        if CONSTS.DEBUG_MODE:
            CONSTS.debug_batch.draw()

game_window = Game_Window(800, 600)

if __name__ == '__main__':
    pyglet.app.run()
