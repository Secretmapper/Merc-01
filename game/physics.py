import constants as CONSTS
import utils

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