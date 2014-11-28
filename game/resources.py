import pyglet
pyglet.resource.path = ['./resources']
pyglet.resource.reindex()


def center_anchor(image):
    image.anchor_x = image.width / 2
    image.anchor_y = image.height / 2
    return image

player = center_anchor(pyglet.resource.image('shooter.png'))
tracker = center_anchor(pyglet.resource.image('tracker.png'))
splitter = center_anchor(pyglet.resource.image('splitter.png'))
liner = center_anchor(pyglet.resource.image('liner.png'))
bullet = center_anchor(pyglet.resource.image('bullet.png'))
fire_particle = center_anchor(pyglet.resource.image('fire-particle.png'))
