import pygame
import pygame_menu

from src.constants import MENU_POSITION, SOUND_VOLUME, PLAYER_NAMES, GAME_NAME, WHITE, MENU_BACKGROUND_COLOR, \
    MENU_SELECTED_TEXT_COLOR, GAME_SPEED, MENU_MIN_WIDTH, MENU_FONT, ADVANCED_GRAPHICS, SELECTOR_WIDGET_COLOR, \
    MAX_PLAYERS, MENU_THEME, MUSIC_VOLUME, BATTLE_THEME, MAP_TYPE
from src.game_presets.game_type_enum import GameType
from src.gui.map_utils.map_type_enum import MapType
from src.gui.menus_and_screens.menu_utils import play_menu_music


class Menu:
    def __init__(self, menu_width: int, menu_height: int, start_game_function):
        self.__start_game_function = start_game_function

        self.__menu_width = menu_width
        self.__menu_height = menu_height

        self.__create_menu_theme()

        # submenus need to be created before main menu
        self.__create_options_menu()
        self.__create_multiplayer_menu()
        self.__create_credits_menu()
        self.__create_local_game_menu()
        self.__create_main_menu()

        self.__is_enabled = self.__main_menu.is_enabled()

    """Menu callbacks"""

    @staticmethod
    def __set_advanced_graphics(value: bool) -> None:
        ADVANCED_GRAPHICS[0] = value

    @staticmethod
    def __set_map_type(map_type: tuple[str, int], value: int) -> None:
        MAP_TYPE[0] = value

    @staticmethod
    def __set_game_speed(value: float) -> None:
        GAME_SPEED[0] = value

    @staticmethod
    def __set_sound_volume(value: float) -> None:
        SOUND_VOLUME[0] = value

    @staticmethod
    def __set_music_volume(value: float) -> None:
        MUSIC_VOLUME[0] = value
        pygame.mixer.music.set_volume(value)

    """Menu creation"""

    def __create_main_menu(self) -> None:
        self.__main_menu: pygame_menu.Menu = pygame_menu.Menu('Main menu', self.__menu_width, self.__menu_height,
                                                              theme=self.__menu_theme, position=MENU_POSITION,
                                                              mouse_motion_selection=True)
        self.__main_menu.add.button('Play local game', self.__local_game_menu)
        self.__main_menu.add.button('Play multiplayer game', self.__multiplayer_menu)
        self.__main_menu.add.button('Options', self.__options_menu)
        self.__main_menu.add.button('Credits', self.__credits)

        self.__main_menu.add.button('Quit', pygame_menu.events.EXIT)
        Menu.set_menu_size(self.__main_menu)
        if self.__main_menu.get_width() < MENU_MIN_WIDTH:
            self.__main_menu.resize(MENU_MIN_WIDTH, self.__main_menu.get_height())

        play_menu_music(MENU_THEME, MUSIC_VOLUME[0])

    def __create_options_menu(self) -> None:
        self.__options_menu: pygame_menu.Menu = pygame_menu.Menu('Options', self.__menu_width, self.__menu_height,
                                                                 theme=self.__menu_theme, mouse_motion_selection=True)
        self.__options_menu.add.toggle_switch('Advanced graphics: ', default=ADVANCED_GRAPHICS[0],
                                              toggleswitch_id='graphics',
                                              onchange=self.__set_advanced_graphics)
        self.__options_menu.add.selector('Game map ', [(map_type.name, map_type.value) for map_type in MapType],
                                         selector_id='map_type', style='fancy',
                                         style_fancy_bgcolor=SELECTOR_WIDGET_COLOR,
                                         onchange=self.__set_map_type)
        self.__options_menu.add.range_slider('Game speed', default=GAME_SPEED[0], range_values=(0, 1), increment=0.1,
                                             rangeslider_id='game_speed_slider',
                                             onchange=self.__set_game_speed)
        self.__options_menu.add.range_slider('Sound volume', default=SOUND_VOLUME[0], range_values=(0, 1),
                                             increment=0.1, rangeslider_id='sound_volume_slider',
                                             onchange=self.__set_sound_volume)
        self.__options_menu.add.range_slider('Music volume', default=MUSIC_VOLUME[0], range_values=(0, 1),
                                             increment=0.1, rangeslider_id='music_volume_slider',
                                             onchange=self.__set_music_volume)
        self.__options_menu.add.button('Back', pygame_menu.events.BACK)
        Menu.set_menu_size(self.__options_menu)

    def __create_local_game_menu(self) -> None:
        self.__local_game_menu: pygame_menu.Menu = pygame_menu.Menu('Local game', self.__menu_width, self.__menu_height,
                                                                    theme=self.__menu_theme,
                                                                    onclose=pygame_menu.events.BACK,
                                                                    mouse_motion_selection=True, menu_id='local')
        self.__local_game_menu.add.button('Battle!', self.__battle)
        self.__local_game_menu.add.text_input('Number of turns: ', input_type=pygame_menu.locals.INPUT_INT, maxchar=2,
                                              textinput_id='num_turns')
        self.__local_game_menu.add.range_slider('Number of players', default=MAX_PLAYERS, rangeslider_id='num_players',
                                                range_values=[i for i in range(1, MAX_PLAYERS + 1)], increment=1)
        self.__local_game_menu.add.toggle_switch('Advanced AI', default=True, toggleswitch_id='advanced_ai')
        self.__local_game_menu.add.toggle_switch('Full game', default=True, toggleswitch_id='full_game')
        self.__local_game_menu.add.button('Back', pygame_menu.events.BACK)

        Menu.set_menu_size(self.__local_game_menu)

    def __create_multiplayer_menu(self) -> None:
        self.__multiplayer_menu: pygame_menu.Menu = pygame_menu.Menu('Play', self.__menu_width, self.__menu_height,
                                                                     theme=self.__menu_theme,
                                                                     onclose=pygame_menu.events.BACK
                                                                     , mouse_motion_selection=True)
        self.__multiplayer_menu.add.button('Battle!', self.__battle)
        self.__multiplayer_menu.add.text_input('Nickname: ', default=PLAYER_NAMES[0], textinput_id='nickname',
                                               maxwidth=10)
        self.__multiplayer_menu.add.text_input('Password:', default='', textinput_id='password', maxwidth=10,
                                               password=True)
        self.__multiplayer_menu.add.text_input('Game name: ', default=GAME_NAME[0], textinput_id='game_name',
                                               maxwidth=10)
        self.__multiplayer_menu.add.text_input('Number of turns: ', input_type=pygame_menu.locals.INPUT_INT, maxchar=2,
                                               textinput_id='num_turns')
        self.__multiplayer_menu.add.range_slider('Number of players', default=MAX_PLAYERS, rangeslider_id='num_players',
                                                 range_values=[i for i in range(1, MAX_PLAYERS + 1)], increment=1)
        self.__multiplayer_menu.add.toggle_switch('Advanced AI', default=True, toggleswitch_id='advanced_ai')
        self.__multiplayer_menu.add.toggle_switch('Full game', default=True, toggleswitch_id='full_game')
        self.__multiplayer_menu.add.toggle_switch('Observer', default=False, toggleswitch_id='observer',
                                                  state_text=('No', 'Yes'))
        self.__multiplayer_menu.add.button('Back', pygame_menu.events.BACK)

        Menu.set_menu_size(self.__multiplayer_menu)

    def __create_credits_menu(self) -> None:
        self.__credits: pygame_menu.Menu = pygame_menu.Menu('Credits', self.__menu_width, self.__menu_height,
                                                            theme=self.__menu_theme, mouse_motion_selection=True)
        self.__credits.add.label('Vuk Djordjevic')
        self.__credits.add.label('Ricardo Suarez del Valle')
        self.__credits.add.label('Jovan Milanovic')
        self.__credits.add.button('Back', pygame_menu.events.BACK)
        Menu.set_menu_size(self.__credits)

    def __create_menu_theme(self) -> None:
        self.__menu_theme = pygame_menu.themes.THEME_DARK.copy()
        self.__menu_theme.title = False
        self.__menu_theme.background_color = MENU_BACKGROUND_COLOR
        self.__menu_theme.widget_font = pygame_menu.font.FONT_NEVIS
        self.__menu_theme.selection_color = MENU_SELECTED_TEXT_COLOR
        self.__menu_theme.widget_font_color = WHITE
        self.__menu_theme.widget_alignment = pygame_menu.locals.ALIGN_LEFT
        self.__menu_theme.widget_font = MENU_FONT

    def __battle(self) -> None:
        game_type: GameType

        if pygame_menu.Menu.get_current(self.__main_menu).get_id() == 'local':
            game_type = GameType.LOCAL
        else:
            game_type = GameType.ONLINE

        play_menu_music(BATTLE_THEME, MUSIC_VOLUME[0] * 2)

        self.__start_game_function(game_type=game_type,
                                   is_full=self.__local_game_menu.get_widget('full_game').get_value(),
                                   use_advanced_ai=self.__local_game_menu.get_widget('advanced_ai').get_value(),
                                   num_players=self.__local_game_menu.get_widget('num_players').get_value(),
                                   num_turns=int(self.__local_game_menu.get_widget('num_turns').get_value()))

    def disable(self) -> None:
        self.__main_menu.disable()

    def enable(self) -> None:
        play_menu_music(MENU_THEME, MUSIC_VOLUME[0])
        self.__main_menu.enable()

    def draw(self, screen) -> None:
        if self.__main_menu.is_enabled():
            self.__main_menu.draw(screen)

    def update(self, events: list[pygame.event.Event]) -> None:
        self.__main_menu.update(events)

    def is_enabled(self) -> bool:
        return self.__main_menu.is_enabled()

    """Multiplayer options"""

    @property
    def game_name(self) -> str:
        return self.__multiplayer_menu.get_widget('game_name').get_value()

    @property
    def player_name(self) -> str:
        return self.__multiplayer_menu.get_widget('nickname').get_value()

    @property
    def password(self) -> str:
        return self.__multiplayer_menu.get_widget('password').get_value()

    @property
    def observer(self) -> bool:
        return self.__multiplayer_menu.get_widget('observer').get_value()

    """Global options"""

    @staticmethod
    def set_menu_size(menu: pygame_menu.Menu) -> None:
        max_width, height = 1, 1
        for widget in menu.get_widgets():
            max_width = max(max_width, widget.get_width())
            height += widget.get_height()

        menu.resize(max_width, height, position=MENU_POSITION)
