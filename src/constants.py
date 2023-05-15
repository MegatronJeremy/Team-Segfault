# server info
HOST_NAME = "wgforge-srv.wargaming.net"
HOST_PORT = 443

# message format constants
BYTES_IN_INT = 4
DEFAULT_BUFFER_SIZE = 4096

# game name
GAME_NAME = ['Test game']

# gui constants
GUI_CAPTION = 'Team Segfault'
FPS_MAX = 60  # max frames per second
SCREEN_SIZE = 250
SCREEN_RATIO = (4, 3)
SCREEN_WIDTH = SCREEN_RATIO[0] * SCREEN_SIZE
SCREEN_HEIGHT = SCREEN_RATIO[1] * SCREEN_SIZE
HEX_RADIUS_X = [-1]
HEX_RADIUS_Y = [-1]

# mab constants
DEFAULT_ACTION_FILE = 'v5'

TANK_PULSE_FULL_DURATION = 20
TANK_SHADOW_MAX_SCALE = 2.5
HEX_TILE_IMAGES_SCALE = (2.0, 1.8)
TANK_IMAGE_SCALE = 1.5
EXPLOSION_IMAGE_SCALE = 2.0
MAP_FONT_SIZE_MULTIPLIER = 1.2

ERROR_FONT_SIZE = SCREEN_HEIGHT // 15

ADVANCED_GRAPHICS = [True]
EXPLOSION_SPEED = 4
BULLET_TRAVEL_TIME = 6

PODIUM_WIDTH = SCREEN_WIDTH * 3 / 4
PODIUM_SCALE = 6
# position of menus in %, relative to the window size
MENU_POSITION = (0, 100)
MENU_MIN_WIDTH = SCREEN_WIDTH / 4
TRACKS_SCALE = (SCREEN_WIDTH * 3 / 4, SCREEN_HEIGHT / 10)
LOADING_ANIMATION_LIMIT = 50

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GAME_BACKGROUND = (47, 31, 128)
PLAYER_COLORS = ((224, 206, 70), (70, 191, 224), (201, 26, 40))  # yellow, blue, red; third could be (227, 61, 116)
BASE_COLOR = (39, 161, 72)
EMPTY_COLOR = (87, 81, 81)
OBSTACLE_COLOR = (51, 46, 46)
DEFAULT_SPAWN_COLOR = (135, 126, 126)

MENU_TEXT_COLOR = (159, 255, 25)
MENU_SELECTED_TEXT_COLOR = (48, 240, 144)
MENU_BACKGROUND_TEXT_COLOR = (0, 0, 255, 128)
MENU_BACKGROUND_COLOR = (62, 62, 66, 192)

LOADING_BAR_BACKGROUND_COLOR = (46, 57, 74)

SHOT_TANK_OUTLINE_COLOR = (255, 0, 0)

SELECTOR_WIDGET_COLOR = (0, 0, 0, 0)

ERROR_MESSAGE_COLOR = (247, 37, 37)

PODIUM_COLORS = ((255, 215, 0), (192, 192, 192), (205, 127, 50))
# player names
PLAYER_NAMES = ['Playa', 'Bot 1', 'Bot 2', 'Bot 3']

# game options
# game speed range is [0.0 - 1.0]; represents (1 - game_speed) seconds sleep between turns
GAME_SPEED = [1.0]
SOUND_VOLUME = [0.0]
MAX_PLAYERS = 3
DEFAULT_NUM_TURNS = 45
# sound paths
EXPLOSION_SOUND = 'src/assets/sounds/explosion.mp3'
BULLET_SOUND = 'src/assets/sounds/shot.mp3'

# font paths
MENU_FONT = 'src/assets/menu/BrunoAceSC-Regular.ttf'

# image paths
TANK_ICON_PATH = 'src/assets/tank_icon.png'
SPG_IMAGE_PATH = 'src/assets/tank_classes/spg.png'
HT_IMAGE_PATH = 'src/assets/tank_classes/ht.png'
LT_IMAGE_PATH = 'src/assets/tank_classes/lt.png'
MT_IMAGE_PATH = 'src/assets/tank_classes/mt.png'
TD_IMAGE_PATH = 'src/assets/tank_classes/td.png'

CATAPULT_IMAGE_PATH = 'src/assets/bonuses/catapult.png'
LIGHT_REPAIR_IMAGE_PATH = 'src/assets/bonuses/light_repair.png'
HARD_REPAIR_IMAGE_PATH = 'src/assets/bonuses/hard_repair.png'

FLAG_PATH = 'src/assets/flag.png'
EXPLOSION_IMAGES = [f'src/assets/explosion_images/{i}.png' for i in range(7)]
BULLET_IMAGE_PATH = 'src/assets/white_bullet.png'

BACKGROUND_IMAGE_PATH = 'src/assets/menu/background.jpg'
GUI_ICON_PATH = 'src/assets/icon.png'
TRACKS_IMAGE_PATH = 'src/assets/tracks_green.png'
TROPHY_IMAGE_PATH = 'src/assets/trophy.png'

# map hexes
SUMMER_GRASS_PATH = 'src/assets/hex_images/summer_empty.png'
SUMMER_OBSTACLE_PATH = 'src/assets/hex_images/summer_obstacle.png'
DESERT_EMPTY_PATH = 'src/assets/hex_images/desert_empty.png'
DESERT_OBSTACLE_PATH = 'src/assets/hex_images/desert_obstacle.png'
WINTER_EMPTY_PATH = 'src/assets/hex_images/winter_empty.png'
WINTER_OBSTACLE_PATH = 'src/assets/hex_images/winter_obstacle.png'

# other
BULLET_VECTOR = (1, 0)
MAP_TYPE = ['']
