import pyglet
import game.states


class Game_Window(pyglet.window.Window):

    def __init__(self, width, height):
        super(Game_Window, self).__init__(width, height)
        self.state = game.states.Play_State(self, width, height)

    def on_mouse_motion(self, x, y, dx, dy):
        self.state.on_mouse_motion(x, y, dx, dy)

    def on_key_press(self, symbol, modifiers):
        self.state.on_key_press(symbol, modifiers)

    def on_update(self, dt):
        self.state.on_update(dt)

    def on_draw(self, ):
        self.state.on_draw()

game_window = Game_Window(800, 600)

if __name__ == '__main__':
    pyglet.app.run()
