import pygame

from src.gui.control_utils.button import Button
from src.parameters import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GRAY, RED, BLACK, MUSIC_MUTED, SOUND_MUTED
from src.settings_utils import get_music_volume


class BaseGameUIController:
    def __init__(self, display_manager):
        self.__display_manager = display_manager

        self.stop_enabled = False
        self.sound_control_enabled = True

        # Button dimensions and padding
        button_width = 90
        button_height = 35
        padding = button_height // 10

        # Calculate total width of all three buttons including padding
        total_buttons_width = button_width * 3 + 2 * padding

        # Calculate the starting x position to align the group of buttons to the right
        buttons_x_start_position = SCREEN_WIDTH - total_buttons_width - padding

        # Set the y position to align the buttons further down
        y_position = SCREEN_HEIGHT - button_height - padding

        # Positions for the buttons
        x_position_stop = buttons_x_start_position - padding * 2  # Position for STOP button
        x_position_mute_music = buttons_x_start_position + button_width + padding  # Mute Music button
        x_position_mute_sfx = x_position_mute_music + button_width + padding  # Mute SFX button

        # Create STOP button with red color
        self.__button_stop = Button("STOP", x_position_stop, y_position, button_width, button_height, GRAY, RED, WHITE,
                                    self.__stop_game)

        # Create Mute Music button without an icon
        self.__button_mute_music = Button("Mute Music", x_position_mute_music, y_position, button_width, button_height,
                                          GRAY, BLACK, WHITE, self.__toggle_mute_music)

        # Create Mute Sound Effects button without an icon
        self.__button_mute_sfx = Button("Mute SFX", x_position_mute_sfx, y_position, button_width, button_height,
                                        GRAY, BLACK, WHITE, self.__toggle_mute_sfx)

        # Track mute states
        self.__music_muted = False
        self.__sfx_muted = False

    def __stop_game(self):
        """Stop the game."""
        self.__display_manager.force_close_game()

    def __toggle_mute_music(self):
        """Toggle mute state for music."""
        self.__music_muted = not self.__music_muted
        MUSIC_MUTED[0] = self.__music_muted

        if self.__music_muted:
            self.__button_mute_music.active_color = GRAY
        else:
            self.__button_mute_music.active_color = BLACK

        pygame.mixer.music.set_volume(get_music_volume())

    def __toggle_mute_sfx(self):
        """Toggle mute state for sound effects."""
        self.__sfx_muted = not self.__sfx_muted

        if self.__sfx_muted:
            self.__button_mute_sfx.active_color = GRAY
        else:
            self.__button_mute_sfx.active_color = BLACK

        SOUND_MUTED[0] = self.__sfx_muted

    def handle_mouse_click(self, mouse_pos):
        """Handle mouse click events for the buttons."""
        if self.stop_enabled:
            self.__button_stop.check_click(mouse_pos)
        if self.sound_control_enabled:
            self.__button_mute_music.check_click(mouse_pos)
            self.__button_mute_sfx.check_click(mouse_pos)

    def draw(self, screen):
        """Draw the buttons on the screen."""
        if self.stop_enabled:
            self.__button_stop.draw(screen)
        if self.sound_control_enabled:
            self.__button_mute_music.draw(screen)
            self.__button_mute_sfx.draw(screen)

    def disable_everything(self):
        self.stop_enabled = False
        self.sound_control_enabled = False

    def reset_to_default(self):
        self.stop_enabled = False
        self.sound_control_enabled = True
