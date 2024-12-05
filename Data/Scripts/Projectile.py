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

        # alive variable
        self.is_alive = True

    def update(self, dt, enemies, ground_tiles, camera_rect):
        # alive update
        if self.is_alive == False:
            self.kill()
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
            self.is_alive = False; # Remove the projectile if its lifetime has passed
        # animation stuff
        if hasattr(self, 'current_animation'):
            self.current_animation.update(dt)
            self.image = self.current_animation.get_current_frame()
            if self.FACING_LEFT == True:
                self.image = pygame.transform.flip(self.image,1,0)

        # collisions
        self.check_collision(enemies)
        self.get_hits(ground_tiles)

    def draw(self, screen, camera):
        # Draw the projectile on the screen
        screen.blit(self.image, camera.apply(self.rect))

    # method to check hits with target_group
    def check_collision(self, target_group):
        collisions = pygame.sprite.spritecollide(self, target_group, False, pygame.sprite.collide_mask)
        if collisions:
            # loop through target 
            for enemy in collisions:
                enemy.health -= enemy.health # Reduce all health as fireball is an insta kill
                print("FIREBALL HIT")  # Destroy the projectile upon collision
                print("ENEMY HEALTH: " + str(enemy.health)) # Destroy the projectile upon collision
            self.kill()

    # method to check hits with envrionment
    def get_hits(self, tile_sprites):
        for tile in tile_sprites:
            if pygame.sprite.collide_mask(self, tile):
                print("Surface Hit")
                self.kill()