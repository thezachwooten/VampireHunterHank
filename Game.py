import pygame
import sys

from Data.Scripts.utils import * # import util scripts
from Data.Scripts.Background import * # import code for parallax effect
from Data.Scripts.Entities import PhysicsEntity # import code for PhysicsEntity

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480



class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Vampire Hunter Hank')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.display = pygame.Surface((SCREEN_WIDTH/2, SCREEN_HEIGHT/2))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        self.assets = {
            'player' : load_image('Player/Sprites/Converted_Vampire/Hurt.png') # temp sprite for character
        }

        # Initialize the background
        self.background = Background('Castle', self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Initialize player
        self.player = PhysicsEntity(self, 'player', (50,200), (8,15))
    

    def run(self):
        # Main Game Loop
        while True:
            
           


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

            # Scroll control based on player input
            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT]:
                self.background.update_scroll('left')
            if key[pygame.K_RIGHT]:
                self.background.update_scroll('right')


            # Draw the background and ground
            self.background.draw_bg()
            self.background.draw_ground()

            # Handle player movement
            self.player.update((self.movement[1] - self.movement[0], 0))
            self.player.render(self.screen)


            pygame.display.update()
            self.clock.tick(60)

Game().run()