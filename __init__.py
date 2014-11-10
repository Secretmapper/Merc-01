from itertools import repeat
import utils
import pyglet, math, resources as res
from pyglet.window import key
from pyglet.graphics import glMatrixMode, GL_PROJECTION, glLoadIdentity, gluOrtho2D, glClear, GL_COLOR_BUFFER_BIT, GL_MODELVIEW, glTranslatef
import game.graphics
from game.objects import Ship, EnemyShip, Bullet, Sprite
from random import randint
import math

win_width = 800
win_height = 600
cell_size = 40.0
max_cell_w = win_width/cell_size
max_cell_h = win_height/cell_size

fps_display = pyglet.clock.ClockDisplay()

class Camera(object):

	def __init__(self, win, x=0, y=0, z=0, zoom=1.0):
		self.win = win
		self.zoom = zoom
		self.x, self.y, self.z = x, y, z
		
		self._offset = [0, 0]
		self._track = type('obj', (object,), {'x':0, 'y':0})
		self._radius = 0
		self._shake_dec = 0 #how much the shake dies down every update

	def update(self, dt):
		if self._radius > 0:
			self._radius *= self._shake_dec
			self._angle += 180 if randint(0, 1) == 0 else 60 
			self._offset = [math.sin(self._angle) * self._radius , math.cos(self._angle) * self._radius]
			if math.floor(self._radius) == 0.0: self._radius = 0
		self.x = ( self._track.x + self._offset[1] )/float(win_width/2)
		self.y = ( self._track.y + self._offset[0] )/float(win_height/2)

	def track(self, track):
		self._track = track

	def shake(self, r, dec= 0.9):
		self._radius = r
		self._shake_dec = dec
		self._angle = randint(0, 360) 
		self._offset = [ math.sin(self._angle) * self._radius , math.cos(self._angle) * self._radius]

	def game_projection(self):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glTranslatef(self.x, self.y, self.z)
		gluOrtho2D( 
			0,self.win.width,
			0,self.win.height)

	def hud_projection(self):
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		#glTranslatef(self.x, self.y, self.z)
		gluOrtho2D( 
			0,self.win.width,
			0,self.win.height)


class Game_Window(pyglet.window.Window):

	def __init__(self, width, height):
		super(Game_Window, self).__init__(width, height)
		self.main_batch = game.graphics.Layer()
		self.ship = Ship(img=res.player, x=400, y=300, batch=self.main_batch)
		self.bullets = []

		self.enemies = []
		for i in range(300):
			self.enemies.append(EnemyShip(img=res.player, x=randint(50,self.width-50), y=randint(50,self.height-50), batch=self.main_batch))
		
		pyglet.clock.set_fps_limit(60)
		pyglet.clock.schedule(self.on_update)
		
		self.push_handlers(self.ship)

		self.camera = Camera(self, zoom=500.0)
		self.camera.track(self.main_batch)
		self.camera.shake(50)

	def on_mouse_motion(self, x, y, dx, dy):
		self.last_mouse_pos = (x, y)

	def on_update(self, dt):
		if self.ship.shoot:
			bullet = Bullet(on_bounds_kill=False, img=res.bullet, x=self.ship.x, y=self.ship.y, r=self.ship.rotation, batch=self.main_batch)
			self.bullets.append(bullet)
		self.ship.update(dt)

		self.main_batch.x = (win_width/2 - self.ship.x)
		self.main_batch.y = (win_height/2 - self.ship.y)

		self.camera.update(dt)

		for bullet in [b for b in self.bullets if b.dead]:
			self.bullets.remove(bullet)

		for enemy in [b for b in self.enemies if b.dead]:
			self.enemies.remove(enemy)
		
		hit_squares = [[[[],[]] for b in range(int(win_width/cell_size))] for a in range(int(win_height/cell_size))]

		for bullet in self.bullets:
			col, cell, col_e, cell_e = map(lambda x: int(x/cell_size), bullet.pos_vertices())
			for a in range(col, col_e+1):
				for b in range(cell, cell_e+1):
					if a < max_cell_h and b < max_cell_w and a >= 0 and b >= 0:
						hit_squares[a][b][1].append(bullet)
			bullet.update(dt)

		for enemy in self.enemies:
			col, cell, col_e, cell_e = map(lambda x: int(x/cell_size), enemy.pos_vertices())
			for a in range(col, col_e+1):
				for b in range(cell, cell_e+1):
					if a < max_cell_h and b < max_cell_w and a >= 0 and b >= 0:
						hit_squares[a][b][0].append(enemy)
			enemy.update(dt)

		for col in hit_squares:
			for cell in col:
				enemies = cell[0]
				bullets = cell[1]
				for a in enemies:
					for b in bullets:
						if not (a.dead or b.dead) and utils.distance_sq(b, a) < (a.width/2 + b.width/2)**2:
							a.dead = True
							b.dead = True

	def on_draw(self, ):
		#self.clear()
		glClear(GL_COLOR_BUFFER_BIT)
		glMatrixMode(GL_MODELVIEW);
		glLoadIdentity();

		self.camera.hud_projection()
 		fps_display.draw()

		self.camera.game_projection()
		self.main_batch.draw()

game_window = Game_Window(800, 600) 

if __name__ == '__main__': 
	pyglet.app.run()