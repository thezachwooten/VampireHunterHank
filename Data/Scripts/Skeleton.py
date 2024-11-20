import pygame
import random # module for random choice
from Data.Scripts import utils
from Data.Scripts import Animations

class Skeleton(pygame.sprite.Sprite):
    # Constructor
    def __init__(self, game, position=(0,0), scale=1.5):
        super().__init__()  # Initialize the Sprite parent class
        
        self.game = game
        self.scale = scale
        
        # Animations
        self.animations = {}
        # Idle
        idle_frames = utils.load_spritesheet('Enemies/Skeletons/Idle.png', 128, 128, 7)
        scaled_idle_frames = [pygame.transform.scale(frame, (int(frame.get_width() * self.scale), 
                                                             int(frame.get_height() * self.scale)))
                              for frame in idle_frames]
        self.animations['idle'] = Animations.Animations(scaled_idle_frames, 60)

        # image 
        self.position, self.velocity = pygame.math.Vector2(position[0], position[1]), pygame.math.Vector2(0, 0)
        self.current_animation = self.animations['idle']  # Start with idle animation
        self.image = self.current_animation.get_current_frame()
        # Rect alignment
        self.rect = self.image.get_rect()
        self.rect.centery = self.position.y  # Align the bottom of the rect with the starting position
        self.rect.centerx = self.position.x  # Optionally center the rect horizontally at the position

        self.update_image() # update ghoul image/mask

        self.last_move_time = 0
        self.state = 'pause'  # Start in the "move_left" state
        self.FACING_LEFT = random.choice([True, False])

        self.health = 100 # Initilize ghoul health to 100
        self.isDead = False

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
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    def update(self, dt, player):
        # self.horizontal_movement(dt)
        # self.move_ai()
        # check if health reaches zero
        if self.health <= 0:
            self.kill()
        # Update the current animation
        self.current_animation.update(dt)
        self.image = self.current_animation.get_current_frame()
        if self.FACING_LEFT == True:
            self.image = pygame.transform.flip(self.image,1,0)
        self.update_image()