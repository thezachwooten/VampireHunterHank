import pygame
import os

class Background:
    # constructor
    def __init__(self, bgtype, screen, screen_width, screen_height):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scroll = 0
        self.bgtype = bgtype

        if self.bgtype == 'Forest':
            # Initialize the background image list
            self.bg_images = []

            # Load background images and scale them [Forest]
            for layer in ['back', 'middle', 'front']:
                image_path = os.path.join("Data", "Images", "Backgrounds", self.bgtype, f"{layer}.png")
                image = pygame.image.load(image_path).convert_alpha()

                # Optionally scale the images to fit the screen dimensions
                scaled_image = pygame.transform.scale(image, (self.screen_width, self.screen_height))
                self.bg_images.append(scaled_image)

            # Set the width of the background based on one of the images (assuming all have the same width)
            self.bg_width = self.bg_images[0].get_width()

    def draw_bg(self):
        # for Castle
        for x in range(15):
            speed = 1
            self.screen.blit(self.bg_images[0], (x * self.bg_width - self.scroll * speed, 0))
            speed += 0.1
            self.screen.blit(self.bg_images[1], (x * self.bg_width - self.scroll * speed, 0))
            speed += 0.1
            self.screen.blit(self.bg_images[2], (x * self.bg_width - self.scroll * speed, 0))
            speed += 0.1

    def update_scroll(self, direction):
        """ Updates the scroll based on the player's movement direction """
        if direction == 'left' and self.scroll > 0:
            self.scroll -= 2
        elif direction == 'right' and self.scroll < 3000:
            self.scroll += 2

