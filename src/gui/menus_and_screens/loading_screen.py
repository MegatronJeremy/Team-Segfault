import pygame
from pygame import Surface

from src.parameters import TRACKS_SCALE, TRACKS_IMAGE_PATH, LOADING_ANIMATION_LIMIT, SCREEN_WIDTH, SCREEN_HEIGHT, \
    LOADING_BAR_BACKGROUND_COLOR, TANK_ICON_PATH


class LoadingScreen:
    def __init__(self):
        self.__tracks_image = pygame.transform.scale(pygame.image.load(TRACKS_IMAGE_PATH), TRACKS_SCALE)
        self.__max_width: int = self.__tracks_image.get_width()
        self.__height: int = self.__tracks_image.get_height()
        # x, y coordinates that represent top left corner of a 'full' loading bar
        self.__x: int = (SCREEN_WIDTH - self.__max_width) // 2
        self.__y: int = (SCREEN_HEIGHT - self.__height) // 2
        self.__loading_counter: int = LOADING_ANIMATION_LIMIT
        self.__step: int = self.__max_width // LOADING_ANIMATION_LIMIT
        self.__tank_image: Surface = pygame.transform.scale(
            pygame.transform.flip(pygame.image.load(TANK_ICON_PATH), flip_x=True, flip_y=False),
            (TRACKS_SCALE[1], TRACKS_SCALE[1]))

    def draw(self, screen: Surface) -> None:
        screen.blit(self.__tracks_image, (self.__x, self.__y))
        new_x = self.__x + self.__step * (LOADING_ANIMATION_LIMIT - self.__loading_counter)
        pygame.draw.rect(screen, LOADING_BAR_BACKGROUND_COLOR,
                         (new_x, self.__y, self.__max_width - new_x + self.__x, self.__height))
        screen.blit(self.__tank_image, (new_x, self.__y))

        if self.__loading_counter > 0:
            self.__loading_counter -= 1

    def reset(self) -> None:
        self.__loading_counter = LOADING_ANIMATION_LIMIT
