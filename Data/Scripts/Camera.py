import pygame

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

class Camera:
    def __init__(self, width, height):
        self.camera_rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        # Offset the entity's position based on the camera's position
        return entity.move(self.camera_rect.topleft)

    def update(self, player, map_width, map_height):
        # Center the camera on the player
        x = -player.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -player.rect.centery + int(SCREEN_HEIGHT / 2)

        # Limit scrolling to map boundaries
        x = max(-(map_width - SCREEN_WIDTH), min(0, x))
        y = max(-(map_height - SCREEN_HEIGHT), min(0, y))

        self.camera_rect = pygame.Rect(x, y, self.width, self.height)
