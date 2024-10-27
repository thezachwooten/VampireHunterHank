import pygame
from Data.Scripts import utils
from Data.Scripts import Animations

class Ghoul():
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game

        self.animations = {}

        # Load spritesheets and create animations
        self.animations['idle'] = Animations.Animations(utils.load_spritesheet('Enemies/Ghoul/Idle.png', 32, 32, 4), 60)  # 5 frames at 60 fps
        self.animations['walk'] = Animations.Animations(utils.load_spritesheet('Enemies/Ghoul/Walk.png', 32, 32, 8), 60)  # 5 frames at 60 fps

        self.position, self.velocity = pygame.math.Vector2(200, 200), pygame.math.Vector2(0, 0)
        self.current_animation = self.animations['idle']  # Start with idle animation
        self.image = self.current_animation.get_current_frame()
        self.rect = self.image.get_rect()
        
        self.update_image() # update ghoul image/mask

        self.FACING_LEFT = False
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