from src.gui.control_utils.button import Button
from src.gui.control_utils.slider import Slider
from src.parameters import SCREEN_HEIGHT, WHITE, GRAY, BLUE, ARCHIVED_GAME_PAUSED, ARCHIVED_GAME_TURN, SCREEN_WIDTH


class ArchivedGameUIController:
    def __init__(self):
        # Button dimensions and padding
        button_width = 80
        button_height = 40
        slider_padding = 40
        padding = 10

        # Number of buttons
        total_button_height = 4 * button_height + 3 * padding

        # Calculate the starting y position to center the buttons vertically
        y_start_position = (SCREEN_HEIGHT - total_button_height) // 2

        # Set the x position to align the buttons on the left edge
        x_position = padding

        # Calculate vertical positions for each button, starting from y_start_position
        y_position_next = y_start_position
        y_position_prev = y_position_next + button_height + padding
        y_position_play = y_position_prev + button_height + padding
        y_position_pause = y_position_play + button_height + padding
        self.__button_next = Button("Next", x_position, y_position_next, button_width, button_height, GRAY, BLUE, WHITE,
                                    self.__advance_turn)
        self.__button_prev = Button("Prev", x_position, y_position_prev, button_width, button_height, GRAY, BLUE, WHITE,
                                    self.__rewind_turn)
        self.__button_play = Button("Play", x_position, y_position_play, button_width, button_height, GRAY, BLUE, WHITE,
                                    self.__unpause_game)
        self.__button_pause = Button("Pause", x_position, y_position_pause, button_width, button_height, GRAY, BLUE,
                                     WHITE, self.__pause_game)

        # Position the slider to the right of the buttons
        slider_width = 20
        slider_height = total_button_height  # Match the height of the buttons stack
        slider_x_position = SCREEN_WIDTH - (x_position + slider_padding + padding)
        slider_y_position = y_start_position
        self.__slider = Slider(slider_x_position, slider_y_position, slider_width, slider_height, 0, 1, 0.5, "Speed")

        self.update_states()

    def update_states(self):
        """Update the state of the buttons based on the game state."""
        if ARCHIVED_GAME_PAUSED[0]:
            self.__button_play.disabled = False
            self.__button_pause.disabled = True
            self.__button_prev.disabled = False
            self.__button_next.disabled = False
        else:
            self.__button_play.disabled = True
            self.__button_pause.disabled = False
            self.__button_prev.disabled = True
            self.__button_next.disabled = True

    def __unpause_game(self):
        """Unpause the game and update button states."""
        ARCHIVED_GAME_PAUSED[0] = False
        self.update_states()

    def __pause_game(self):
        """Pause the game and update button states."""
        ARCHIVED_GAME_PAUSED[0] = True
        self.update_states()

    @staticmethod
    def __advance_turn():
        """Advance to the next turn."""
        ARCHIVED_GAME_TURN[0] += 1

    @staticmethod
    def __rewind_turn():
        """Rewind to the previous turn."""
        ARCHIVED_GAME_TURN[0] -= 1

    def handle_mouse_click(self, mouse_pos):
        self.__button_play.check_click(mouse_pos)
        self.__button_pause.check_click(mouse_pos)
        self.__button_prev.check_click(mouse_pos)
        self.__button_next.check_click(mouse_pos)
        self.__slider.handle_event(mouse_pos)

    def draw(self, screen):
        self.__button_play.draw(screen)
        self.__button_pause.draw(screen)
        self.__button_prev.draw(screen)
        self.__button_next.draw(screen)
        self.__slider.draw(screen)