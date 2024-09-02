import pygame
from pygame import Surface

from src.gui.menus_and_screens.menu_utils import play_menu_music
from src.parameters import SCREEN_WIDTH, SCREEN_HEIGHT, TANK_ICON_PATH, PODIUM_COLORS, PODIUM_WIDTH, PODIUM_SCALE, \
    TROPHY_IMAGE_PATH, MENU_FONT, VICTORY_THEME
from src.settings_utils import get_music_volume


class EndScreen:
    def __init__(self):
        self.__enabled = False
        self.__tank_image = pygame.transform.scale(pygame.image.load(TANK_ICON_PATH),
                                                   (PODIUM_WIDTH / PODIUM_SCALE, PODIUM_WIDTH / PODIUM_SCALE))
        width = 2 * PODIUM_WIDTH / PODIUM_SCALE
        third_height: int = PODIUM_WIDTH / PODIUM_SCALE
        self.__positions: list[tuple[int, int, int, int]] = [
            (SCREEN_WIDTH / 2 - width / 2, SCREEN_HEIGHT - 2 * third_height, width, third_height * 2),
            (SCREEN_WIDTH / 2 - width * 1.5, SCREEN_HEIGHT - 1.5 * third_height, width, third_height * 1.5),
            (SCREEN_WIDTH / 2 + width / 2, SCREEN_HEIGHT - third_height, width, third_height)
        ]

        self.__podium_font = pygame.font.SysFont('arial', SCREEN_WIDTH // PODIUM_SCALE)
        self.__scoreboard_font = pygame.font.Font(MENU_FONT, SCREEN_WIDTH // 50)
        self.__trophy = pygame.transform.scale(pygame.image.load(TROPHY_IMAGE_PATH),
                                               (PODIUM_WIDTH / (PODIUM_SCALE * 2), PODIUM_WIDTH / (PODIUM_SCALE * 2)))

    def draw_podium(self, screen: Surface, players: list[tuple[str, str | tuple[int, int, int], int]]):
        """
        Draws podium based on a given list of player names, colors and points. The list should be sorted by points
        :param Surface screen: screen to draw on
        :param list players: sorted list of players by points, where each element is a tuple(player_name, player_color,
        player_points)
        """
        # index representing current podium position that tank should be drawn on
        current_index = 0
        longest_name_len = 0

        # draw tanks / players
        for i, player in enumerate(players):
            longest_name_len = max(longest_name_len, self.__scoreboard_font.size(player[0])[0])
            # color image
            img = self.__tank_image.copy()
            color_image = pygame.Surface(img.get_size())
            color_image.fill(player[1])
            img.blit(color_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            # draw tank
            if i > 0 and players[i - 1][2] > players[i][2]:
                current_index += 1
            offset_multiplier = i - current_index if len(players) == 3 and players[0][2] == players[2][2] \
                else 1 - i + current_index
            x = self.__positions[current_index][0] + offset_multiplier * (img.get_width() / 2)
            y = self.__positions[current_index][1] - img.get_height() * 3 / 4
            screen.blit(img, dest=(x, y))

        # write name and number of points
        for i, player in enumerate(players):
            name = self.__scoreboard_font.render(player[0], True, player[1])
            name_rect = name.get_rect()
            x, y = 0, self.__trophy.get_height() * (2 + 2 * i) // 2
            name_rect.topleft = (x, y)

            x += longest_name_len
            screen.blit(name, name_rect)
            # draw trophies for each player
            for point in range(player[2]):
                screen.blit(self.__trophy,
                            (x + point * self.__trophy.get_width(), y - self.__trophy.get_height() // 2))

        # draw podium
        for i in range(3):
            pygame.draw.rect(screen, PODIUM_COLORS[i], self.__positions[i])
            text = self.__podium_font.render(str(i + 1), True, 'black')
            text_rect = text.get_rect(center=(self.__positions[i][0] + self.__positions[i][2] // 2,
                                              self.__positions[i][1] + self.__positions[i][3] // 2))
            screen.blit(text, text_rect)

    def disable(self) -> None:
        self.__enabled = False

    def enable(self) -> None:
        play_menu_music(VICTORY_THEME, get_music_volume() * 2)
        self.__enabled = True

    @property
    def enabled(self) -> bool:
        return self.__enabled
