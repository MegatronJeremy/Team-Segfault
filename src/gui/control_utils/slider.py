import pygame


class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.grabbed = False
        self.handle_width = 10
        self.handle_rect = pygame.Rect(x, y, self.handle_width, height)

    def draw(self, screen):
        # Draw the slider track
        pygame.draw.rect(screen, (180, 180, 180), self.rect)

        # Draw the handle
        self.handle_rect.x = self.get_handle_position()
        pygame.draw.rect(screen, (100, 100, 250), self.handle_rect)

    def get_handle_position(self):
        # Calculate the position of the handle based on the current value
        proportion = (self.val - self.min_val) / (self.max_val - self.min_val)
        return self.rect.x + proportion * (self.rect.width - self.handle_width)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.grabbed = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.grabbed = False

        elif event.type == pygame.MOUSEMOTION:
            if self.grabbed:
                new_x = event.pos[0]
                new_x = max(self.rect.x, min(new_x, self.rect.x + self.rect.width - self.handle_width))
                proportion = (new_x - self.rect.x) / (self.rect.width - self.handle_width)
                self.val = self.min_val + proportion * (self.max_val - self.min_val)

    def get_value(self):
        return self.val
