from itertools import repeat
import pyglet
import math
import utils
import game.resources as res
import game.constants as CONSTS
from pyglet.window import key
from pyglet.graphics import glMatrixMode, GL_PROJECTION, glLoadIdentity, gluOrtho2D, glClear, GL_COLOR_BUFFER_BIT, GL_MODELVIEW, glTranslatef
import game.graphics
from game.objects import Ship, EnemyShip, TrackerShip, Bullet, Sprite
from random import randint
import math

fps_display = pyglet.clock.ClockDisplay()


class Spatial_Grid():

    def __init__(self):
        self._cb_type_i = 0
        self._cb_types = []  # cache _cb_types for hit list creation
        self._entities = []  # memory intensive
        self.max_cell_w = CONSTS.game_width / CONSTS.cell_size
        self.max_cell_h = CONSTS.game_height / CONSTS.cell_size

    def clear(self):
        self._hit_squares = [[[[] for i in self._cb_types] for b in range(
            int(CONSTS.game_width / CONSTS.cell_size))] for a in range(int(CONSTS.game_height / CONSTS.cell_size))]

    def update(self):
        for col in self._hit_squares:
            for cell in col:
                a_list = cell[0]
                b_list = cell[1]
                for a in a_list:
                    for b in b_list:
                        if not (a.dead or b.dead) and utils.distance_sq(b, a) < (a.width / 2 + b.width / 2) ** 2:
                            a.dead = True
                            b.dead = True

    def add_entity(self, e, i):
        self._entities[i].append(e)

    def remove_entity(self, e, i):
        self._entities[i].remove(e)  # warning: O(n)

    def add(self, item, i):
        col, cell, col_e, cell_e = map(
            lambda x: int(x / CONSTS.cell_size), item.pos_vertices())
        for a in range(col, col_e + 1):
            for b in range(cell, cell_e + 1):
                if a < self.max_cell_h and b < self.max_cell_w and a >= 0 and b >= 0:
                    self._hit_squares[a][b][i].append(item)

    def cb_type(self):
        self._cb_type_i += 1
        self._cb_types.append(0)
        self._entities.append([])
        return self._cb_type_i - 1


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
            # y=randint(50,self.height-50)
            enemy = TrackerShip(img=res.tracker, track=self.ship, x=randint(
                50, self.width - 50), y=randint(50, self.height - 50), batch=self.main_batch)
            self.spatial_grid.add_entity(enemy, self.ENEMY_CB_TYPE)
            self.enemies.append(enemy)

        pyglet.clock.set_fps_limit(60)
        pyglet.clock.schedule(self.on_update)

        self.push_handlers(self.ship)

    def on_mouse_motion(self, x, y, dx, dy):
        self.last_mouse_pos = (x, y)

    def on_update(self, dt):
        if self.ship.shoot:
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
        # self.main_batch.draw()

        self.camera.game_projection()
        self.main_batch.draw()

game_window = Game_Window(800, 600)

if __name__ == '__main__':
    pyglet.app.run()
