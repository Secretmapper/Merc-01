import pyglet
import os

working_dir = os.path.dirname(os.path.realpath(__file__))

pyglet.resource.path = [os.path.join(
    working_dir, '../resources/img'), os.path.join(working_dir, '../resources/music'), ]
pyglet.resource.reindex()


def center_anchor(image):
    image.anchor_x = image.width / 2
    image.anchor_y = image.height / 2
    return image

bomb = center_anchor(pyglet.resource.image('bomb.png'))
player = center_anchor(pyglet.resource.image('shooter.png'))


black_hole = center_anchor(pyglet.resource.image('black_hole.png'))
black_field = center_anchor(pyglet.resource.image('black_field.png'))
black_hole_colors = [100, 0, 0]

tracker = center_anchor(pyglet.resource.image('tracker.png'))
tracker_colors = [140, 198, 63]

splitter = center_anchor(pyglet.resource.image('splitter.png'))
splitter_colors = [170, 104, 170]

evader = center_anchor(pyglet.resource.image('evader.png'))
evader_colors = [255, 242, 0]

liner = center_anchor(pyglet.resource.image('liner.png'))
bullet = center_anchor(pyglet.resource.image('bullet.png'))
homing_bullet = center_anchor(pyglet.resource.image('homing-bullet.png'))
fire_particle = center_anchor(pyglet.resource.image('fire-particle.png'))

health_bar = center_anchor(pyglet.resource.image('health-bar.png'))
health_bar.anchor_y = 10
health_bar.anchor_x = 80

health_bar_un = center_anchor(pyglet.resource.image('health-bar-un.png'))
health_bar_un.anchor_y = 10
health_bar_un.anchor_x = 80

circle_detect = center_anchor(pyglet.resource.image('circle-detect.png'))

circle_detect_text = pyglet.resource.image('circle-detect-text.png')
circle_detect_text.anchor_x = 13
circle_detect_text.anchor_y = 10


# music
paragon = pyglet.resource.media('152047_ParagonX9___Chaoz_I.mp3')
