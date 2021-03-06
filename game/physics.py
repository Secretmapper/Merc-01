import constants as CONSTS
import math
import pyglet
import utils


class Spatial_Grid():

    def __init__(self):
        self._cb_type_i = 0
        self._cb_types = []  # cache _cb_types for hit list creation
        self._entities = []  # memory intensive
        self.max_cell_w = CONSTS.game_width / CONSTS.cell_size
        self.max_cell_h = CONSTS.game_height / CONSTS.cell_size
        self.debug_v_list = []

    def clear(self):
        self._hit_squares = [[[[] for i in self._cb_types] for b in range(
            int(CONSTS.game_width / CONSTS.cell_size))] for a in range(int(CONSTS.game_height / CONSTS.cell_size))]

    def update(self):
        for i in self.debug_v_list:
            i.delete()
        self.debug_v_list = []

        raycast_check_list = []

        for y in xrange(len(self._hit_squares)):
            row = self._hit_squares[y]
            for x in xrange(len(row)):
                cell = row[x]

                """
                Player - Sensor Checks (Line Enemy)
                """
                a_list = cell[CONSTS.PLAYER_CB_TYPE]
                b_list = cell[CONSTS.SENSOR_CB_TYPE]
                for b in b_list:
                    for a in a_list:
                        if not (a.dead or b.dead):
                            if utils.distance_sq(b, a) < (a.width / 2 + b.width / 2) ** 2:
                                b.dead = True
                                b.trigger(x=a.x, y=a.y)

                """
                Player - Enemy Checks
                """
                a_list = cell[CONSTS.PLAYER_CB_TYPE]
                b_list = cell[CONSTS.ENEMY_CB_TYPE] + \
                    cell[CONSTS.ENEMY_BLACK_HOLE] + \
                    cell[CONSTS.ENEMY_LINE_CB_TYPE]
                for b in b_list:
                    for a in a_list:
                        if not (a.dead or b.dead or a.invinsible):
                            if utils.distance_sq(b, a) < (a.width / 2 + b.width / 2) ** 2:
                                a.hit()
                                if a.boost:
                                    b.dead = True
                                    b.shot(a.x, a.y)
                                else:
                                    a.dead = b

                a_list = cell[CONSTS.PLAYER_CB_TYPE]
                b_list = cell[CONSTS.ENEMY_BULLET_CB_TYPE]
                for b in b_list:
                    for a in a_list:
                        if not (a.dead or b.dead):
                            if utils.distance_sq(b, a) < (a.width / 2 + b.width / 2) ** 2:
                                #b.dead = True
                                a.dead = b

                a_list = cell[CONSTS.BULLET_CB_TYPE]
                b_list = cell[CONSTS.ENEMY_BLACK_HOLE]
                for b in b_list:
                    for a in a_list:
                        if not (a.dead or b.dead):
                            if utils.distance_sq(b, a) < (a.width / 2 + b.width / 2) ** 2:
                                b.dead = True
                                a.dead = True

                a_list = cell[CONSTS.BULLET_CB_TYPE]
                b_list = cell[CONSTS.ENEMY_CB_TYPE]
                """
                Bullet - Enemy Checks
                """
                for b in b_list:
                    for a in a_list:
                        if not (a.dead or b.dead):
                            if utils.distance_sq(b, a) < (a.width / 2 + b.width / 2) ** 2:
                                a.dead = True
                                b.dead = True
                                b.shot(a.x, a.y)
                                self.color_grid(x, y, (0, 0, 255, 100) * 4)
                    if not b.dead:
                        """
                        Nearby Callback

                        Here we're iterating through adjacent places on the grid:
                        x-1 y+1, x  y+1, x+1 y+1
                        x-1 y  , x  y  , x+1 y
                        x-1 y-1, x, y-1, x-1 y-1

                        and then calling adjacency callbacks.
                        """
                        # nearby
                        nearby_bullets = []
                        y_rows_n = [
                            max(0, y - 1), y, min(int(CONSTS.game_height / CONSTS.cell_size) - 1, y + 1)]
                        x_rows_n = [
                            max(0, x - 1), x, min(int(CONSTS.game_width / CONSTS.cell_size) - 1, x + 1)]
                        for y_row_i in y_rows_n:
                            y_row = self._hit_squares[y_row_i]
                            x_rows = [y_row[i] for i in x_rows_n]
                            for cell_i in xrange(len(x_rows)):
                                nearby_bullets.append(
                                    x_rows[cell_i][CONSTS.BULLET_CB_TYPE])
                                self.color_grid(
                                    x_rows_n[cell_i], y_row_i, (0, 100, 100, 100) * 4)
                        # nearby
                        b.near_by_cb(nearby_bullets)

                a_list = cell[CONSTS.ENEMY_CB_TYPE]
                b_list = cell[CONSTS.ENEMY_BLACK_HOLE]
                """
                Bullet - Enemy Checks
                """
                for b in b_list:
                    """
                    for a in a_list:
                        if not (a.dead or b.dead):
                            if utils.distance_sq(b, a) < (a.width / 2 + b.width / 2) ** 2:
                                a.dead = True
                                b.dead = True
                                b.shot(a.x, a.y)
                                self.color_grid(x, y, (0, 0, 255, 100) * 4)
                    """
                    if not b.dead:
                        """
                        Nearby Callback

                        Here we're iterating through adjacent places on the grid:
                        x-1 y+1, x  y+1, x+1 y+1
                        x-1 y  , x  y  , x+1 y
                        x-1 y-1, x, y-1, x-1 y-1

                        and then calling adjacency callbacks.
                        """
                        # nearby
                        nearby = []
                        max_y = int(CONSTS.game_height / CONSTS.cell_size) - 1
                        max_x = int(CONSTS.game_width / CONSTS.cell_size) - 1
                        y_rows_n = [
                            max(0, y - 3), max(0, y - 2), max(0, y - 1), y, min(max_y, y + 1), min(max_y, y + 2), min(max_y, y + 3)]
                        x_rows_n = [
                            max(0, x - 3), max(0, x - 2), max(0, x - 1), x, min(max_x, x + 1), min(max_x, x + 2), min(max_x, x + 3)]
                        for y_row_i in y_rows_n:
                            y_row = self._hit_squares[y_row_i]
                            x_rows = [y_row[i] for i in x_rows_n]
                            for cell_i in xrange(len(x_rows)):
                                if b.attract:
                                    nearby.append(
                                        x_rows[cell_i][CONSTS.ENEMY_CB_TYPE])
                                    nearby.append(
                                        x_rows[cell_i][CONSTS.PLAYER_CB_TYPE])
                                    nearby.append(
                                        x_rows[cell_i][CONSTS.ENEMY_BLACK_HOLE])
                                nearby.append(
                                    x_rows[cell_i][CONSTS.BULLET_CB_TYPE])
                                self.color_grid(
                                    x_rows_n[cell_i], y_row_i, (50, 50, 50, 100) * 4)
                        # nearby
                        for bu in sum(nearby, []):
                            bu.black_hole(b)

                a_list = cell[CONSTS.ENEMY_CB_TYPE]
                b_list = cell[CONSTS.ENEMY_BLACK_HOLE]
                for a in a_list:
                    for b in b_list:
                        if not (a.dead or b.dead) and utils.distance_sq(a, b) < (a.width / 2 + b.width / 2) ** 2:
                            a.dead = True
                            a.particle_data = {'particles': 10}

                a_list = cell[CONSTS.ENEMY_BLACK_HOLE]
                b_list = cell[CONSTS.ENEMY_BLACK_HOLE]
                for a in a_list:
                    for b in b_list:
                        if not (a.id == b.id) and not (a.dead or b.dead) and utils.distance_sq(a, b) < (a.width / 2 + b.width / 2) ** 2:
                            a.type_overlap_cb(b)
                            b.type_overlap_cb(a)
                            self.color_grid(x, y, (255, 0, 0, 100) * 4)

                """
                ENEMY - ENEMY Checks (Separation)
                """
                a_list = cell[CONSTS.ENEMY_CB_TYPE]
                b_list = cell[CONSTS.ENEMY_CB_TYPE]
                for a in a_list:
                    for b in b_list:
                        if not (a.id == b.id) and not (a.dead or b.dead) and (a.separate and b.separate) and utils.distance_sq(a, b) < (a.width / 2 + b.width / 2) ** 2:
                            a.type_overlap_cb(b)
                            b.type_overlap_cb(a)
                            self.color_grid(x, y, (255, 0, 0, 100) * 4)

    def color_grid(self, x, y, color):
        if CONSTS.DEBUG_MODE:
            coords = (
                x * CONSTS.cell_size, y * CONSTS.cell_size,
                x *
                CONSTS.cell_size, (y + 1) * CONSTS.cell_size,
                (x + 1) * CONSTS.cell_size, (y + 1) *
                CONSTS.cell_size,
                (x + 1) * CONSTS.cell_size, y * CONSTS.cell_size,)
            self.debug_v_list.append(CONSTS.debug_batch.add(4, pyglet.gl.GL_QUADS,
                                                            None,
                                                            ('v2f',
                                                             coords),
                                                            ('c4B', color)))

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
