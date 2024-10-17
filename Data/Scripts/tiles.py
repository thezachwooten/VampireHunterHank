import pygame, csv, os
from pygame.sprite import _Group

class tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y, spritesheet):
        pygame.sprite.Sprite.__init__(self)
        self.image = spritesheet.parse_image()

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def draw(self, surf):
        surf.blit(self.image, (self.rect.x, self.rect.y))

class Tilemap:
    def __init__(self, tile_size, filename, spritesheet):
        self.tile_size = tile_size
        self.start_x, self.start_y = 0,0
        self.spritesheet = spritesheet