import pygame
import sys

from enum import Enum # import Enums

from Data.Scripts.utils import * # import util scripts
from Data.Scripts.Background import * # import code for parallax effect
from Data.Scripts.tiles import Tilemap # import tilemap code
from Data.Scripts import Player # import player class
from Data.Scripts import Ghoul # import ghoul class
from Data.Scripts import Skeleton # import skeleton class
from Data.Scripts import Vampire # import Vampire class
from Data.Scripts import Camera # import camera class
from Data.Scripts import Projectile # import projectile class

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
TARGET_FPS = 60
MUSIC_PATH = "./Data/Music/" # path for music

class GameState(Enum):
    PLAYING = 1
    GAME_OVER = 2
    NEXT_LEVEL = 3

class Game:
    # Game Constructor
    def __init__(self):
        pygame.init() # Initialize pygame
        pygame.mixer.init() # Initialize audio mixer

        pygame.display.set_caption('Vampire Hunter Hank')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    

        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        self.state = GameState.PLAYING # Start in playing mode

        self.levels = ['Forest', 'Cemetary', 'Castle']

        self.curLevel = 2 # 0-2; 3 total level choices

        # initialize level
        self.load_level() # this defaults to 'Forest' as curLevel is initialized to 0

        # initialize projectiles
        self.projectiles = pygame.sprite.Group()

    # method to load level data based on curLevel parameter
    def load_level(self):
        # Load tile map for current level
        self.tile_map = Tilemap("./Data/Images/Tilesets/" + self.levels[self.curLevel] + "/NewTest.tmx") # test file 

        # Load background music for current level
        self.cur_track = MUSIC_PATH + self.levels[self.curLevel] + ".ogg" # ./Data/Music/{curLevel}.ogg
        pygame.mixer.music.load(self.cur_track)  # Replace with your file path
        pygame.mixer.music.set_volume(0.15)  # Set volume (15%)
        pygame.mixer.music.play(-1)  # Loop indefinitely

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
        self.vampireSpawner = self.tile_map.get_tile_objects_with_masks(layer_name="Spawners", property_name="vampire") # Get vampire spawner tiles
        self.portal_tiles = self.tile_map.get_tile_objects_with_masks(layer_name="Portals", property_name="collision") # Get portal tiles on map

        player_start_pos = next(iter(self.playerSpawner))  # Get the first (and only) sprite
        start_x, start_y = player_start_pos.rect.x, player_start_pos.rect.y  # Access position
        # Initialize player
        self.player = Player.Player(self,(start_x,start_y))
        self.playerSG = pygame.sprite.Group()
        self.playerSG.add(self.player)
        # enemy sprite group
        self.enemies = pygame.sprite.Group()  # Unified enemy sprite group
        # loop ghoul spawner
        for ghoulspawn in self.ghouldSpawner:
            start_x, start_y = ghoulspawn.rect.x, ghoulspawn.rect.y  # Access position
            ghoul = Ghoul.Ghoul(self, (start_x,start_y))
            self.enemies.add(ghoul)
        # skeleton
        for skeletonSpawn in self.skeletonSpawner:
            start_x, start_y = skeletonSpawn.rect.x, skeletonSpawn.rect.y # Access position
            skeleton = Skeleton.Skeleton(self, (start_x,start_y))
            self.enemies.add(skeleton)
        # Vampire
        for vampireSpawn in self.vampireSpawner:
            start_x, start_y = vampireSpawn.rect.x, vampireSpawn.rect.y # Access position
            vamp = Vampire.Vampire(self, (start_x,start_y))
            self.enemies.add(vamp)

        

    

    # method to check if game is over
    def checkGameOver(self):
        if self.player.health <= 0:
            # Change game state to GAME_OVER
            self.state = GameState.GAME_OVER
    # method to switch to next level
    def nextLevel(self):
        # Switch to next level or print gameover if final level reached
        if self.curLevel < len(self.levels) - 1:
            self.curLevel += 1
            self.load_level()
        else:
            print("Congratulations! You've completed all levels. Maybe I'll add a fancy screen for this")
            self.state = GameState.GAME_OVER
    
    # Main Game method
    def run(self):
        # Main Game Loop
        while True:
            
            self.dt = self.clock.tick(60) * 0.001 * TARGET_FPS
           


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and self.state == GameState.GAME_OVER: # Return-key pressed during GAME_OVER
                        # Restart the game on curLevel
                        self.state = GameState.PLAYING # changes game state
                        self.load_level() # reload level 

            # Game State Logic
            if self.state == GameState.PLAYING: # Game is being played
                # update game and check game over
                self.checkGameOver()
                self.update_gameplay()
            elif self.state == GameState.GAME_OVER: # Game is over
                # draw game over
                self.display_game_over()
            

            pygame.display.update()
            self.clock.tick(60)

    def update_gameplay(self):
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
        self.player.update(self.dt, self.ground_tiles, self.painting_tiles, self.portal_tiles, self.enemies, self.camera)
        self.tile_map.draw(self.screen, self.camera, self.portal_tiles) # draw portals (DO IT HERE TO BE BEHIND PLAYER)
        self.player.draw(self.screen, self.camera)


        # Update Enemies
        for enemy in self.enemies:
            enemy.update(self.dt, self.player, self.ground_tiles, self.camera, self.playerSG) # update enemy
            enemy.draw(self.screen, self.camera)
        # Update Camera
        self.camera.update(self.player, self.map_width, self.map_height)
        # Draw Map
        self.tile_map.draw(self.screen, self.camera, self.ground_tiles) # draw ground tiles
        self.tile_map.draw(self.screen, self.camera, self.painting_tiles) # draw paintings
        

    def display_game_over(self):
        # displays game over screen
        self.screen.fill((0,0,0))
        font = pygame.font.Font("./Data/Fonts/gothic.ttf", 74)
        text = font.render("Game Over", True, (255, 0 , 0))
        text_rect = text.get_rect(center=(SCREEN_HEIGHT // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()

Game().run()