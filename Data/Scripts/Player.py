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

        self.position, self.velocity = pygame.math.Vector2(100, 0), pygame.math.Vector2(0, 0)
        self.current_animation = self.animations['idle']  # Start with idle animation
        self.image = self.current_animation.get_current_frame()
        self.rect = self.image.get_rect()
        
        # Create the mask and bounding rect based on the current image
        self.update_image()

        self.rectWidth = 128
        self.rectHeight = 128

        self.LEFT_KEY, self.RIGHT_KEY, self.FACING_LEFT = False, False, False 
        self.is_jumping, self.on_ground = False, False
        self.gravity, self.friction = .35, -.12
        
        self.acceleration = pygame.math.Vector2(0, self.gravity)

        self.health = 100 # Initilize player health to 100

    def draw(self, surf):
        surf.blit(self.image, (self.rect.x - self.get_mask_width(), self.rect.y - self.get_mask_height() + 25))
        pygame.draw.rect(surf, (255,0,0), self.rect, 2) # rect around player image
        pygame.draw.rect(surf, (255,255,0), self.bound_rect, 2) # rect around player image


    def update(self, dt, tile_rects):
        # Move
        self.handle_input()
        self.horizontal_movement(dt)
        self.check_collisionX(tile_rects)
        self.vertical_movement(dt)
        self.check_collisionY(tile_rects)
        
        

        # Update the current animation
        self.current_animation.update(dt)
        self.image = self.current_animation.get_current_frame()
        if self.FACING_LEFT == True:
            self.image = pygame.transform.flip(self.image,1,0)

    # Helper function to update image/mask
    def update_image(self):
        # Create the mask and bounding rect based on the current image
        
        self.mask = pygame.mask.from_surface(self.image)
        self.bound_rect = self.mask.get_bounding_rects()[0]
        self.image = self.image.subsurface(self.bound_rect).copy()
        self.rect = self.image.get_rect()

    # Helper functions for returning size of mask
    def get_mask_width(self):
        return self.mask.get_size()[0]  # Returns the width of the mask
    def get_mask_height(self):
        return self.mask.get_size()[1]  # Returns the width of the mask



    def check_collisionX(self, tile_sprites):
        collisions = self.get_hits(tile_sprites)
        for tile in collisions:
            if self.velocity.x > 0:  # Moving right
                # Stop at the left edge of the tile
                self.position.x = tile.rect.left - self.get_mask_width()  # Prevent overlap
                self.rect.x = self.position.x  # Update rect position
                self.velocity.x = 0 # stop movement
            elif self.velocity.x < 0:  # Moving left
                # Stop at the right edge of the tile
                self.position.x = tile.rect.right # Prevent overlap
                self.rect.x = self.position.x  # Update rect position
                self.velocity.x = 0 # stop movement

        
    def check_collisionY(self, tile_sprites):
        self.on_ground = False  # Reset on_ground before checking for collisions
        collisions = self.get_hits(tile_sprites)

        for tile in collisions:
            if self.velocity.y > 0:  # Hit from the top (falling onto a tile)
                self.on_ground = True
                self.is_jumping = False
                self.velocity.y = 0  # Stop downward velocity
                self.rect.bottom = tile.rect.top   # Align bottom of player with top of tile
                self.position.y = self.rect.bottom  # Sync position with rect
            elif self.velocity.y < 0:  # Hit from the bottom (jumping into a ceiling)
                self.velocity.y = 0  # Stop upward velocity
                self.rect.top = tile.rect.bottom  # Align top of player with bottom of tile
                self.position.y = self.rect.bottom  # Sync position with rect


    # Helper function for collision detection
    def get_hits(self, tile_sprites):
        hits = []
        for tile in tile_sprites:
            if pygame.sprite.collide_mask(self, tile):
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
            # Create the mask and bounding rect based on the current image
            self.update_image()
        elif keys[pygame.K_RIGHT]:
            self.RIGHT_KEY, self.FACING_LEFT = True, False
            self.current_animation = self.animations['walk']  # Switch to walking animation
            # Create the mask and bounding rect based on the current image
            self.update_image()
        else:
            # Switch to idle animation if not moving and on the ground
            if self.on_ground:
                self.current_animation = self.animations['idle']
                # Create the mask and bounding rect based on the current image
                self.update_image()

        if keys[pygame.K_SPACE] and self.on_ground:
            self.jump()  # Trigger jump
            self.current_animation = self.animations['jump']  # Switch to jump animation
            # Create the mask and bounding rect based on the current image
            self.update_image()
    

    def jump(self):
        if self.on_ground:
            self.is_jumping = True
            self.velocity.y -= 10
            self.on_ground = False