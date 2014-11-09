import pyglet, math, resources as res
from pyglet.window import key
from random import randint

win_width = 800
win_height = 600

class Sprite(pyglet.sprite.Sprite):

	def __init__(self, on_bounds_kill=False, *args, **kwargs):
		super(Sprite, self).__init__(**kwargs)
		self.dead = False
		self.on_bounds_kill = on_bounds_kill

		self.min_x = -self.image.width/2
		self.min_y = -self.image.height/2
		#todo -hardcoded windows
		self.max_x = win_width + self.image.width/2
		self.max_y = win_height + self.image.height/2

	def pos_vertices(self):
		return [self.y-self.height/2, self.x-self.width/2, self.y+self.height/2, self.x+self.width/2]

	def update(self, dt):
		if self.on_bounds_kill:
			self.check_bounds()

	def check_bounds(self):
		if self.x < self.min_x or self.x > self.max_x or self.x < self.min_y or self.y > self.max_y:
			self.dead = True

class Bullet(Sprite):

	def __init__(self, r, *args, **kwargs):
		super(Bullet, self).__init__(**kwargs)
		r *= -math.pi/180
		self.dir_x = math.cos(r)
		self.dir_y = math.sin(r)
		self.speed = 5

	def update(self, dt):
		Sprite.update(self, dt)
		self.x += self.dir_x * self.speed
		self.y += self.dir_y * self.speed

class EnemyShip(Sprite):

	def __init__(self, *args, **kwargs):
		super(EnemyShip, self).__init__(**kwargs)
		self.hit = True
		r = randint(0, 360)
		r *= -math.pi/180
		self.dir_x = math.cos(r)
		self.dir_y = math.sin(r)
		self.speed = 10

		self.min_x = self.image.width/2
		self.min_y = self.image.height/2
		#todo -hardcoded windows
		self.max_x = win_width-200 - self.image.width/2
		self.max_y = win_height - self.image.height/2

	def update(self, dt):
		Sprite.update(self, dt)
		#return
		self.x += self.dir_x * self.speed
		self.y += self.dir_y * self.speed

		if self.y <= self.min_y or self.y >= self.max_y:
			self.dir_y = -self.dir_y
		elif self.x <= self.min_x or self.x >= self.max_x:
			self.dir_x = -self.dir_x

class Ship(Sprite):

	def __init__(self, *args, **kwargs):
		super(Ship, self).__init__(**kwargs)
		self.mouse_pos = (0, 0)
		self.keys = dict(spacebar=False, W=False, A=False, S=False, D=False)
		self.shoot = False
		self.shoot_timer = 10
		self.i_shoot = self.shoot_timer

	def on_mouse_motion(self, x, y, dx, dy):
		self.rotation = -math.atan2(y-self.y, x-self.x) * 180/math.pi
		#self.mouse_pos = (x, y)

	def update(self, dt):
		Sprite.update(self, dt)
		self.shoot = False
		self.i_shoot -= 1
		if self.i_shoot < 0:
			self.shoot = True
			self.i_shoot = self.shoot_timer
		if self.keys['W']:
			self.y += 2
		if self.keys['S']:
			self.y -= 2
		if self.keys['A']:
			self.x -= 2
		if self.keys['D']:
			self.x += 2

	def on_key_press(self, symbol, modifiers):
		if symbol == key.SPACE:
			self.keys['spacebar'] = True
		if symbol == key.W:
			self.keys['W'] = True
		if symbol == key.A:
			self.keys['A'] = True
		if symbol == key.S:
			self.keys['S'] = True
		if symbol == key.D:
			self.keys['D'] = True

	def on_key_release(self, symbol, modifiers):
		if symbol == key.SPACE:
			self.keys['spacebar'] = False
		if symbol == key.W:
			self.keys['W'] = False
		if symbol == key.A:
			self.keys['A'] = False
		if symbol == key.S:
			self.keys['S'] = False
		if symbol == key.D:
			self.keys['D'] = False