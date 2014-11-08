import pyglet, math, resources as res
from pyglet.window import key
from game.objects import Ship, EnemyShip, Bullet, Sprite
from random import randint
import utils
from itertools import repeat

fps_display = pyglet.clock.ClockDisplay()

class Game_Window(pyglet.window.Window):

	def __init__(self, width, height):
		super(Game_Window, self).__init__(width, height)
		self.main_batch = pyglet.graphics.Batch()
		self.ship = Ship(img=res.player, x=400, y=300)
		self.bullets = []

		self.enemies = []
		for i in range(700):
			self.enemies.append(EnemyShip(img=res.player, x=randint(50,self.width-50), y=randint(50,self.height-50), batch=self.main_batch))
		
		pyglet.clock.set_fps_limit(60)
		pyglet.clock.schedule(self.on_update)
		
		self.push_handlers(self.ship)

	def on_mouse_motion(self, x, y, dx, dy):
		self.last_mouse_pos = (x, y)

	def on_update(self, dt):
		if self.ship.shoot:
			bullet = Bullet(on_bounds_kill=True, img=res.bullet, x=self.ship.x, y=self.ship.y, r=self.ship.rotation, batch=self.main_batch)
			self.bullets.append(bullet)
		self.ship.update(dt)

		for bullet in [b for b in self.bullets if b.dead]:
			self.bullets.remove(bullet)

		for enemy in [b for b in self.enemies if b.dead]:
			self.enemies.remove(enemy)

		win_width = 800
		win_height = 600
		cell_size = 20.0
		
		hit_squares = [[[[],[]] for b in range(int(win_width/cell_size))] for a in range(int(win_height/cell_size))]

		for bullet in self.bullets:
			col, cell = int(bullet.y/cell_size), int(bullet.x/cell_size)
			if col < 30 and cell < 40 and col >= 0 and cell >= 0:
				hit_squares[col][cell][1].append(bullet)
			bullet.update(dt)

		for enemy in self.enemies:
			col, cell = int(enemy.y/cell_size), int(enemy.x/cell_size)
			if col < 30 and cell < 40 and col >= 0 and cell >= 0:
				hit_squares[col][cell][0].append(enemy)
			enemy.update(dt)

		for col in hit_squares:
			for cell in col:
				enemies = cell[0]
				bullets = cell[1]
				for a in enemies:
					for b in bullets:
						if utils.distance_sq(b, a) < (a.width/2 + b.width/2)**2:
							a.dead = True
							b.dead = True

	def on_draw(self, ):
		self.clear()

 		fps_display.draw()

		self.main_batch.draw()

		self.ship.draw()


game_window = Game_Window(800, 600) 

if __name__ == '__main__': 
	pyglet.app.run()