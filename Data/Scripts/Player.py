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


        self.current_animation = self.animations['idle']  # Start with idle animation
        self.image = self.current_animation.get_current_frame()
        self.rect = self.image.get_rect()

        self.rectWidth = 128
        self.rectHeight = 128
        self.LEFT_KEY, self.RIGHT_KEY, self.FACING_LEFT = False, False, False 
        self.is_jumping, self.on_ground = False, False
        self.gravity, self.friction = .35, -.12
        self.position, self.velocity = pygame.math.Vector2(0, 0), pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, self.gravity)

    def draw(self, surf):
        surf.blit(self.image, (self.rect.x, self.rect.y))

    def handle_collisions(self, tile_rects):
        # Check for collisions with tiles and adjust position accordingly
        for rect in tile_rects:
            if self.rect.colliderect(rect):
                # Collision detected, handle it
                if self.velocity.y > 0:  # Falling down
                    self.rect.bottom = rect.top  # Stop falling
                    self.on_ground = True
                    self.velocity.y = 0  # Reset vertical velocity
                elif self.velocity.y < 0:  # Jumping up
                    self.rect.top = rect.bottom  # Stop rising
                    self.velocity.y = 0  # Reset vertical velocity
                
                if self.velocity.x > 0:  # Moving right
                    self.rect.right = rect.left  # Stop moving right
                elif self.velocity.x < 0:  # Moving left
                    self.rect.left = rect.right  # Stop moving left

    def update(self, dt, tile_rects):
        # Move
        self.handle_input()
        self.horizontal_movement(dt)
        self.vertical_movement(dt)

        # Handle collisions
        self.handle_collisions(tile_rects)

        # Update the current animation
        self.current_animation.update(dt)
        self.image = self.current_animation.get_current_frame()


        
        

    def limit_velocity(self, max_vel):
        min(-max_vel, max(self.velocity.x, max_vel))
        if abs(self.velocity.x) < .01: self.velocity.x = 0

    def horizontal_movement(self, dt):
        self.acceleration.x = 0
        if self.LEFT_KEY:
            self.acceleration.x -= .3
        elif self.RIGHT_KEY:
            self.acceleration.x += .3
        self.acceleration.x += self.velocity.x * self.friction
        self.velocity.x += self.acceleration.x * dt
        self.limit_velocity(4)
        self.position.x += self.velocity.x * dt + (self.acceleration.x * 0.5) * (dt * dt)
        self.rect.x = self.position.x

        
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