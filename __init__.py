import pyglet
import game.states
import game.constants as CONSTS


class Game_Window(pyglet.window.Window):

    def __init__(self, width, height):
        super(Game_Window, self).__init__(width, height, fullscreen=True)
        self.menu = True
        self.state = game.states.Menu_State()
        pyglet.clock.set_fps_limit(60)
        pyglet.clock.schedule(self.on_update)

    def on_mouse_motion(self, x, y, dx, dy):
        self.state.on_mouse_motion(x, y, dx, dy)

    def on_key_press(self, symbol, modifiers):
        self.state.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        self.state.on_key_release(symbol, modifiers)

    def on_update(self, dt):
        self.state.on_update(dt)
        if self.menu and self.state.game:
            self.menu = False
            self.state = game.states.Play_State(self, 800, 600)

        if not self.menu and self.state.quit_dead:
            self.menu = True
            self.state = game.states.Menu_State()

    def on_draw(self, ):
        self.state.on_draw()

game_window = Game_Window(800, 600)

if __name__ == '__main__':
    pyglet.app.run()
