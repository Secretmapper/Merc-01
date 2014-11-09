import pyglet

class Layer(pyglet.graphics.Batch):

	def __init__(self, *args, **kwargs):
		super(Layer, self).__init__(**kwargs)
		self.x = 0
		self.y = 0
		self.z = 0