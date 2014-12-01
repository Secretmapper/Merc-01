import pyglet
pyglet.resource.path = ['./resources/img']
pyglet.resource.reindex()


def center_anchor(image):
    image.anchor_x = image.width / 2
    image.anchor_y = image.height / 2
    return image

player = center_anchor(pyglet.resource.image('shooter.png'))

tracker = center_anchor(pyglet.resource.image('tracker.png'))
tracker_colors = [140, 198, 63]

splitter = center_anchor(pyglet.resource.image('splitter.png'))
splitter_colors = [170, 104, 170]

liner = center_anchor(pyglet.resource.image('liner.png'))
bullet = center_anchor(pyglet.resource.image('bullet.png'))
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
