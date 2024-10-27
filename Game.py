import pygame
import sys

from Data.Scripts.utils import * # import util scripts
from Data.Scripts.Background import * # import code for parallax effect
from Data.Scripts.tiles import Tilemap # import tilemap code
from Data.Scripts import Player # import player class
from Data.Scripts import Ghoul # import ghoul class
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

        

        self.levels = ['Forest', 'Cemetery', 'Castle']

        self.curLevel = 0

        self.tile_map = Tilemap("Data/Images/Tilesets/" + self.levels[self.curLevel] + "/NewTest.tmx") # test file 

        # initialize camera
        self.camera = Camera.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.map_width, self.map_height = self.tile_map.get_map_size()

        # Initialize the background
        self.background = Background(self.levels[0], self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Initialize player
        self.player = Player.Player(self)
        self.ghoul = Ghoul.Ghoul(self)

        self.ground_tiles = self.tile_map.get_tile_objects_with_masks(layer_name="Ground", property_name="collision")  # Get the tiles with rects and masks
        self.painting_tiles = self.tile_map.get_tile_objects_with_masks(layer_name="Paintings", property_name="collision")  # Get the tiles with rects and masks
        self.playerSpawner = self.tile_map.get_tile_objects_with_masks(layer_name="Spawners", property_name="player")  # Get the tiles with rects and masks
        self.skeletonSpawner = self.tile_map.get_tile_objects_with_masks(layer_name="Spawners", property_name="skeleton")  # Get the tiles with rects and masks

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
            # Draw tilemap and player with camera offset
            self.player.update(self.dt, self.ground_tiles, self.painting_tiles)
            self.player.draw(self.screen, self.camera)
            self.ghoul.draw(self.screen, self.camera)
            # Update camera position based on the player
            self.camera.update(self.player, self.map_width, self.map_height)
            # Draw Map
            self.tile_map.draw(self.screen, self.camera, self.ground_tiles)
            self.tile_map.draw(self.screen, self.camera, self.painting_tiles)

            pygame.display.update()
            self.clock.tick(60)

Game().run()