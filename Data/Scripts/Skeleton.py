import pygame
from Data.Scripts import utils
from Data.Scripts import Animations

class Skeleton(pygame.sprite.Sprite):
    # Constructor
    def __init__(self, game, position=(0,0)):
        super().__init__()  # Initialize the Sprite parent class
        
        self.game = game
        
        # Animations
        self.animations = {}
        self.animations['idle'] = Animations.Animations(utils.load_spritesheet('Enemies/Skeletons/Idle.png', 128, 128, 7), 60) # default animation

        # image 
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

    def update(self, dt):
        # self.horizontal_movement(dt)
        # self.move_ai()
        # check if health reaches zero
        if self.health <= 0:
            self.kill()