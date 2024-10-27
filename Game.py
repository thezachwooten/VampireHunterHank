import pygame
import sys

from Data.Scripts.utils import * # import util scripts
from Data.Scripts.Background import * # import code for parallax effect
from Data.Scripts.tiles import Tilemap # import tilemap code
from Data.Scripts import Player # import player class
from Data.Scripts import Camera # import camera class

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

        # initialize camera
        self.camera = Camera.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.map_width, self.map_height = self.tile_map.get_map_size()

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

            # Handle player movement
            # tile_rects = self.tile_map.get_tile_rects()  # Get tile rectangles for tiles that have collision
            ground_tiles = self.tile_map.get_tile_objects_with_masks(layer_name="Ground", property_name="collision")  # Get the tiles with rects and masks
            painting_tiles = self.tile_map.get_tile_objects_with_masks(layer_name="Paintings", property_name="collision")  # Get the tiles with rects and masks
            # Draw tilemap and player with camera offset
            self.player.update(self.dt, ground_tiles)
            self.player.draw(self.screen, self.camera)
            # Update camera position based on the player
            self.camera.update(self.player, self.map_width, self.map_height)
            # Draw Map
            self.tile_map.draw(self.screen, self.camera, ground_tiles)
            self.tile_map.draw(self.screen, self.camera, painting_tiles)

            pygame.display.update()
            self.clock.tick(60)

Game().run()