import pyglet
from pyglet import font
from pyglet.window import mouse
from pyglet.window import key
from dataclasses import dataclass
from backend_generation import generate_plots

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

global ACTIVE_WORD, VIEW_DICT, VIEW_MODE, main_display

INTERFACE_PATH = "/Users/jamesashford/Documents/Projects/Hackathons/Oxford Hack 2020/OxHack-2020/TCARS"
RSC_PATH = f"{INTERFACE_PATH}/rsc"
OUTPUT_PATH = f"{INTERFACE_PATH}/output"
WIDTH, HEIGHT = 1440, 898
ACTIVE_WORD = "ENTER QUERY"
VIEW_MODE = 1
VIEW_DICT = {1: "wordcloud",
             2: "coocgraph",
             3: "psplot"}

# Load in font
font.add_file(f'{RSC_PATH}/swiss_911_ultra_compressed_bt.ttf')
font.load(f'{RSC_PATH}/swiss_911_ultra_compressed_bt.ttf', 16)

# Generate window for app
window = pyglet.window.Window(WIDTH, HEIGHT, "Twitter Analysis")

# Title and Search Labels
title = pyglet.text.Label("TCARS",
                          font_name='Swiss911 UCm BT',
                          font_size=90,
                          x=150, y=800, width=250, height=100,
                          anchor_x='left', anchor_y='bottom')
subtitle = pyglet.text.Label("Twitter Content Access/Retrieval System",
                          font_name='Swiss911 UCm BT',
                          font_size=30,
                          x=150, y=670, width=250, height=100,
                          anchor_x='left', anchor_y='bottom')
search_word = pyglet.text.Label(ACTIVE_WORD,
                          font_name='Swiss911 UCm BT',
                          font_size=40,
                          x=860, y=620, width=580, height=270,
                          anchor_x='left', anchor_y='bottom')

# Button Regions
generate_button = Region(1190, 740, 75, 210)
wordcloud_buttom = Region(1280, 603, 35, 40)
coocgraph_buttom = Region(1280, 368, 35, 40)
psplot_buttom = Region(1280, 153, 35, 40)

# Button Labels
wordcloud_label = pyglet.image.load(f"{RSC_PATH}/button_word_cloud.png")
wordcloud_label.anchor_x = 0; wordcloud_label.anchor_y = 0
coocgraph_label = pyglet.image.load(f"{RSC_PATH}/button_cooc_graph.png")
coocgraph_label.anchor_x = 0; coocgraph_label.anchor_y = 0
psplot_label = pyglet.image.load(f"{RSC_PATH}/button_polsub_graph.png")
psplot_label.anchor_x = 0; psplot_label.anchor_y = 0

# Main Images
background = pyglet.image.load(f"{RSC_PATH}/oxhack2020_background.png")
main_display = pyglet.image.load(f"{RSC_PATH}/standby.png")
main_display.anchor_x = 0; main_display.anchor_y = 0

# Twitter Logo (for fun!)
twitter_logo = pyglet.image.load(f"{RSC_PATH}/twitter_logo.png")
twitter_logo.anchor_x = 0; twitter_logo.anchor_y = 0


@window.event
def on_draw():
    window.clear()

    background.blit(0, 0)
    twitter_logo.blit(400, 800)
    wordcloud_label.blit(1230, 560)
    coocgraph_label.blit(1230, 330)
    psplot_label.blit(1230, 100)

    title.draw()
    subtitle.draw()
    
    main_display.blit(200, 100)
    
    search_word.draw()

@window.event
def on_mouse_press(x, y, button, modifiers):
    global ACTIVE_WORD, VIEW_DICT, VIEW_MODE, main_display

    SCREEN_UPDATE = True

    if button == mouse.LEFT:
        print(f'The left mouse button was pressed at x:{x}, y:{y}')
        # Test if generate_button pressed
        if generate_button.in_region(x, y):
            print(f'Generate a Twitter Profile for "{ACTIVE_WORD}"')
            generate_plots(ACTIVE_WORD)
        
        # Test if wordcloud_buttom pressed
        elif wordcloud_buttom.in_region(x, y):
            print('Pressed wordcloud button. Setting plot type to wordcloud')
            VIEW_MODE = 1
        elif coocgraph_buttom.in_region(x, y):
            print('Pressed coocgraph button. Setting plot type to coocgraph')
            VIEW_MODE = 2
        elif psplot_buttom.in_region(x, y):
            print('Pressed psplot button. Setting plot type to psplot')
            VIEW_MODE = 3

        else:
            SCREEN_UPDATE = False
        
    if SCREEN_UPDATE:
        # Update main plot with the 
        main_display = pyglet.image.load(f"{OUTPUT_PATH}/{ACTIVE_WORD}_{VIEW_DICT[VIEW_MODE]}.png")
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
        if new_button in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ_0_1_2_3_4_5_6_7_8_9':
            # Remove _ from numbers
            new_button = new_button.strip("_")
            ACTIVE_WORD += new_button

    # Update label text
    search_word.text = ACTIVE_WORD

# Run the app
pyglet.app.run()