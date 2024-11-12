import pygame
import sys

from enum import Enum # import Enums

from Data.Scripts.utils import * # import util scripts
from Data.Scripts.Background import * # import code for parallax effect
from Data.Scripts.tiles import Tilemap # import tilemap code
from Data.Scripts import Player # import player class
from Data.Scripts import Ghoul # import ghoul class
from Data.Scripts import Skeleton # import ghoul class
from Data.Scripts import Camera # import camera class

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
TARGET_FPS = 60

class GameState(Enum):
    PLAYING = 1
    GAME_OVER = 2
    NEXT_LEVEL = 3

class Game:
    # Game Constructor
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Vampire Hunter Hank')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    

        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        self.state = GameState.PLAYING # Start in playing mode

        self.levels = ['Forest', 'Cemetary', 'Castle']

        self.curLevel = 0 # 0-2; 3 total level choices

        # initialize level
        self.load_level() # this defaults to 'Forest' as curLevel is initialized to 0

    # method to load level data based on curLevel parameter
    def load_level(self):
        self.tile_map = Tilemap("Data/Images/Tilesets/" + self.levels[self.curLevel] + "/NewTest.tmx") # test file 

        # initialize camera
        self.camera = Camera.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.map_width, self.map_height = self.tile_map.get_map_size()

        # Initialize the background
        self.background = Background(self.levels[self.curLevel], self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)

        

        self.ground_tiles = self.tile_map.get_tile_objects_with_masks(layer_name="Ground", property_name="collision")  # Get the tiles with rects and masks
        self.painting_tiles = self.tile_map.get_tile_objects_with_masks(layer_name="Paintings", property_name="collision")  # Get the tiles with rects and masks
        self.playerSpawner = self.tile_map.get_tile_objects_with_masks(layer_name="Spawners", property_name="player")  # Get the tiles with rects and masks
        self.ghouldSpawner = self.tile_map.get_tile_objects_with_masks(layer_name="Spawners", property_name="ghoul")  # Get the tiles with rects and masks
        self.skeletonSpawner = self.tile_map.get_tile_objects_with_masks(layer_name="Spawners", property_name="skeleton")  # Get the tiles with rects and masks

        player_start_pos = next(iter(self.playerSpawner))  # Get the first (and only) sprite
        start_x, start_y = player_start_pos.rect.x, player_start_pos.rect.y  # Access position
        # Initialize player
        self.player = Player.Player(self,(start_x,start_y))
        # loop ghoul spawner
        self.ghouls = []
        for ghoulspawn in self.ghouldSpawner:
            start_x, start_y = ghoulspawn.rect.x, ghoulspawn.rect.y  # Access position
            ghoul = Ghoul.Ghoul(self, (start_x,start_y))
            self.ghouls.append(ghoul)
        # skeleton
        self.skeletons = []
        for skeletonSpawn in self.skeletonSpawner:
            start_x, start_y = skeletonSpawn.rect.x, skeletonSpawn.rect.y # Access position
            skeleton = Skeleton.Skeleton(self, (start_x,start_y))
            self.skeletons.append(skeleton)

    

    # method to check if game is over
    def checkGameOver(self):
        if self.player.health <= 0:
            print("Game Over")
    # method to switch to next level
    def nextLevel(self):
        # check if on last level
        if self.curLevel == len(self.levels):
            print("On last level")
        else:
            # increment level
            self.curLevel += 1
            # reset background to curLevel
            self.background = Background(self.levels[0], self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)
            # change map
            self.tile_map = Tilemap("Data/Images/Tilesets/" + self.levels[self.curLevel] + "/NewTest.tmx") # test file 
    
    # Main Game method
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

            self.checkGameOver()

            # Handle player movement
            # Draw tilemap and player with camera offset
            self.player.update(self.dt, self.ground_tiles, self.painting_tiles, self.ghouls)
            self.player.draw(self.screen, self.camera)
            # Update ghouls
            for ghoul in self.ghouls[:]:  # Iterate over a copy of the list
                ghoul.update(self.dt, self.player)
                if ghoul.health <= 0:  # Check if the ghoul is dead
                    ghoul.is_dying = True # set ghould to dying 
                else:
                    ghoul.draw(self.screen, self.camera)  # Draw if alive
            # Update Skeletons
            for skeleton in self.skeletons[:]:
                self.skeleton.update(self.dt)
                if skeleton.health <= 0:
                    skeleton.kill()
                else:
                    self.skeleton.draw(self.screen, self.camera)
            # Update Camera
            self.camera.update(self.player, self.map_width, self.map_height)
            # Draw Map
            self.tile_map.draw(self.screen, self.camera, self.ground_tiles)
            self.tile_map.draw(self.screen, self.camera, self.painting_tiles)

            pygame.display.update()
            self.clock.tick(60)

Game().run()