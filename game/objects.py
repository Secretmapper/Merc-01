import pyglet, math, resources as res
from pyglet.window import key
from random import randint

win_width = 800
win_height = 600

class Sprite(pyglet.sprite.Sprite):

	def __init__(self, img, x=0, y=0, on_bounds_kill=False):
		super(Sprite, self).__init__(img=img, x=x, y=y)
		self.dead = False
		self.on_bounds_kill = on_bounds_kill

		self.min_x = -img.width/2
		self.min_y = -img.height/2
		#todo -hardcoded windows
		self.max_x = win_width + img.width/2
		self.max_y = win_height + img.height/2

	def update(self, dt):
		if self.on_bounds_kill:
			self.check_bounds()

	def check_bounds(self):
		if self.x < self.min_x or self.x > self.max_x or self.x < self.min_y or self.y > self.max_y:
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

class EnemyShip(Sprite):

	def __init__(self, img, x, y):
		super(EnemyShip, self).__init__(img=img, x=x, y=y)
		self.hit = True
		r = randint(0, 360)
		r *= -math.pi/180
		self.dir_x = math.cos(r)
		self.dir_y = math.sin(r)
		self.speed = 10

		self.min_x = img.width/2
		self.min_y = img.height/2
		#todo -hardcoded windows
		self.max_x = win_width - img.width/2
		self.max_y = win_height - img.height/2

	def update(self, dt):
		Sprite.update(self, dt)
		self.x += self.dir_x * self.speed
		self.y += self.dir_y * self.speed

		if self.y <= self.min_y or self.y >= self.max_y:
			self.dir_y = -self.dir_y
		elif self.x <= self.min_x or self.x >= self.max_x:
			self.dir_x = -self.dir_x

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