import pygame

from src.parameters import EXPLOSION_IMAGES, EXPLOSION_SOUND, HEX_RADIUS_X, HEX_RADIUS_Y, \
    EXPLOSION_IMAGE_SCALE, EXPLOSION_SPEED, ANIMATION_SPEED_MULTIPLIER
from src.settings_utils import get_sound_volume


class Explosion(pygame.sprite.Sprite):
    __IMAGES = [pygame.image.load(path) for path in EXPLOSION_IMAGES]

    def __init__(self, coord: tuple[int, int], shot_ended: list[bool]):
        super().__init__()

        # image index
        self.index = 0
        # animation counter
        self.counter = 0
        self.image = Explosion.__IMAGES[-1]
        self.rect = self.image.get_rect()
        self.rect.center = (coord[0], coord[1])

        # used for delaying explosion_images if the bullet is too slow
        self.__shot_ended = shot_ended

        self.__sound = pygame.mixer.Sound(EXPLOSION_SOUND)
        self.__sound.set_volume(get_sound_volume())
        self.__sound_played = False

    def update(self) -> None:
        if not self.__shot_ended[0]:
            return

        if self.__sound_played is False:
            self.__sound.play()
            self.__sound_played = True

        self.counter += 1

        if self.counter >= EXPLOSION_SPEED * ANIMATION_SPEED_MULTIPLIER[0] and self.index < len(Explosion.__IMAGES) - 1:
            self.counter = 0
            self.index += 1
            self.image = Explosion.__IMAGES[self.index]

        if self.index >= len(Explosion.__IMAGES) - 1 and self.counter >= EXPLOSION_SPEED * ANIMATION_SPEED_MULTIPLIER[
            0]:
            self.kill()

    @staticmethod
    def set_image_scale() -> None:
        for i in range(len(Explosion.__IMAGES)):
            Explosion.__IMAGES[i] = pygame.transform.scale(Explosion.__IMAGES[i],
                                                           (HEX_RADIUS_X[0] * EXPLOSION_IMAGE_SCALE,
                                                            HEX_RADIUS_Y[0] * EXPLOSION_IMAGE_SCALE)
                                                           )
