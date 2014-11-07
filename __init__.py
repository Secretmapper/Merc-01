import pyglet, math, resources as res
from pyglet.window import key
from game.objects import Ship, EnemyShip, Bullet, Sprite
from random import randint
import utils

class Game_Window(pyglet.window.Window):

	def __init__(self, width, height):
		super(Game_Window, self).__init__(width, height)
		self.ship = Ship(img=res.player, x=400, y=300)
		self.bullets = []

		self.enemies = []
		for i in range(100):
			self.enemies.append(EnemyShip(img=res.player, x=randint(50,self.width-50), y=randint(50,self.height-50)))
		
		pyglet.clock.schedule_interval(self.on_update, 1/60.0)
		self.push_handlers(self.ship)

	def on_mouse_motion(self, x, y, dx, dy):
		self.last_mouse_pos = (x, y)

	def on_update(self, dt):
		if self.ship.shoot:
			bullet = Bullet(img=res.bullet, x=self.ship.x, y=self.ship.y, r=self.ship.rotation, on_bounds_kill=True)
			self.bullets.append(bullet)
		self.ship.update(dt)

		for bullet in [b for b in self.bullets if b.dead]:
			self.bullets.remove(bullet)

		for bullet in self.bullets:
			bullet.update(dt)

		#removes enemies that collides with bullets
		#list comprehension to modify list in iteration (faster)
		self.enemies[:] = [enemy for enemy in self.enemies if not utils.collides(enemy, self.bullets)]

		for enemy in self.enemies:
			enemy.update(dt)

	def on_draw(self, ):
		self.clear()

		for bullet in self.bullets:
			bullet.draw()

		for enemies in self.enemies:
			enemies.draw()

		self.ship.draw()


game_window = Game_Window(800, 600) 

if __name__ == '__main__': 
	pyglet.app.run()