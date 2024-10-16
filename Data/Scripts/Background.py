import pygame
import os

class Background:
    # constructor
    def __init__(self, screen, screen_width, screen_height):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scroll = 0

        # Load ground image and scale it
        self.ground_image = pygame.image.load(os.path.join("Data", "Images", "Backgrounds", "PNG", "Castle", "Bright", "ground.png")).convert_alpha()
        self.ground_image = pygame.transform.scale(self.ground_image, (screen_width, int(screen_height * 0.5)))
        self.ground_width = self.ground_image.get_width()
        self.ground_height = self.ground_image.get_height()

        # Load background images and scale them
        self.bg_images = []
        for i in range(0, 6):
            bg_image = pygame.image.load(os.path.join("Data", "Images", "Backgrounds", "PNG", "Castle", "Bright", f"{i}.png")).convert_alpha()
            bg_image = pygame.transform.scale(bg_image, (screen_width, screen_height))
            self.bg_images.append(bg_image)
        self.bg_width = self.bg_images[0].get_width()

    def draw_bg(self):
        for x in range(7):
            speed = 1
            self.screen.blit(self.bg_images[0], (x * self.bg_width - self.scroll * speed, 0))
            self.screen.blit(self.bg_images[1], (x * self.bg_width - self.scroll * speed, 0))
            speed += 0.2
            self.screen.blit(self.bg_images[2], (x * self.bg_width - self.scroll * speed, 0))
            self.screen.blit(self.bg_images[3], (x * self.bg_width - self.scroll * speed, 0))
            speed += 0.2
            self.screen.blit(self.bg_images[4], (x * self.bg_width - self.scroll * speed, 0))
            self.screen.blit(self.bg_images[5], (x * self.bg_width - self.scroll * speed, 0))
            speed += 0.2

    def draw_ground(self):
        for x in range(10):
            self.screen.blit(self.ground_image, (x * self.ground_width - 2 - self.scroll * 2.2, self.screen_height - self.ground_height))

    def update_scroll(self, direction):
        """ Updates the scroll based on the player's movement direction """
        if direction == 'left' and self.scroll > 0:
            self.scroll -= 5
        elif direction == 'right' and self.scroll < 3000:
            self.scroll += 5

