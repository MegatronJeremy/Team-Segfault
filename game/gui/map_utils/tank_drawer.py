import pygame

from map.hex import Hex


class TankDrawer(pygame.sprite.Sprite):
    # timers representing how long will tank on previous position be visible
    __timer = 30

    def __init__(self, tank):
        pygame.sprite.Sprite.__init__(self)
        self.__tank = tank
        # load image
        self.image = pygame.image.load(tank.get_image_path())
        self.image = pygame.transform.scale(self.image, (Hex.radius_x * 1.5, Hex.radius_y * 1.5))
        # color sprite image
        color_image = pygame.Surface(self.image.get_size())
        color_image.fill(tank.get_color())
        self.image.blit(color_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.rect = self.image.get_rect()
        self.rect.center = Hex.make_center(tank.get_coord())

        # used for translucent sprite drawing
        self.__transparent_image = None
        self.__last_position = None
        self.__counter = -1
        # used for changing alpha value; alpha is in range [1, 255]
        self.__step = 255 / TankDrawer.__timer

    def update(self, screen) -> None:
        # self.rect.center = Hex.make_center(self.__tank.get_coord())
        new_pos = Hex.make_center(self.__tank.get_coord())
        if self.rect.center != new_pos:
            self.__counter = TankDrawer.__timer
            # coordinates need to be translated so that image is drawn from center (blit only has topleft drawing)
            self.__last_position = (self.rect.center[0] - self.image.get_width() / 2,
                                    self.rect.center[1] - self.image.get_height() / 2)
            self.__transparent_image = self.image.copy()
            self.rect.center = new_pos

        # display hp if tank has any
        if self.__tank.get_hp() == 0:
            return
        font_size = round(min(Hex.radius_y, Hex.radius_x))
        font = pygame.font.SysFont('arial', font_size, bold=True)
        text = font.render(str(self.__tank.get_hp()), True, 'white')
        text_rect = text.get_rect(bottomleft=(Hex.make_center(self.__tank.get_coord())[0] + Hex.radius_x / 2,
                                              Hex.make_center(self.__tank.get_coord())[1] + Hex.radius_y / 2))
        screen.blit(text, text_rect)

        # display last position
        if self.__counter >= 0:
            self.__transparent_image.set_alpha(round(self.__counter * self.__step))
            screen.blit(self.__transparent_image, self.__last_position)
            self.__counter -= 1
