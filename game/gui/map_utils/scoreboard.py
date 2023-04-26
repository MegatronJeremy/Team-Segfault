import pygame
from pygame import Surface

from constants import FLAG_PATH, TANK_ICON_PATH, HEX_RADIUS_X, HEX_RADIUS_Y


class Scoreboard:
    def __init__(self, players: dict):

        # images
        self.__tank_image = pygame.image.load(TANK_ICON_PATH)
        self.__flag = pygame.image.load(FLAG_PATH)
        self.__tank_image = pygame.transform.scale(self.__tank_image, (HEX_RADIUS_X[0] * 2, HEX_RADIUS_Y[0] * 2))
        self.__flag = pygame.transform.scale(self.__flag, (HEX_RADIUS_X[0] * 2, HEX_RADIUS_Y[0] * 2))

        # used for coloring tank icons
        self.__color_image = pygame.Surface(self.__tank_image.get_size())
        self.__rad_x_third = HEX_RADIUS_X[0] / 3
        self.__rad_y_third = HEX_RADIUS_Y[0] / 3
        # length of 4 whole hexes
        self.__max_rect_length = 4 * (2 * HEX_RADIUS_X[0])

        self.__players: () = players
        self.__n_players = len(self.__players) + 1

    """Capture scoreboards"""

    def draw_capture_scoreboard(self, screen, font, font_size):
        screen.blit(font.render(' Capture points: ', True, 'grey'), dest=(0, 0))
        self.draw_capture_scoreboard_flags(screen, font_size)

        # self.draw_capture_scoreboard_barplot(screen, font, font_size)

    def draw_capture_scoreboard_flags(self, screen, font_size):
        i = 0
        for player in self.__players.values():
            if player is not None:
                i += 1

                tank_image_rect = self.__tank_image.get_rect(topleft=(0, i * (font_size + self.__rad_y_third)))

                self.__color_image.fill(player.color)
                ti = self.__tank_image.copy()
                ti.blit(self.__color_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(ti, tank_image_rect)

                # draw flags (capture points) for each player
                for point in range(player.capture_points):
                    screen.blit(self.__flag,
                                (HEX_RADIUS_X[0] + (point + 1) * HEX_RADIUS_X[0], i * (font_size + self.__rad_y_third)))

    def draw_capture_scoreboard_barplot(self, screen: Surface, font, font_size):
        i = 0
        for player in self.__players:
            if player is not None:
                i += 1
                pygame.draw.rect(screen, player.color,
                                 (self.__rad_x_third, i * (font_size + self.__rad_y_third),
                                  player.capture_points * HEX_RADIUS_X[0], HEX_RADIUS_Y[0]))

        # draw capture points table:
        capture_points_to_win = 5
        active_players = i
        for i in range(capture_points_to_win + 1):
            x = self.__rad_x_third + HEX_RADIUS_X[0] * i
            y = font_size + self.__rad_y_third
            pygame.draw.line(screen, 'white', (x, y), (x, (active_players + 1) * y), 2)
            text = font.render(str(i), True, 'white')
            screen.blit(text, dest=(x - font_size / 2.5, (active_players + 1) * y))

    def draw_capture_scoreboard_text(self, screen, font, font_size):
        i = 0
        for player in self.__players:
            if player is not None:
                i += 1
                text = font.render('    player id ' + str(player.index) + ': '
                                   + str(player.damage_points), True, player.color)
                screen.blit(text, dest=(0, screen.get_height() - (4 - i) * (font_size + self.__rad_y_third)))

    """Damage scoreboards"""

    def draw_damage_scoreboard(self, screen, font, font_size, max_damage):
        screen.blit(font.render(' Damage points: ', True, 'grey'),
                    dest=(0, screen.get_height() - (self.__n_players + 1) * (font_size + self.__rad_y_third)))
        self.draw_damage_scoreboard_barplot(screen, font, font_size, max_damage)

        # self.draw_damage_scoreboard_text(screen, font, font_size)

    def draw_damage_scoreboard_barplot(self, screen, font, font_size, max_damage):
        i = 0
        # image width + 0.5 of x_radius for offset
        x_pos = HEX_RADIUS_X[0] * 2.5

        for player in self.__players.values():
            if player is not None:
                i += 1
                self.__color_image.fill(player.color)
                ti = self.__tank_image.copy()
                ti.blit(self.__color_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(ti,
                            (0, screen.get_height() - (self.__n_players + 1 - i) * (font_size + self.__rad_y_third)))

                # scalable bar plot for damage
                if player.damage_points != 0 and max_damage != 0:
                    # need to check max_damage as well - because of race conditions!
                    y_pos = screen.get_height() \
                            - (self.__n_players + 1 - i) * (font_size + self.__rad_y_third)  # + HEX_RADIUS_Y[0] / 4
                    width = self.__max_rect_length * player.damage_points / max_damage
                    pygame.draw.rect(screen, player.color,
                                     (x_pos, y_pos + self.__rad_y_third, width, HEX_RADIUS_Y[0]))

                    # write hp
                    text = font.render(str(player.damage_points), True, 'black')
                    screen.blit(text, dest=(x_pos, y_pos))

    def draw_damage_scoreboard_text(self, screen, font, font_size):
        i = 0
        for player in self.__players:
            if player is not None:
                i += 1
                text = font.render('    player id ' + str(player.index) + ': '
                                   + str(player.capture_points), True, player.color)
                screen.blit(text, dest=(0, i * (font_size + self.__rad_y_third)))

    """Update functions"""

    def update_image_size(self, scale_x, scale_y):
        self.__tank_image = pygame.transform.scale(self.__tank_image, (scale_x, scale_y))
        self.__flag = pygame.transform.scale(self.__flag, (scale_x, scale_y))
