import pygame
from Data.Scripts import utils
from Data.Scripts import Animations

class Ghoul():
    def __init__(self, game, position=(0,0)):
        pygame.sprite.Sprite.__init__(self)
        self.game = game

        self.animations = {}

        # Load spritesheets and create animations
        self.animations['idle'] = Animations.Animations(utils.load_spritesheet('Enemies/Ghoul/Idle.png', 32, 32, 4), 60)  # 5 frames at 60 fps
        self.animations['walk'] = Animations.Animations(utils.load_spritesheet('Enemies/Ghoul/Walk.png', 32, 32, 8), 60)  # 5 frames at 60 fps

        self.position, self.velocity = pygame.math.Vector2(position[0], position[1]), pygame.math.Vector2(0, 0)
        self.current_animation = self.animations['idle']  # Start with idle animation
        self.image = self.current_animation.get_current_frame()
        self.rect = self.image.get_rect()
        
        self.update_image() # update ghoul image/mask

        self.last_move_time = 0
        self.state = 'pause'  # Start in the "move_left" state
        self.previous_state = 'move_left'
        self.FACING_LEFT = False
        self.MOVE_LEFT = False
        self.MOVE_RIGHT = False
        self.on_ground = False
        self.gravity, self.friction = .35, -.12
        
        self.acceleration = pygame.math.Vector2(0, self.gravity)

        self.health = 100 # Initilize ghoul health to 100

    def draw(self, surf, camera):
        # Draw the ghoul image using the camera offset
        surf.blit(self.image, camera.apply(self.rect))
        pygame.draw.rect(surf, (255, 0, 0), camera.apply(self.rect), 2)  # Debug: rect around ghoul image

    # Helper function to update image/mask
    def update_image(self):
        # Create the mask and bounding rect based on the current image
        
        self.mask = pygame.mask.from_surface(self.image)
        self.bound_rect = self.mask.get_bounding_rects()[0]
        self.image = self.image.subsurface(self.bound_rect).copy()
        self.image = pygame.transform.scale2x(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = self.position


    def update(self, dt):
        self.horizontal_movement(dt)
        self.move_ai()
        # check if health reaches zero
        if self.health <= 0:
            self.kill()

    def limit_velocity(self, max_vel):
        min(-max_vel, max(self.velocity.x, max_vel))
        if abs(self.velocity.x) < .01: self.velocity.x = 0

    # method to move horizontally 
    def horizontal_movement(self, dt):
        self.acceleration.x = 0
        if self.MOVE_LEFT:
            self.acceleration.x -= .3
            self.FACING_LEFT = True
        elif self.MOVE_RIGHT:
            self.acceleration.x += .3
            self.FACING_LEFT = False
        self.acceleration.x += self.velocity.x * self.friction # Physics eq
        self.velocity.x += self.acceleration.x * dt # Physics eq
        self.limit_velocity(2) # limit the velocity
        self.position.x += self.velocity.x * dt + (self.acceleration.x * 0.5) * (dt * dt) # update the position
        self.rect.x = self.position.x # update the player image by the position

    def move_ai(self):
        current_time = pygame.time.get_ticks()  # Get the current time in milliseconds

        # Pause state
        if self.state == 'pause':
            self.MOVE_LEFT = False
            self.MOVE_RIGHT = False
            if current_time - self.last_move_time >= 2000:  # 2 seconds
                self.last_move_time = current_time
                # Toggle between moving left and right after each pause
                self.state = 'move_right' if self.previous_state == 'move_left' else 'move_left'
                self.previous_state = self.state  # Update the previous state for tracking

        # Move left state
        elif self.state == 'move_left':
            self.MOVE_LEFT = True
            self.MOVE_RIGHT = False
            if current_time - self.last_move_time >= 2000:  # 2 seconds
                self.MOVE_LEFT = False
                self.last_move_time = current_time
                self.state = 'pause'  # Switch to "pause" state

        # Move right state
        elif self.state == 'move_right':
            self.MOVE_LEFT = False
            self.MOVE_RIGHT = True
            if current_time - self.last_move_time >= 2000:  # 2 seconds
                self.MOVE_RIGHT = False
                self.last_move_time = current_time
                self.state = 'pause'  # Switch to "pause" state
