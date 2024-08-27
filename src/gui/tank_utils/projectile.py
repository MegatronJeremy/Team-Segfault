import pygame
from pygame import Surface

from src.parameters import BULLET_IMAGE_PATH, BULLET_SOUND, BULLET_VECTOR, SOUND_VOLUME, HEX_RADIUS_X, HEX_RADIUS_Y, \
    BULLET_TRAVEL_TIME, ANIMATION_SPEED_MULTIPLIER


class Projectile(pygame.sprite.Sprite):
    __IMAGE: Surface = pygame.image.load(BULLET_IMAGE_PATH)

    def __init__(self, start_pos: tuple[int, int], end_pos: tuple[int, int], color: tuple[int, int, int] | str):
        super().__init__()

        self.shot_vector = (end_pos[0] - start_pos[0], end_pos[1] - start_pos[1])
        self.start_pos = start_pos

        self.image = Projectile.__IMAGE
        # rotate bullet so it is pointing to end_pos
        angle = pygame.Vector2(BULLET_VECTOR).angle_to(pygame.Vector2(self.shot_vector))
        angle = -angle
        self.image = pygame.transform.scale(self.image, (HEX_RADIUS_X[0], HEX_RADIUS_Y[0]))
        self.image = pygame.transform.rotate(self.image, angle)

        # color the bullet
        color_image = pygame.Surface(self.image.get_size())
        color_image.fill(color)
        self.image.blit(color_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.rect = self.image.get_rect()
        self.rect.center = start_pos

        # animation variables
        self.counter: float = 0

        # sound
        self.__sound = pygame.mixer.Sound(BULLET_SOUND)
        self.__sound.set_volume(SOUND_VOLUME[0])
        self.__sound_played = False

    def update(self) -> None:
        if self.__sound_played is False:
            self.__sound.play()
            self.__sound_played = True
        self.counter += 1.0 / (BULLET_TRAVEL_TIME * ANIMATION_SPEED_MULTIPLIER[0])

        if self.counter >= 1:
            self.kill()

        x, y = self.start_pos
        self.rect.center = (round(x + self.counter * self.shot_vector[0]),
                            round(y + self.counter * self.shot_vector[1]))
