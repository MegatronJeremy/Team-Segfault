import pygame

from src.parameters import MENU_FONT


class Button:
    def __init__(self, text, x, y, width, height, inactive_color, active_color, text_color, action=None):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.text_color = text_color
        self.action = action
        self.disabled = False
        self.font = self._get_best_fit_font_size()

    def _get_best_fit_font_size(self):
        min_size = 1
        max_size = 100
        best_size = min_size

        while min_size <= max_size:
            mid_size = (min_size + max_size) // 2
            font = pygame.font.Font(MENU_FONT, mid_size)
            text_surface = font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect()

            if text_rect.width <= self.width and text_rect.height <= self.height:
                best_size = mid_size
                min_size = mid_size + 1
            else:
                max_size = mid_size - 1

        return pygame.font.Font(MENU_FONT, best_size)

    def draw(self, screen):
        color = self.inactive_color if self.disabled else self.active_color
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        font = self.font
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.x + self.width / 2, self.y + self.height / 2))
        screen.blit(text_surface, text_rect)

    def check_click(self, event):
        if self.disabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
                if self.action:
                    self.action()
                return True
        return False
