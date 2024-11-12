import pygame

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

class Projectile(pygame.sprite.Sprite):
    def __init__(self, image, pos, vel):
        super().__init__()
        self.image = image
        self.rect = self.image.pygame.Surface.get_rect(center=pos)
        self.velocity = pygame.math.Vector2(vel)
        self.lifetime = 3000 # lifetime in ms 
        self.spawn_time = pygame.time.get_ticks()
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
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

    def draw(self, screen):
        # Draw the projectile on the screen
        screen.blit(self.image, self.rect)