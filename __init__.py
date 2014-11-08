import pyglet, math, resources as res
from pyglet.window import key
from game.objects import Ship, EnemyShip, Bullet, Sprite
from random import randint
import utils

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

		for bullet in self.bullets:
			bullet.update(dt)

		#removes enemies that collides with bullets
		#list comprehension to modify list in iteration (faster)
		self.enemies[:] = [enemy for enemy in self.enemies if not utils.collides(enemy, self.bullets)]

		for enemy in self.enemies:
			enemy.update(dt)

	def on_draw(self, ):
		self.clear()

 		fps_display.draw()

		self.main_batch.draw()

		self.ship.draw()


game_window = Game_Window(800, 600) 

if __name__ == '__main__': 
	pyglet.app.run()