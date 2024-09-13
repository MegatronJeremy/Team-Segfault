# server info
HOST_NAME = "wgforge-srv.wargaming.net"
HOST_PORT = 443

# message format constants
BYTES_IN_INT = 4
DEFAULT_BUFFER_SIZE = 4096

# game name
DEFAULT_GAME_NAME = ['Test game']
CURRENT_GAME_NAME = ['']

# player names
PLAYER_NAMES_BY_IDX: dict[int, str] = {}

# gui constants
GUI_CAPTION = 'Team Segfault'
FPS_MAX = 60  # max frames per second
FPS_CURRENT = [0]  # current frames per second
SCREEN_SIZE = 250
SCREEN_RATIO = (4, 3)
SCREEN_WIDTH = SCREEN_RATIO[0] * SCREEN_SIZE
SCREEN_HEIGHT = SCREEN_RATIO[1] * SCREEN_SIZE
HEX_RADIUS_X = [-1]
HEX_RADIUS_Y = [-1]

# archived game parameters
ARCHIVED_GAME_SPEED = [0]
MIN_ARCHIVED_GAME_DELAY = 0.3
MAX_ARCHIVED_GAME_DELAY = 3.0
ARCHIVED_GAME_TURN = [0]
ARCHIVED_GAME_MAX_TURN = [0]
ARCHIVED_GAME_PAUSED = [True]

# mab constants
DEFAULT_ACTION_FILE = 'v6'

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
ANIMATION_SPEED_MULTIPLIER = [1.0]
DISABLE_ANIMATIONS_GLOBAL = [False]

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
GRAY = (100, 100, 100)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
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
SHOOTING_TANK_OUTLINE_COLOR = (0, 0, 255)

SELECTOR_WIDGET_COLOR = (0, 0, 0, 0)

ERROR_MESSAGE_COLOR = (247, 37, 37)

PODIUM_COLORS = ((255, 215, 0), (192, 192, 192), (205, 127, 50))
# player names
PLAYER_NAMES = ['Playa', 'Bot 1', 'Bot 2', 'Bot 3']

# game options
# game speed range is [0.0 - 1.0]; represents (1 - game_speed) seconds slept between turns
GAME_SPEED = [1.0]
SOUND_VOLUME = [0.1]
SOUND_MUTED = [False]
MUSIC_VOLUME = [0.1]
MUSIC_MUTED = [False]
MAX_PLAYERS = 3
DEFAULT_NUM_TURNS = 45
DEFAULT_NUM_TURNS_ONE_PLAYER = 15

import os

# get the directory where the current script is located
SCRIPT_DIR = os.path.dirname(__file__)

# define the base directory for the assets
ASSETS_LOCATION = os.path.join(SCRIPT_DIR, '../assets')

# define the base directory for the replays
REPLAYS_LOCATION = os.path.join(SCRIPT_DIR, '../replays')

# sound paths
EXPLOSION_SOUND = os.path.join(ASSETS_LOCATION, 'sounds', 'explosion.mp3')
BULLET_SOUND = os.path.join(ASSETS_LOCATION, 'sounds', 'shot.mp3')

# music paths
MENU_THEME = os.path.join(ASSETS_LOCATION, 'music', 'Menu-Theme.mp3')
BATTLE_THEME = os.path.join(ASSETS_LOCATION, 'music', 'Battle-Theme.mp3')
VICTORY_THEME = os.path.join(ASSETS_LOCATION, 'music', 'Fanfare.mp3')

# font path
MENU_FONT = os.path.join(ASSETS_LOCATION, 'menu', 'BrunoAceSC-Regular.ttf')

# settings file path
SETTINGS_FILE = os.path.join(SCRIPT_DIR, '../settings.json')

# image paths
TANK_ICON_PATH = os.path.join(ASSETS_LOCATION, 'tank_icon.png')
SPG_IMAGE_PATH = os.path.join(ASSETS_LOCATION, 'tank_classes', 'spg.png')
HT_IMAGE_PATH = os.path.join(ASSETS_LOCATION, 'tank_classes', 'ht.png')
LT_IMAGE_PATH = os.path.join(ASSETS_LOCATION, 'tank_classes', 'lt.png')
MT_IMAGE_PATH = os.path.join(ASSETS_LOCATION, 'tank_classes', 'mt.png')
TD_IMAGE_PATH = os.path.join(ASSETS_LOCATION, 'tank_classes', 'td.png')

CATAPULT_IMAGE_PATH = os.path.join(ASSETS_LOCATION, 'bonuses', 'catapult.png')
LIGHT_REPAIR_IMAGE_PATH = os.path.join(ASSETS_LOCATION, 'bonuses', 'light_repair.png')
HARD_REPAIR_IMAGE_PATH = os.path.join(ASSETS_LOCATION, 'bonuses', 'hard_repair.png')

FLAG_PATH = os.path.join(ASSETS_LOCATION, 'flag.png')
EXPLOSION_IMAGES = [os.path.join(ASSETS_LOCATION, 'explosion_images', f'{i}.png') for i in range(8)]
BULLET_IMAGE_PATH = os.path.join(ASSETS_LOCATION, 'white_bullet.png')

BACKGROUND_IMAGE_PATH = os.path.join(ASSETS_LOCATION, 'menu', 'background.jpg')
GUI_ICON_PATH = os.path.join(ASSETS_LOCATION, 'icon.png')
TRACKS_IMAGE_PATH = os.path.join(ASSETS_LOCATION, 'tracks_green.png')
TROPHY_IMAGE_PATH = os.path.join(ASSETS_LOCATION, 'trophy.png')

# map hexes
SUMMER_GRASS_PATH = os.path.join(ASSETS_LOCATION, 'hex_images', 'summer_empty.png')
SUMMER_OBSTACLE_PATH = os.path.join(ASSETS_LOCATION, 'hex_images', 'summer_obstacle.png')
DESERT_EMPTY_PATH = os.path.join(ASSETS_LOCATION, 'hex_images', 'desert_empty.png')
DESERT_OBSTACLE_PATH = os.path.join(ASSETS_LOCATION, 'hex_images', 'desert_obstacle.png')
WINTER_EMPTY_PATH = os.path.join(ASSETS_LOCATION, 'hex_images', 'winter_empty.png')
WINTER_OBSTACLE_PATH = os.path.join(ASSETS_LOCATION, 'hex_images', 'winter_obstacle.png')

# other
BULLET_VECTOR = (1, 0)
MAP_TYPE = ['']
