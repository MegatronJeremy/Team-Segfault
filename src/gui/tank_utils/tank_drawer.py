import pygame

from src.game_map.hex import Hex
from src.parameters import HEX_RADIUS_Y, HEX_RADIUS_X, ANIMATION_SPEED_MULTIPLIER

# Define the text outline thickness
outline_thickness = 2


# Function to render text with outline
def render_text_with_outline(font, text, color, outline_color):
    # Render the outline text by drawing the text multiple times offset by the outline thickness
    outline_surface = pygame.Surface(
        (font.size(text)[0] + outline_thickness * 2, font.size(text)[1] + outline_thickness * 2), pygame.SRCALPHA)
    outline_font = font
    for dx in range(-outline_thickness, outline_thickness + 1):
        for dy in range(-outline_thickness, outline_thickness + 1):
            if dx ** 2 + dy ** 2 <= outline_thickness ** 2:
                outline_surface.blit(outline_font.render(text, True, outline_color),
                                     (outline_thickness + dx, outline_thickness + dy))

    # Render the main text on top of the outline
    text_surface = font.render(text, True, color)

    # Create a new surface and blit the outline and text on it
    surface = pygame.Surface((outline_surface.get_width(), outline_surface.get_height()), pygame.SRCALPHA)
    surface.blit(outline_surface, (0, 0))
    surface.blit(text_surface, (outline_thickness, outline_thickness))

    return surface


class TankDrawer(pygame.sprite.Sprite):
    # timers representing how long will tank on previous position be visible
    __timer = 30

    def __init__(self, tank):
        pygame.sprite.Sprite.__init__(self)
        self.__tank = tank
        # load image
        self.image = pygame.image.load(tank.image_path)
        self.image = pygame.transform.scale(self.image, (HEX_RADIUS_X[0] * 1.5, HEX_RADIUS_Y[0] * 1.5))
        # color sprite image
        color_image = pygame.Surface(self.image.get_size())
        color_image.fill(tank.color)
        self.image.blit(color_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.rect = self.image.get_rect()
        self.rect.center = Hex.make_center(tank.coord)

        # used for translucent sprite drawing
        self.__transparent_image = None
        self.__last_position = None
        self.__counter = -1
        # used for changing alpha value; alpha is in range [1, 255]
        self.__step = 255 / TankDrawer.__timer

    def update(self, screen) -> None:
        # self.rect.center = Hex.make_center(self.__tank.get_coord())
        new_pos = Hex.make_center(self.__tank.coord)
        if self.rect.center != new_pos:
            self.__counter = TankDrawer.__timer * \
                             (0.2 * ANIMATION_SPEED_MULTIPLIER[0] + 0.8) if self.__tank.was_destroyed \
                else TankDrawer.__timer
            # coordinates need to be translated so that image is drawn from center (blit only has topleft drawing)
            self.__last_position = (self.rect.center[0] - self.image.get_width() / 2,
                                    self.rect.center[1] - self.image.get_height() / 2)
            self.__transparent_image = self.image.copy()
            self.rect.center = new_pos

        # display hp if tank has any
        if self.__tank.health_points == 0:
            return
        font_size = round(min(HEX_RADIUS_Y[0], HEX_RADIUS_X[0]))
        font = pygame.font.SysFont('arial', font_size, bold=True)
        text = render_text_with_outline(font, f'{self.__tank.health_points}', 'white', 'black')
        text_rect = text.get_rect(bottomleft=(Hex.make_center(self.__tank.coord)[0] + HEX_RADIUS_X[0] / 2,
                                              Hex.make_center(self.__tank.coord)[1] + HEX_RADIUS_Y[0] / 2))
        screen.blit(text, text_rect)

        # display last position
        if self.__counter >= 0:
            self.__transparent_image.set_alpha(round(self.__counter * self.__step))
            screen.blit(self.__transparent_image, self.__last_position)
            self.__counter -= 1
