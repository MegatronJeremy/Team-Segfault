import pygame
from pygame import Surface

from src.entities.map_features.bonuses.catapult import Catapult
from src.entities.map_features.bonuses.hard_repair import HardRepair
from src.entities.map_features.bonuses.light_repair import LightRepair
from src.entities.map_features.landmarks.base import Base, Entities, Feature
from src.entities.map_features.landmarks.empty import Empty
from src.entities.map_features.landmarks.obstacle import Obstacle
from src.gui.map_utils.map_type_enum import MapType
from src.parameters import MAP_TYPE, HEX_RADIUS_Y, HEX_RADIUS_X, LIGHT_REPAIR_IMAGE_PATH, HARD_REPAIR_IMAGE_PATH, \
    TANK_IMAGE_SCALE, CATAPULT_IMAGE_PATH, HEX_TILE_IMAGES_SCALE, SUMMER_OBSTACLE_PATH, WHITE, BLACK, \
    SUMMER_GRASS_PATH, DESERT_OBSTACLE_PATH, DESERT_EMPTY_PATH, WINTER_EMPTY_PATH, WINTER_OBSTACLE_PATH


class FeatureDrawer:
    def __init__(self, map_size: int):

        self.__aaline_color: str | tuple[int, int, int] = WHITE
        self.__load_images()

        # map legend
        self.__map_legend_items: list[Feature] = []
        features = [Empty, Base, Obstacle]
        # regular hexes will always be on the screen and on top right, while bonuses will be on bottom right
        x, y, z = map_size, map_size - 1, -map_size - 1
        for i, feature in enumerate(features):
            self.__map_legend_items.append(feature((x, y - i, z + i)))

        x, y, z = map_size + 2, -map_size + 2, map_size
        bonuses = [Catapult, LightRepair, HardRepair]
        for i, bonus in enumerate(bonuses):
            self.__map_legend_items.append(bonus((x, y + i, z - i)))

    def __load_images(self) -> None:
        """Loads all necessary feature images"""
        scale_size: tuple[float, float] = (HEX_RADIUS_X[0] * TANK_IMAGE_SCALE, HEX_RADIUS_Y[0] * TANK_IMAGE_SCALE)
        self.__hard_repair_image: Surface = pygame.transform.scale(pygame.image.load(HARD_REPAIR_IMAGE_PATH),
                                                                   scale_size)
        self.__light_repair_image: Surface = pygame.transform.scale(pygame.image.load(LIGHT_REPAIR_IMAGE_PATH),
                                                                    scale_size)
        self.__catapult_image: Surface = pygame.transform.scale(pygame.image.load(CATAPULT_IMAGE_PATH), scale_size)

        empty_path: str = ''
        obstacle_path: str = ''
        match MAP_TYPE[0]:
            case MapType.SUMMER:
                empty_path = SUMMER_GRASS_PATH
                obstacle_path = SUMMER_OBSTACLE_PATH
            case MapType.WINTER:
                empty_path = WINTER_EMPTY_PATH
                obstacle_path = WINTER_OBSTACLE_PATH
                self.__aaline_color = BLACK
            case MapType.DESERT:
                empty_path = DESERT_EMPTY_PATH
                obstacle_path = DESERT_OBSTACLE_PATH

        self.__empty_image: Surface = pygame.transform.scale(pygame.image.load(empty_path),
                                                             (HEX_RADIUS_X[0] * HEX_TILE_IMAGES_SCALE[0],
                                                              HEX_RADIUS_Y[0] * HEX_TILE_IMAGES_SCALE[1])
                                                             ) if empty_path != '' else None
        self.__obstacle_image: Surface = pygame.transform.scale(
            pygame.image.load(obstacle_path), (HEX_RADIUS_X[0] * HEX_TILE_IMAGES_SCALE[0],
                                               HEX_RADIUS_Y[0] * HEX_TILE_IMAGES_SCALE[1])
        ) if obstacle_path != '' else None

    def draw(self, screen: Surface, feature: Feature, is_tank_there: bool) -> None:
        """Renders the hexagon on the screen and draw a white border around the hexagon"""
        image: Surface | None = None
        if self.__empty_image and self.__obstacle_image:
            image = self.__obstacle_image.copy() if feature.type == Entities.OBSTACLE else self.__empty_image.copy()

        if image is not None:
            x = feature.center[0] - image.get_width() / 2
            y = feature.center[1] - image.get_height() / 2
            if feature.type == Entities.BASE or feature.type == Entities.SPAWN:
                color_image = pygame.Surface(image.get_size())
                color_image.fill(feature.color)
                image.blit(color_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            screen.blit(image, (x, y))
        else:
            pygame.draw.polygon(screen, feature.color, feature.corners)

        is_bonus = False
        # check if there is a bonus on hex:
        match feature.type:
            case Entities.CATAPULT:
                image = self.__catapult_image
                is_bonus = True
            case Entities.LIGHT_REPAIR:
                image = self.__light_repair_image
                is_bonus = True
            case Entities.HARD_REPAIR:
                image = self.__hard_repair_image
                is_bonus = True

        if is_bonus:
            x = feature.center[0] - image.get_width() / 2
            y = feature.center[1] - image.get_height() / 2
            if is_tank_there:
                image = pygame.transform.scale(image, (HEX_RADIUS_X[0] / 2, HEX_RADIUS_Y[0] / 2))
            screen.blit(image, (x, y))

        pygame.draw.aalines(screen, self.__aaline_color, closed=True, points=feature.corners)

    def draw_legend(self, screen, font) -> None:
        y = 0
        for feature in self.__map_legend_items:
            text = font.render(' ' + str(feature.type), True, WHITE)
            text_rect = text.get_rect(midleft=(feature.center[0] + HEX_RADIUS_X[0], feature.center[1]))
            screen.blit(text, text_rect)
            y += 2 * HEX_RADIUS_Y[0]
            self.draw(screen, feature, False)
