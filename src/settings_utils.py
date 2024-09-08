import json
import re

from src.parameters import ADVANCED_GRAPHICS, MAP_TYPE, GAME_SPEED, SOUND_VOLUME, MUSIC_VOLUME, MUSIC_MUTED, SOUND_MUTED


def save_settings(filename='settings.json'):
    with open(filename, 'w') as f:
        settings = {
            'ADVANCED_GRAPHICS': ADVANCED_GRAPHICS[0],
            'MAP_TYPE': MAP_TYPE[0],
            'GAME_SPEED': GAME_SPEED[0],
            'SOUND_VOLUME': SOUND_VOLUME[0],
            'MUSIC_VOLUME': MUSIC_VOLUME[0],
            'SOUND_MUTED': SOUND_MUTED[0],
            'MUSIC_MUTED': MUSIC_MUTED[0]
        }

        json.dump(settings, f, indent=4)


# Function to load settings from a file
def load_settings(filename='settings.json'):
    try:
        with open(filename, 'r') as f:
            settings_file = json.load(f)

            if settings_file.get('ADVANCED_GRAPHICS'):
                ADVANCED_GRAPHICS[0] = settings_file.get('ADVANCED_GRAPHICS')
            if settings_file.get('MAP_TYPE'):
                MAP_TYPE[0] = settings_file.get('MAP_TYPE')
            if settings_file.get('GAME_SPEED'):
                GAME_SPEED[0] = settings_file.get('GAME_SPEED')
            if settings_file.get('SOUND_VOLUME'):
                SOUND_VOLUME[0] = settings_file.get('SOUND_VOLUME')
            if settings_file.get('MUSIC_VOLUME'):
                MUSIC_VOLUME[0] = settings_file.get('MUSIC_VOLUME')
            if settings_file.get('SOUND_MUTED'):
                SOUND_MUTED[0] = settings_file.get('SOUND_MUTED')
            if settings_file.get('MUSIC_MUTED'):
                MUSIC_MUTED[0] = settings_file.get('MUSIC_MUTED')
    except FileNotFoundError:
        print("Settings file not found, using default settings.")


def get_music_volume():
    return MUSIC_VOLUME[0] if not MUSIC_MUTED[0] else 0


def get_sound_volume():
    return SOUND_VOLUME[0] if not SOUND_MUTED[0] else 0


def get_original_game_name_from_filename(filename: str) -> str:
    # Find the position of the second underscore after the timestamp
    underscores = [pos for pos, char in enumerate(filename) if char == '_']
    if len(underscores) < 2:
        raise ValueError("Filename does not contain the expected format with two underscores.")

    # Extract the cleaned game name portion (after the second underscore)
    cleaned_game_name = filename[underscores[1] + 1:]

    # Replace underscores with spaces to get the original game name
    original_game_name = cleaned_game_name.replace("_", " ")

    return original_game_name


def strip_number_from_name_end(name: str) -> str:
    # Match cases like 'Name-123' or 'Name 123' or 'Name_123' at the end of the string
    return re.sub(r'[\s\-_]\d+$', '', name)
