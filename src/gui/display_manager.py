import pygame.draw
from pygame import font

from src.game_presets.archived_game import archived_game
from src.game_presets.local_game import local_game
from src.game_presets.online_game import online_game
from src.gui.control_utils.archived_game_ui_controller import ArchivedGameUIController
from src.gui.menus_and_screens.end_screen import EndScreen
from src.gui.menus_and_screens.error_screen import ErrorScreen
from src.gui.menus_and_screens.helper_menu import HelperMenu
from src.gui.menus_and_screens.loading_screen import LoadingScreen
from src.gui.menus_and_screens.menu import *
from src.parameters import FPS_MAX, FPS_CURRENT, SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_IMAGE_PATH, GUI_ICON_PATH, \
    GAME_BACKGROUND, GUI_CAPTION, ERROR_FONT_SIZE, ERROR_MESSAGE_COLOR, HEX_RADIUS_Y, ARCHIVED_GAME_TURN, \
    ARCHIVED_GAME_PAUSED

os.environ['SDL_VIDEO_CENTERED'] = '1'  # window at center


class DisplayManager:

    def __init__(self, game=None):
        pygame.init()
        pygame.display.set_icon(pygame.image.load(GUI_ICON_PATH))

        self.__screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        pygame.display.set_caption(GUI_CAPTION)

        self.__running = True
        self.__playing = False
        self.__music_paused = False

        self.__game = game
        self.__force_quit = False

        self.__clock = pygame.time.Clock()

        # load images
        self.__background_image = pygame.transform.scale(pygame.image.load(BACKGROUND_IMAGE_PATH),
                                                         (SCREEN_WIDTH, SCREEN_HEIGHT))

        # create menu
        self.__menu = Menu(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3, self.__start_the_game)

        self.__loading_screen = LoadingScreen()

        self.__error_screen: ErrorScreen = ErrorScreen()
        self.__end_screen: EndScreen = EndScreen()
        self.__helper_menu: HelperMenu = HelperMenu(self.__menu.enable, self.__error_screen.disable,
                                                    self.__end_screen.disable)

        if game:
            # I added this part - useful for supporting the tests we already have
            self.__menu.disable()
            self.__playing = True
            self.__game.start()

    def __pause_music(self) -> None:
        if not self.__music_paused:
            self.__music_paused = True
            pygame.mixer.music.pause()

    def __unpause_music(self) -> None:
        if self.__music_paused:
            self.__music_paused = False
            pygame.mixer.music.unpause()

    @staticmethod
    def __advance_turn():
        if ARCHIVED_GAME_PAUSED[0]:
            ARCHIVED_GAME_TURN[0] += 1

    @staticmethod
    def __rewind_turn():
        if ARCHIVED_GAME_PAUSED[0]:
            ARCHIVED_GAME_TURN[0] -= 1

    @staticmethod
    def __pause_game():
        ARCHIVED_GAME_PAUSED[0] = True

    @staticmethod
    def __unpause_game():
        ARCHIVED_GAME_PAUSED[0] = False

    def __start_the_game(self, game_type: GameType,
                         is_full: bool = False,
                         use_advanced_ai: bool = False,
                         num_players: int = 1,
                         game_name=DEFAULT_GAME_NAME[0],
                         num_turns: int | None = None,
                         replay_file: str | None = None) -> None:
        del self.__game
        self.__menu.disable()

        match game_type:
            case GameType.LOCAL:
                self.__game = local_game(num_players=num_players, use_advanced_ai=use_advanced_ai,
                                         num_turns=num_turns, is_full=is_full)
            case GameType.ONLINE:
                PLAYER_NAMES[0] = self.__menu.player_name
                self.__game = online_game(game_name=game_name, player_name=PLAYER_NAMES[0],
                                          num_players=num_players,
                                          use_advanced_ai=use_advanced_ai, num_turns=num_turns, is_full=is_full,
                                          is_observer=self.__menu.observer, password=self.__menu.password)
            case GameType.ARCHIVED:
                self.__archived_game_ui_controller = ArchivedGameUIController()

                self.__game = archived_game(replay_file)

        self.__playing = True
        self.__game.start()

    def __check_events(self) -> list[pygame.event.Event]:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                # set the game end
                if self.__game:
                    self.__game.over.set()
                    self.__force_quit = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    events.remove(event)  # Consume ESCAPE event to avoid menus bugging out
                if event.type == pygame.QUIT:
                    self.__running = False
            if self.__game and self.__game.is_archived:
                self.__archived_game_ui_controller.handle_mouse_click(event)
        return events

    def run(self) -> None:
        try:
            self.__run()
        finally:
            # ensure cleanup
            if self.__game:
                self.__game.over.set()
            pygame.quit()

    def __run(self) -> None:
        players = []
        while self.__running:
            self.__draw_background()

            # draw archived game ui
            if self.__game and self.__game.is_archived:
                self.__archived_game_ui_controller.draw(self.__screen)

            events = self.__check_events()

            # draw enabled menu
            if self.__menu.is_enabled():
                self.__menu.update(events)
                self.__menu.draw(self.__screen)

            if self.__helper_menu.enabled:
                self.__helper_menu.update(events)
                self.__helper_menu.draw(self.__screen)

            # check if error happened
            if self.__game and self.__game.error is not None:
                self.__error_screen.enable()
                self.__error_screen.set_error_message(self.__game.error)

                self.__helper_menu.enable()
                self.__menu.disable()

                self.__finalize_game()

            # draw the map or loading screen if the game started
            if self.__playing and not self.__game.over.is_set():
                players = self.__game.player_wins_and_info
                if self.__game.game_map:
                    self.__unpause_music()
                    self.__game.game_map.draw(self.__screen, self.__game.current_round)
                else:
                    self.__pause_music()
                    self.__loading_screen.draw(self.__screen)

            # check if game has ended
            if self.__playing and self.__game.over.is_set():
                self.__loading_screen.reset()
                self.__playing = False
                # delete shadow client and sort the list
                players = sorted(filter(lambda x: x[1] is not None, self.__game.player_wins_and_info),
                                 key=lambda x: x[2], reverse=True)

                if not self.__force_quit:
                    self.__helper_menu.enable()
                    self.__end_screen.enable()
                else:
                    self.__force_quit = False
                    self.__menu.enable()

                self.__finalize_game()

            # draw error/end screen
            if self.__end_screen.enabled:
                self.__end_screen.draw_podium(self.__screen, players)

            if self.__error_screen.enabled:
                self.__error_screen.draw_error(self.__screen)

            # get the current fps
            FPS_CURRENT[0] = int(self.__clock.get_fps())

            # delay for a constant framerate
            self.__clock.tick(FPS_MAX)

            # update display
            pygame.display.flip()

    def __draw_background(self) -> None:
        self.__screen.fill(GAME_BACKGROUND)
        self.__screen.blit(self.__background_image, (0, 0))

    def __draw_error(self, text) -> None:
        # display text
        error_number, error_msg = str(text).split(':')
        error_number = pygame.font.Font(MENU_FONT, ERROR_FONT_SIZE).render(error_number, True, ERROR_MESSAGE_COLOR)
        error_msg = pygame.font.Font(MENU_FONT, ERROR_FONT_SIZE).render(error_msg, True, ERROR_MESSAGE_COLOR)
        self.__screen.blit(error_number, ((SCREEN_WIDTH - error_number.get_width()) / 2, HEX_RADIUS_Y[0]))
        self.__screen.blit(error_msg, ((SCREEN_WIDTH - error_msg.get_width()) / 2,
                                       HEX_RADIUS_Y[0] + error_number.get_height()))

    def __finalize_game(self) -> None:
        self.__game.over.set()
        self.__game = None
        self.__playing = False
        ARCHIVED_GAME_TURN[0] = 0
        ARCHIVED_GAME_PAUSED[0] = True
