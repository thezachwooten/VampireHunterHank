import pygame
from Data.Scripts import utils
from Data.Scripts import Animations

class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game

        self.animations = {}

        # Load spritesheets and create animations
        self.animations['idle'] = Animations.Animations(utils.load_spritesheet('Player/Sprites/Converted_Vampire/idle.png', 128, 128, 5), 60)  # 5 frames at 60 fps
        self.animations['walk'] = Animations.Animations(utils.load_spritesheet('Player/Sprites/Converted_Vampire/Walk.png', 128, 128, 8), 60)  # 8 frames at 60 fps
        self.animations['jump'] = Animations.Animations(utils.load_spritesheet('Player/Sprites/Converted_Vampire/Jump.png', 128, 128, 7), 60)  # 7 frames at 60 fps

        self.position, self.velocity = pygame.math.Vector2(0, 0), pygame.math.Vector2(0, 0)
        self.current_animation = self.animations['idle']  # Start with idle animation
        self.image = self.current_animation.get_current_frame()
        self.rect = self.image.get_rect()
        self.hitbox = self.rect.inflate(-55, -40)

        self.rectWidth = 128
        self.rectHeight = 128

        self.LEFT_KEY, self.RIGHT_KEY, self.FACING_LEFT = False, False, False 
        self.is_jumping, self.on_ground = False, False
        self.gravity, self.friction = .35, -.12
        
        self.acceleration = pygame.math.Vector2(0, self.gravity)

        self.health = 100 # Initilize player health to 100

    def draw(self, surf):
        surf.blit(self.image, (self.rect.x, self.rect.y))
        pygame.draw.rect(surf, (255, 0, 0, 100), self.hitbox, 2)  # Red rectangle with transparency


    def update(self, dt, tile_rects):
        # Move
        self.handle_input()
        self.horizontal_movement(dt)
        self.hitbox.center = self.rect.center
        self.hitbox.x = self.position.x + 15 
        self.check_collisionX(tile_rects)
        self.vertical_movement(dt)
        self.hitbox.center = self.rect.center
        self.hitbox.y = self.position.y - self.hitbox.height
        self.check_collisionY(tile_rects)
        
        

        # Update the current animation
        self.current_animation.update(dt)
        self.image = self.current_animation.get_current_frame()


    # check for collision on both axis
    def check_collisionX(self, tile_rect):
        collisions = self.get_hits(tile_rect)
        for tile in collisions:
            if self.velocity.x > 0: # Hit from right
                self.position.x = tile.left - tile.width
                self.rect.x = self.position.x
            elif self.velocity.x < 0: # Hit from left
                self.position.x = tile.right
                self.rect.x = self.position.x

        
    def check_collisionY(self, tile_rect):
        self.on_ground = False  # Reset on_ground before checking for collisions
        self.rect.bottom += 1  # Add 1 pixel buffer for collision detection
        collisions = self.get_hits(tile_rect)
        
        for tile in collisions:
            if self.velocity.y > 0:  # Hit from top (falling onto a tile)
                self.on_ground = True
                self.is_jumping = False
                self.velocity.y = 0
                self.rect.bottom = tile.top  # Align bottom of character to top of tile
                self.position.y = self.rect.bottom  # Sync position with rect
            elif self.velocity.y < 0:  # Hit from bottom (jumping into a ceiling)
                self.velocity.y = 0
                self.rect.top = tile.bottom  # Align top of character to bottom of tile
                self.position.y = self.rect.bottom  # Sync position with rect


    # Helper function for collision detection
    def get_hits(self, tile_rect):
        hits = []
        for tile in tile_rect:
            if self.hitbox.colliderect(tile):
                hits.append(tile)
        return hits

    def limit_velocity(self, max_vel):
        min(-max_vel, max(self.velocity.x, max_vel))
        if abs(self.velocity.x) < .01: self.velocity.x = 0

    def horizontal_movement(self, dt):
        self.acceleration.x = 0
        if self.LEFT_KEY:
            self.acceleration.x -= .3
        elif self.RIGHT_KEY:
            self.acceleration.x += .3
        self.acceleration.x += self.velocity.x * self.friction # Physics eq
        self.velocity.x += self.acceleration.x * dt # Physics eq
        self.limit_velocity(4) # limit the velocity
        self.position.x += self.velocity.x * dt + (self.acceleration.x * 0.5) * (dt * dt) # update the position
        self.rect.x = self.position.x # update the player image by the position

        
    def vertical_movement(self, dt):
        self.velocity.y += self.acceleration.y * dt
        if self.velocity.y > 7: self.velocity.y = 7
        self.position.y += self.velocity.y * dt + (self.acceleration.y * 0.5) * (dt * dt)
        self.rect.bottom = self.position.y

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # Reset movement keys
        self.LEFT_KEY, self.RIGHT_KEY = False, False

        if keys[pygame.K_LEFT]:
            self.LEFT_KEY, self.FACING_LEFT = True, True
            self.current_animation = self.animations['walk']  # Switch to walking animation
        elif keys[pygame.K_RIGHT]:
            self.RIGHT_KEY, self.FACING_LEFT = True, False
            self.current_animation = self.animations['walk']  # Switch to walking animation
        else:
            # Switch to idle animation if not moving and on the ground
            if self.on_ground:
                self.current_animation = self.animations['idle']

        if keys[pygame.K_SPACE] and self.on_ground:
            self.jump()  # Trigger jump
            self.current_animation = self.animations['jump']  # Switch to jump animation
    

    def jump(self):
        if self.on_ground:
            self.is_jumping = True
            self.velocity.y -= 8
            self.on_ground = False