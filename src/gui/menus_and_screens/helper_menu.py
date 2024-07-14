import pygame
import pygame_menu

from src.parameters import MENU_BACKGROUND_COLOR, MENU_FONT, WHITE, MENU_SELECTED_TEXT_COLOR, SCREEN_HEIGHT, \
    SCREEN_WIDTH, PODIUM_SCALE


class HelperMenu:
    def __init__(self, *list_of_functions):
        self.__list_of_functions = list_of_functions
        self.__create_menu()

    def __create_menu(self):
        self.__menu_theme = pygame_menu.themes.THEME_DARK.copy()
        self.__menu_theme.title = False
        self.__menu_theme.background_color = MENU_BACKGROUND_COLOR
        self.__menu_theme.selection_color = MENU_SELECTED_TEXT_COLOR
        self.__menu_theme.widget_font_color = WHITE
        self.__menu_theme.widget_alignment = pygame_menu.locals.ALIGN_CENTER
        self.__menu_theme.widget_font = MENU_FONT

        self.__menu = pygame_menu.Menu('Helper', 2 * SCREEN_WIDTH // PODIUM_SCALE, SCREEN_HEIGHT // PODIUM_SCALE,
                                       theme=self.__menu_theme, mouse_motion_selection=True)
        self.__menu.add.button('Main menu', self.__close_screen)
        width, height = 1, 1
        for widget in self.__menu.get_widgets():
            width += widget.get_width()
            height += widget.get_height()
        # position it on the center
        self.__menu.resize(width, height, position=(0, 0))
        self.__menu.disable()

    def __close_screen(self) -> None:
        self.__menu.disable()
        for f in self.__list_of_functions:
            f()

    def update(self, events: list[pygame.event.Event]) -> None:
        self.__menu.update(events)

    def draw(self, screen) -> None:
        if self.__menu.is_enabled():
            self.__menu.draw(screen)

    def enable(self) -> None:
        self.__menu.enable()

    @property
    def enabled(self) -> bool:
        return self.__menu.is_enabled()
