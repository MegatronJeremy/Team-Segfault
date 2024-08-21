import json

from src.parameters import ADVANCED_GRAPHICS, MAP_TYPE, GAME_SPEED, SOUND_VOLUME, MUSIC_VOLUME


def save_settings(filename='settings.json'):
    with open(filename, 'w') as f:
        settings = {
            'ADVANCED_GRAPHICS': ADVANCED_GRAPHICS[0],
            'MAP_TYPE': MAP_TYPE[0],
            'GAME_SPEED': GAME_SPEED[0],
            'SOUND_VOLUME': SOUND_VOLUME[0],
            'MUSIC_VOLUME': MUSIC_VOLUME[0]
        }

        json.dump(settings, f, indent=4)


# Function to load settings from a file
def load_settings(filename='settings.json'):
    try:
        with open(filename, 'r') as f:
            settings_file = json.load(f)

            ADVANCED_GRAPHICS[0] = settings_file.get('ADVANCED_GRAPHICS')
            MAP_TYPE[0] = settings_file.get('MAP_TYPE')
            GAME_SPEED[0] = settings_file.get('GAME_SPEED')
            SOUND_VOLUME[0] = settings_file.get('SOUND_VOLUME')
            MUSIC_VOLUME[0] = settings_file.get('MUSIC_VOLUME')
    except FileNotFoundError:
        print("Settings file not found, using default settings.")
