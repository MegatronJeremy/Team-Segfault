import textwrap

import pygame

from src.parameters import ARCHIVED_GAME_SPEED, MENU_FONT, WHITE


class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, caption=None,
                 bound_parameter=ARCHIVED_GAME_SPEED, caption_position='above', reverse_value=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.grabbed = False
        self.handle_height = 10
        self.handle_rect = pygame.Rect(x, y, width, self.handle_height)
        self.caption = caption
        self.bound_parameter = bound_parameter
        self.caption_position = caption_position  # 'above' or 'below'
        self.reverse_value = reverse_value  # True if increasing slider decreases the value
        self.font = pygame.font.Font(MENU_FONT, 18)  # Font for the caption
        self.caption_lines = []

        self.update_handle_position()
        self.update_caption_lines()

    def update_caption_lines(self):
        if self.caption:
            # Wrap the caption text into lines that fit within the width of the slider
            wrapped_text = textwrap.wrap(self.caption,
                                         width=int(self.rect.width // 2))  # Adjust width factor as needed
            self.caption_lines = wrapped_text

    def draw(self, screen):
        # Draw the slider track
        pygame.draw.rect(screen, (180, 180, 180), self.rect)

        # Draw the handle
        self.update_handle_position()
        pygame.draw.rect(screen, (100, 100, 250), self.handle_rect)

        # Draw the caption
        if self.caption_lines:
            caption_height = len(self.caption_lines) * (self.font.get_height() + 5)  # Height for all lines with padding
            base_y = self.rect.y - caption_height // 2 - 15 if self.caption_position == 'above' else self.rect.bottom + 10

            for i, line in enumerate(self.caption_lines):
                caption_surface = self.font.render(line, True, WHITE)
                caption_rect = caption_surface.get_rect(
                    center=(self.rect.centerx, base_y + i * (self.font.get_height() + 5)))
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

                # Adjust bound_parameter based on reverse_value flag
                if self.reverse_value:
                    self.bound_parameter[0] = (self.max_val + self.min_val) - self.val
                else:
                    self.bound_parameter[0] = self.val

    def get_value(self):
        return self.val
