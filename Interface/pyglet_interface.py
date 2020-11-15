import pyglet
from pyglet import font
from pyglet.window import mouse
from pyglet.window import key
from dataclasses import dataclass
from generation_function import generate_plots

@dataclass
class Region:
    bottom_left_x: int
    bottom_left_y: int
    height: int
    width: int

    def in_region(self, x, y):
        if x > self.bottom_left_x and x < self.bottom_left_x+self.width and y > self.bottom_left_y and y < self.bottom_left_y+self.height:
            return True
        else:
            return False

global ACTIVE_WORD, main_display

INTERFACE_PATH = "/Users/jamesashford/Documents/Projects/Hackathons/Oxford Hack 2020/OxHack-2020/Interface"
RSC_PATH = f"{INTERFACE_PATH}/rsc"
OUTPUT_PATH = f"{INTERFACE_PATH}/output"
WIDTH, HEIGHT = 1440, 898
ACTIVE_WORD = "ENTER QUERY"

# Load in font
font.add_file(f'{RSC_PATH}/swiss_911_ultra_compressed_bt.ttf')
font.load(f'{RSC_PATH}/swiss_911_ultra_compressed_bt.ttf', 16)

window = pyglet.window.Window(WIDTH, HEIGHT, "Twitter Analysis")
background = pyglet.image.load(f"{RSC_PATH}/oxhack2020_background.png")

generate_button = Region(1190, 740, 75, 210)

search_word = pyglet.text.Label(ACTIVE_WORD,
                          font_name='Swiss911 UCm BT',
                          font_size=40,
                          x=860, y=620, width=580, height=270,
                          anchor_x='left', anchor_y='bottom')

main_display = pyglet.image.load(f"{RSC_PATH}/standby.png")
main_display.anchor_x = 0; main_display.anchor_y = 0

@window.event
def on_draw():
    window.clear()
    background.blit(0, 0)
    main_display.blit(200, 80)
    search_word.draw()

@window.event
def on_mouse_press(x, y, button, modifiers):
    global ACTIVE_WORD, main_display
    if button == mouse.LEFT:
        print(f'The left mouse button was pressed at x:{x}, y:{y}')
        # Test if generate_button pressed
        if generate_button.in_region(x, y):
            print(f'Generate a Twitter Profile for "{ACTIVE_WORD}"')
            generate_plots(ACTIVE_WORD)

            # Update main plot with the 
            main_display = pyglet.image.load(f"{OUTPUT_PATH}/{ACTIVE_WORD}_coocgraph.png")
            main_display.anchor_x = 0; main_display.anchor_y = 0

@window.event
def on_key_press(symbol, modifiers):
    global ACTIVE_WORD
    # If "/" is pressed, reset the active word
    if symbol == 47:
        ACTIVE_WORD = ""
    # Enable backspacing
    if symbol == key.BACKSPACE:
        if len(ACTIVE_WORD) > 0:
            ACTIVE_WORD = ACTIVE_WORD[:-1]
    # Enable spaces
    elif symbol == key.SPACE:
        ACTIVE_WORD += " "
    # Allow letter key presses
    else:
        new_button = str(key.symbol_string(symbol))
        if new_button in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
            ACTIVE_WORD += new_button

    # Update label text
    search_word.text = ACTIVE_WORD

# Run the app
pyglet.app.run()