import pyglet

win_width = 800
win_height = 600
cell_size = 40.0

game_iter = float(1) / 60
game_width = 1280
game_height = 960

debug_batch = pyglet.graphics.Batch()


def DEBUG_MODE_VAR(key):
    if not DEBUG_MODE:
        return True
    else:
        return DEBUG_MODE_OBJ[key]

DEBUG_MODE = True
DEBUG_MODE_OBJ = {
    'shoot': True
}
