import pygame

from src.parameters import ARCHIVED_GAME_SPEED, MENU_FONT, WHITE


class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, caption=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.grabbed = False
        self.handle_height = 10
        self.handle_rect = pygame.Rect(x, y, width, self.handle_height)
        self.caption = caption
        self.font = pygame.font.Font(MENU_FONT, 24)  # Font for the caption

        self.update_handle_position()

    def draw(self, screen):
        # Draw the slider track
        pygame.draw.rect(screen, (180, 180, 180), self.rect)

        # Draw the handle
        self.update_handle_position()
        pygame.draw.rect(screen, (100, 100, 250), self.handle_rect)

        # Draw the caption
        if self.caption:
            caption_surface = self.font.render(self.caption, True, WHITE)
            caption_rect = caption_surface.get_rect(center=(self.rect.centerx, self.rect.y - 20))
            screen.blit(caption_surface, caption_rect)

    def update_handle_position(self):
        # Calculate the position of the handle based on the current value
        proportion = (self.val - self.min_val) / (self.max_val - self.min_val)
        self.handle_rect.y = self.rect.y + (1 - proportion) * (self.rect.height - self.handle_height)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.grabbed = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.grabbed = False

        elif event.type == pygame.MOUSEMOTION:
            if self.grabbed:
                new_y = event.pos[1]
                new_y = max(self.rect.y, min(new_y, self.rect.y + self.rect.height - self.handle_height))
                proportion = 1 - (new_y - self.rect.y) / (self.rect.height - self.handle_height)
                self.val = self.min_val + proportion * (self.max_val - self.min_val)
                ARCHIVED_GAME_SPEED[0] = self.val

    def get_value(self):
        return self.val
