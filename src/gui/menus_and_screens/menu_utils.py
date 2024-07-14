import pygame


def play_menu_music(music_file: str, volume: float = 1.0) -> None:
    # Stop any currently playing music and play the given track
    pygame.mixer.music.stop()
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1)
