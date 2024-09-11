import pygame

from src.parameters import HEX_RADIUS_Y, HEX_RADIUS_X, TANK_PULSE_FULL_DURATION, TANK_IMAGE_SCALE, \
    TANK_SHADOW_MAX_SCALE, SHOT_TANK_OUTLINE_COLOR


class ShotTank(pygame.sprite.Sprite):
    """Class representing a shadow of a tank that has been shot, but not destroyed"""

    def __init__(self, coord: tuple[int, int], image_path: str,
                 color: str | tuple[int, int, int] = SHOT_TANK_OUTLINE_COLOR,
                 shot_ended: list[bool] | None = None):
        super().__init__()

        self.__shot_ended = shot_ended

        # image index
        self.index = 0
        # animation counter
        self.counter = 0
        self.color = color
        self.coord = coord
        self.base_image = pygame.image.load(image_path)
        self.scale = (HEX_RADIUS_X[0] * TANK_IMAGE_SCALE, HEX_RADIUS_Y[0] * TANK_IMAGE_SCALE)
        # color tank image
        self.image = pygame.transform.scale(pygame.image.load(image_path), self.scale)
        color_image = pygame.Surface(self.image.get_size())
        color_image.fill(color)
        self.image.blit(color_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        difference = TANK_SHADOW_MAX_SCALE - TANK_IMAGE_SCALE
        half_duration = TANK_PULSE_FULL_DURATION / 2
        self.scale_step: tuple[float, float] = (difference * HEX_RADIUS_X[0] / half_duration,
                                                difference * HEX_RADIUS_Y[0] / half_duration)

        self.rect = self.image.get_rect()
        self.rect.center = (coord[0], coord[1])

    def update(self) -> None:
        if self.__shot_ended and not self.__shot_ended[0]:
            return

        self.counter += 1
        sign: float = 1.0
        if self.counter > TANK_PULSE_FULL_DURATION / 2:
            sign = -1.0
        self.scale = (self.scale[0] + sign * self.scale_step[0], self.scale[1] + sign * self.scale_step[1])

        # this could be optimized if necessary
        self.image = pygame.transform.scale(self.base_image, self.scale)
        color_image = pygame.Surface(self.image.get_size())
        color_image.fill(self.color)
        self.image.blit(color_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.rect = self.image.get_rect()
        self.rect.center = self.coord

        if self.counter >= TANK_PULSE_FULL_DURATION:
            self.kill()
