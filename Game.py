import pygame
import sys

from Data.Scripts.utils import * # import util scripts
from Data.Scripts.Background import * # import code for parallax effect
from Data.Scripts.tiles import Tilemap # import tilemap code
from Data.Scripts import Player # import player class

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
TARGET_FPS = 60



class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Vampire Hunter Hank')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    

        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        

        self.levels = ['Castle', 'Forest', 'Cemetery']

        self.tile_map = Tilemap("Data/Images/Tilesets/Graveyard/NewTest.tmx") # test file 

        # Initialize the background
        self.background = Background(self.levels[1], self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Initialize player
        self.player = Player.Player(self)
    

    def run(self):
        # Main Game Loop
        while True:
            
            self.dt = self.clock.tick(60) * 0.001 * TARGET_FPS
           


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
            # Handle player input inside the Player class
            self.player.handle_input()

            # Scroll control based on player input
            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT]:
                self.background.update_scroll('left')
            if key[pygame.K_RIGHT]:
                self.background.update_scroll('right')


            # Draw the background and ground
            self.background.draw_bg()

            # Draw the tilemap
            self.tile_map.draw(self.screen)

            # Handle player movement
            # tile_rects = self.tile_map.get_tile_rects()  # Get tile rectangles for tiles that have collision
            tile_sprites = self.tile_map.get_tile_objects_with_masks()  # Get the tiles with rects and masks
            self.player.update(self.dt, tile_sprites)  # Update the player with masked tiles
            self.player.draw(self.screen) # draw player to screen


            pygame.display.update()
            self.clock.tick(60)

Game().run()