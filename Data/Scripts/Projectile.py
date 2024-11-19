import pygame

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

class Projectile(pygame.sprite.Sprite):
    def __init__(self, image, pos, vel , animated=False, anims=None):
        super().__init__()
        # if not animated
        if animated == False:
            self.image = image
            self.rect = self.image.get_rect(center=pos)
        self.velocity = pygame.math.Vector2(vel)
        self.lifetime = 3000 # lifetime in ms 
        self.spawn_time = pygame.time.get_ticks()
        # handle if projectile is animated
        if animated == True:
            # create animations dict
            self.animations = anims
            # default animation for projectiles should be named move
            self.current_animation = self.animations
            # get the current image from current frame
            self.image = self.current_animation.get_current_frame()
            # get rect for image
            self.rect = self.image.get_rect(center = pos)

        # handle mask
        self.mask = pygame.mask.from_surface(self.image)

        # facing left and right
        self.FACING_LEFT = False
        self.FACING_RIGHT = False

    def update(self, dt):
        # update what direction projectile is facing based on its velocity
        if (self.velocity.x < 0):
            self.FACING_RIGHT = False
            self.FACING_LEFT = True
        elif (self.velocity.x > 0):
            self.FACING_LEFT = False
            self.FACING_RIGHT = True
        else:
            self.FACING_RIGHT = False
            self.FACING_LEFT = False

        # Update image if facing left
        if self.FACING_LEFT == True:
            self.image = pygame.transform.flip(self.image,1,0)

        # move the projectile by its velocity
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        # check if projectile expired
        current_time = pygame.time.get_ticks()
        if current_time - self.spawn_time >= self.lifetime:
            self.kill() # Remove the projectile if its lifetime has passed
        # Remove if it goes off-screen
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill() # Remove
        # animation stuff
        if hasattr(self, 'current_animation'):
            self.current_animation.update(dt)
            self.image = self.current_animation.get_current_frame()
            if self.FACING_LEFT == True:
                self.image = pygame.transform.flip(self.image,1,0)

    def draw(self, screen):
        # Draw the projectile on the screen
        screen.blit(self.image, self.rect)