import pygame
import sys
from Data.Scripts.Background import * # import code for parallax effect
from Data.Scripts.Entities import *

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480



class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Vampire Hunter Hank')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        # Initialize the background
        self.background = Background('Castle', self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Initialize player
        self.player = PhysicsEntitiy(self, 'player', (0,self.background.ground_height), (8,15))
    

    def run(self):
        # Main Game Loop
        while True:
            self.player.update((self.movement[1] - self.movement[0], 0))
           
            # Scroll control based on player input
            key = pygame.key.get_pressed()


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if key[pygame.K_LEFT]:
                        self.background.update_scroll('left')
                    if key[pygame.K_RIGHT]:
                        self.background.update_scroll('right')


            # Draw the background and ground
            self.background.draw_bg()
            self.background.draw_ground()

            
            

            # update 
            pygame.display.update()
            self.clock.tick(60)

Game().run()