import pyglet

win_width = 800
win_height = 600
cell_size = 40.0

game_iter = float(1) / 60
game_width = 800
game_height = 600

debug_batch = pyglet.graphics.Batch()


def DEBUG_MODE_VAR(key):
    if not DEBUG_MODE:
        return True
    else:
        return DEBUG_MODE_OBJ[key]

DEBUG_MODE = False
DEBUG_MODE_OBJ = {
    'shoot': False,
    'play': True,
}

# number of cb types
CB_TYPES = 7

# cb types:
BULLET_CB_TYPE = 0
ENEMY_CB_TYPE = 1
PLAYER_CB_TYPE = 3
SENSOR_CB_TYPE = 4

ENEMY_LINE_CB_TYPE = 2
ENEMY_BULLET_CB_TYPE = 5
ENEMY_BLACK_HOLE = 6
