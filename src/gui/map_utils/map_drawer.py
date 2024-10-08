import queue

import pygame
from pygame import Surface
from pygame.font import Font
from pygame.sprite import Sprite, Group

from src.entities.tanks.tank import Tank
from src.game_map.hex import Hex
from src.gui.map_utils.feature_drawer import FeatureDrawer
from src.gui.map_utils.scoreboard import Scoreboard
from src.gui.tank_utils.explosion import Explosion
from src.gui.tank_utils.projectile import Projectile
from src.gui.tank_utils.shot_tank import ShotTank
from src.gui.tank_utils.tank_drawer import TankDrawer
from src.parameters import SCREEN_WIDTH, HEX_RADIUS_X, HEX_RADIUS_Y, WHITE, MENU_FONT, MAP_FONT_SIZE_MULTIPLIER, \
    ADVANCED_GRAPHICS, SCREEN_HEIGHT, CURRENT_GAME_NAME, DISABLE_ANIMATIONS_GLOBAL
from src.settings_utils import strip_number_from_name_end


class MapDrawer:
    def __init__(self, map_size: int, players: dict, game_map: dict, current_turn: list[int], num_turns: int,
                 num_rounds: int):
        self.__turn: list[int] = current_turn
        self.__num_turns = num_turns // len(players)
        self.__num_rounds = num_rounds
        self.__max_damage_points: int = 0
        self.__players = players
        self.__map = game_map

        Explosion.set_image_scale()
        self.__scoreboard = Scoreboard(players)
        self.__font_size = round(MAP_FONT_SIZE_MULTIPLIER * min(HEX_RADIUS_X[0], HEX_RADIUS_Y[0]))
        self.__font: Font | None = None
        self.__explosion_group: Group = Group()
        self.__projectile_group: Group = Group()
        # tanks that are shot, but not destroyed
        self.__shot_tanks_group: Group = Group()
        self.__feature_drawer = FeatureDrawer(map_size)

        # buffered sprite creation - thread-safe queue object
        self.__explosion_group_buf: queue = queue.Queue()
        self.__projectile_group_buf: queue = queue.Queue()
        self.__shot_tanks_group_buf: queue = queue.Queue()

        # tanks
        self.__tanks: Group = Group()
        for _, entities in self.__map.items():
            tank = entities['tank']
            if tank is not None:
                self.__tanks.add(TankDrawer(tank))

    def draw(self, screen: Surface, current_round: int) -> None:
        if self.__font is None:
            self.__font = pygame.font.Font(MENU_FONT, self.__font_size)

        # display tanks and features
        for coord, entities in self.__map.items():
            feature, tank = entities['feature'], entities['tank']
            self.__feature_drawer.draw(screen, feature, tank is not None)
        # create sprites form buffered data
        self.__add_sprites()

        if ADVANCED_GRAPHICS[0]:
            # draw tanks outlines for tanks that have been hit
            self.__shot_tanks_group.draw(screen)
            self.__shot_tanks_group.update()

        # draw tanks
        self.__tanks.draw(screen)
        self.__tanks.update(screen)

        # display scoreboards
        self.__scoreboard.draw_damage_scoreboard(screen, self.__font, self.__font_size, self.__max_damage_points)
        self.__scoreboard.draw_capture_scoreboard(screen, self.__font, self.__font_size)

        if ADVANCED_GRAPHICS[0]:
            # draw explosions
            self.__explosion_group.draw(screen)
            self.__explosion_group.update()

            # draw projectiles
            self.__projectile_group.draw(screen)
            self.__projectile_group.update()

        # display turn
        if self.__turn is not None:
            turn = self.__turn[0] // len(self.__players)
            text = self.__font.render('Turn: ' + str(turn) + '/' + str(self.__num_turns), True, WHITE)
            text_rect = text.get_rect(midtop=(SCREEN_WIDTH // 2, 0))
            screen.blit(text, text_rect)

        # display round
        text = self.__font.render('Match: ' + str(current_round) + '/' + str(self.__num_rounds), True, WHITE)
        text_rect = text.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT))
        screen.blit(text, text_rect)

        # display game name
        text = self.__font.render(f' Game name: {strip_number_from_name_end(CURRENT_GAME_NAME[0])}', True, WHITE)
        text_rect = text.get_rect(bottomleft=(0, SCREEN_HEIGHT))
        screen.blit(text, text_rect)

        # draw map legend
        self.__feature_drawer.draw_legend(screen, self.__font)

    def __add_sprites(self) -> None:
        # add tank shadows
        while not self.__shot_tanks_group_buf.empty():
            coords, image_path, color, shot_ended = self.__shot_tanks_group_buf.get()
            tank: Sprite = ShotTank(coords, image_path, color, shot_ended)
            self.__shot_tanks_group.add(tank)

        # add explosions
        while not self.__explosion_group_buf.empty():
            coord, shot_ended = self.__explosion_group_buf.get()
            explosion: Sprite = Explosion(Hex.make_center(coord), shot_ended)
            self.__explosion_group.add(explosion)

        # add projectiles
        while not self.__projectile_group_buf.empty():
            start_pos, end_pos, color, shot_ended = self.__projectile_group_buf.get()
            projectile: Sprite = Projectile(start_pos, end_pos, color, shot_ended)
            self.__projectile_group.add(projectile)

    """Adding sprites to their group"""

    def add_explosion(self, tank: Tank, target: Tank, shot_ended: list[bool]) -> None:
        if DISABLE_ANIMATIONS_GLOBAL[0]:
            return

        self.__max_damage_points = \
            max(self.__max_damage_points, self.__players[tank.player_id].damage_points)

        self.__explosion_group_buf.put((target.coord, shot_ended))

    def add_shot(self, start_pos: tuple[int, int], end_pos: tuple[int, int], color: tuple[int, int, int],
                 shot_ended: list[bool]) -> None:
        if DISABLE_ANIMATIONS_GLOBAL[0]:
            return

        self.__projectile_group_buf.put((start_pos, end_pos, color, shot_ended))

    def add_hitreg(self, coords: tuple[int, int], image_path: str, color: str | tuple[int, int, int] = None,
                   shot_ended: list[bool] = None):
        if DISABLE_ANIMATIONS_GLOBAL[0]:
            return

        self.__shot_tanks_group_buf.put((coords, image_path, color, shot_ended))
