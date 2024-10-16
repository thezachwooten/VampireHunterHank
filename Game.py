import pygame
import sys
from Data.Scripts.Background import * # import code for parallax effect

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480



class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Vampire Hunter Hank')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.clock = pygame.time.Clock()

        # Initialize the background
        self.background = Background('Castle', self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)
    

    def run(self):
        # Main Game Loop
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Draw the background and ground
            self.background.draw_bg()
            self.background.draw_ground()

            # Scroll control based on player input
            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT]:
                self.background.update_scroll('left')
            if key[pygame.K_RIGHT]:
                self.background.update_scroll('right')

            # update 
            pygame.display.update()
            self.clock.tick(60)

Game().run()