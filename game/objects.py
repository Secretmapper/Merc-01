import pyglet, math, resources as res
from pyglet.window import key

class Sprite(pyglet.sprite.Sprite):

	def __init__(self, img, x=0, y=0, on_bounds_kill=False):
		super(Sprite, self).__init__(img=img, x=x, y=y)
		self.dead = False
		self.on_bounds_kill = on_bounds_kill

	def update(self, dt):
		self.check_bounds()

	def check_bounds(self):
		min_x = -self.image.width/2
		min_y = -self.image.height/2
		#todo -hardcoded windows
		max_x = 800 + self.image.width/2
		max_y = 600 + self.image.height/2
		if self.on_bounds_kill:
			if self.x < min_x or self.x > max_x or self.x < min_y or self.y > max_y:
				self.dead = True

class Bullet(Sprite):

	def __init__(self, img, x, y, r, on_bounds_kill=False):
		super(Bullet, self).__init__(img=img, x=x, y=y, on_bounds_kill=on_bounds_kill)
		r *= -math.pi/180
		self.dir_x = math.cos(r)
		self.dir_y = math.sin(r)
		self.speed = 10

	def update(self, dt):
		Sprite.update(self, dt)
		self.x += self.dir_x * self.speed
		self.y += self.dir_y * self.speed

class Ship(Sprite):

	def __init__(self, img, x, y):
		super(Ship, self).__init__(img=img, x=x, y=y)
		self.mouse_pos = (0, 0)
		self.keys = dict(spacebar=False)
		self.shoot = False

	def on_mouse_motion(self, x, y, dx, dy):
		self.rotation = -math.atan2(y-self.y, x-self.x) * 180/math.pi
		self.mouse_pos = (x, y)

	def on_mouse_press(self, x, y, button, modifiers):
		self.shoot = True

	def update(self, dt):
		Sprite.update(self, dt)
		self.shoot = False
		if not self.keys['spacebar']:
			end_x, end_y = self.mouse_pos
			self.x += (end_x - self.x) / 5
			self.y += (end_y - self.y) / 5

	def on_key_press(self, symbol, modifiers):
		if symbol == key.SPACE:
			self.keys['spacebar'] = True

	def on_key_release(self, symbol, modifiers):
		if symbol == key.SPACE:
			self.keys['spacebar'] = False