import pygame
from Data.Scripts import utils
from Data.Scripts import Animations
from Data.Scripts import Projectile # import Projectile class


class Player(pygame.sprite.Sprite):
    def __init__(self, game, position=(0,0)):
        pygame.sprite.Sprite.__init__(self)
        self.game = game

        self.animations = {}

        # Load spritesheets and create animations
        self.animations['idle'] = Animations.Animations(utils.load_spritesheet('Player/Sprites/Converted_Vampire/Idle.png', 128, 128, 5), 120)  # 5 frames at 60 fps
        self.animations['walk'] = Animations.Animations(utils.load_spritesheet('Player/Sprites/Converted_Vampire/Walk.png', 128, 128, 8), 120)  # 8 frames at 60 fps
        self.animations['jump'] = Animations.Animations(utils.load_spritesheet('Player/Sprites/Converted_Vampire/Jump.png', 128, 128, 7), 120)  # 7 frames at 60 fps
        self.animations['attack'] = Animations.Animations(utils.load_spritesheet('Player/Sprites/Converted_Vampire/Attack_2.png', 128, 128, 3), 120, False)  # 3 frames at 60 fps
        self.animations['fire'] = Animations.Animations(utils.load_spritesheet('Player/Sprites/Converted_Vampire/Hurt.png', 128, 128, 1), 120, False)  # 1 frames at 60 fps

        self.position, self.velocity = pygame.math.Vector2(position[0], position[1]), pygame.math.Vector2(0, 0)
        self.current_animation = self.animations['idle']  # Start with idle animation
        
        self.image = self.current_animation.get_current_frame()
        self.rect = self.image.get_rect(center = position)
        self.offsetRect = self.rect.copy() # offset rect

        
        
        # Create the mask and bounding rect based on the current image
        self.update_image()
        self.rect.x = position[0]
        self.rect.y = position[1]
        

        self.LEFT_KEY, self.RIGHT_KEY, self.FACING_LEFT = False, False, False 
        self.is_jumping, self.on_ground = False, False
        self.gravity, self.friction = .35, -.12
        
        self.acceleration = pygame.math.Vector2(0, self.gravity)

        self.health = 100 # Initilize player health to 100
        self.max_health = 100 # Maximum health for player
        self.jumpCount = 0 # for double jump

        self.is_attacking = False
        self.attack_cooldown = 500  # cooldown in milliseconds
        self.last_attack_time = 0

        # level related events
        self.foundPainting = 0 # default to not having map painting

        # healh overlay
        self.health_overlay = utils.load_image("Misc/health_overlay.png")
        self.health_overlay_rect = self.health_overlay.get_rect()
        # resize overlay
        self.health_overlay = pygame.transform.scale(self.health_overlay, (125, 50))

        # current projectiles
        self.projectiles = pygame.sprite.Group()
        self.MaxProjectiles = 1 # current max # of fireballs on screen at a time

    def draw(self, surf, camera):
        # Fix offsets facing left
        if self.FACING_LEFT:
            self.offsetRect = self.rect.copy()
            self.offsetRect.x -= self.rect.width 
            self.offsetRect.y -= self.rect.height - 25
        else:
            # Fix offsets facing right
            self.offsetRect = self.rect.copy()
            self.offsetRect.x -= self.rect.width - 15
            self.offsetRect.y -= self.rect.height - 25
        # Draw the player image using the camera offset 
        surf.blit(self.image, camera.apply(self.offsetRect))
        pygame.draw.rect(surf, (255, 0, 0), camera.apply(self.rect), 2)  # Debug: rect around player image
        # draw healthbar
        # Health bar
        self.draw_health_bar(surf)
        # player projectiles
        for projectile in self.projectiles:
            projectile.draw(surf, camera) # draw 


    def update(self, dt, ground_tile, paintings, portals, enemies_SG, camera):
        # Move
        self.handle_input()
        self.horizontal_movement(dt)
        self.check_collisionX(ground_tile)
        self.vertical_movement(dt)
        self.check_collisionY(ground_tile)

        if self.is_attacking:
            self.check_attack_hits(enemies_SG)

        if self.is_attacking and self.current_animation.is_finished:
            self.is_attacking = False
            self.current_animation.reset()  # Reset animation for next attack

        # Projectile stuff
        for projectile in self.projectiles:
            if projectile.is_alive == False:
                projectile.kill() # remove projectile if it has expired
            projectile.update(dt, enemies_SG, ground_tile, camera.camera_rect) # update

        # painting collision
        self.paintHits(paintings)
        # Portal Collisions
        self.portal_hits(portals)
        
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
                self.velocity.x = 0 # stop movement
                self.position.x = tile.rect.left - self.get_mask_width() - 5  # Prevent overlap
                self.rect.x = self.position.x  # Update rect position
            elif self.velocity.x < 0:  # Moving left
                # Stop at the right edge of the tile
                self.velocity.x = 0 # stop movement
                self.position.x = tile.rect.right # Prevent overlap
                self.rect.x = self.position.x  # Update rect position
                

        
    def check_collisionY(self, tile_sprites):
        self.on_ground = False  # Reset on_ground before checking for collisions
        collisions = self.get_hits(tile_sprites)

        for tile in collisions:
            if self.velocity.y > 0:  # Hit from the top (falling onto a tile)
                self.on_ground = True
                self.jumpCount = 0
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
        self.rect.x = self.position.x # u pdate the player image by the position

        
    def vertical_movement(self, dt):
        self.velocity.y += self.acceleration.y * dt
        if self.velocity.y > 7: self.velocity.y = 7
        self.position.y += self.velocity.y * dt + (self.acceleration.y * 0.5) * (dt * dt)
        self.rect.bottom = self.position.y

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # Reset movement keys
        self.LEFT_KEY, self.RIGHT_KEY = False, False

        if self.is_attacking:
            return  # Exit early if attacking to prevent movement and other actions

        # Only allow movement or idle animations if not attacking
        if keys[pygame.K_LEFT]:
            self.LEFT_KEY, self.FACING_LEFT = True, True
            self.current_animation = self.animations['walk']  # Switch to walking animation
            self.update_image()
        elif keys[pygame.K_RIGHT]:
            self.RIGHT_KEY, self.FACING_LEFT = True, False
            self.current_animation = self.animations['walk']  # Switch to walking animation
            self.update_image()
        else:
            # Switch to idle animation if not moving and on the ground
            if self.on_ground:
                self.current_animation = self.animations['idle']
                self.update_image()

        # Start the jump if on the ground and space is pressed
        if keys[pygame.K_SPACE] and self.on_ground:
            self.jump()
            self.current_animation = self.animations['jump']  # Switch to jump animation
            self.update_image()

        # Start attack if Z key is pressed and not currently attacking
        if keys[pygame.K_z]:
            self.attack()
        # Fireball
        if keys[pygame.K_x] and len(self.projectiles) < self.MaxProjectiles:
            # shoot fireball
            self.fire_fireball()
            self.current_animation = self.animations['fire']
    

    def jump(self):
        if self.on_ground or self.jumpCount < 2:
            self.is_jumping = True
            self.velocity.y -= 10
            self.on_ground = False
            self.jumpCount += 1

    # method for dealing with painting collisions
    def paintHits(self, paintings):
        collisions = self.get_hits(paintings)  # Get the collided paintings

        for painting in collisions:
            if not painting.collected:  # Check if it's already collected
                painting.remove()  # Mark as collected
                self.foundPainting = 1 # Update the player to having the map's painting

    def attack(self):
        current_time = pygame.time.get_ticks()
        if not self.is_attacking and current_time - self.last_attack_time >= self.attack_cooldown:
            self.is_attacking = True
            self.last_attack_time = current_time
            self.current_animation = self.animations['attack']
            self.update_image()
            # Do not reset here; let the update method handle the animation progression
    
    
    # Method for checking attack hits within a range in front of the player
    def check_attack_hits(self, enemies):
        attack_damage = 20  # Define the amount of damage per attack
        attack_range = 30   # Define the range of the attack in pixels
        
        # Determine the attack area based on the player's facing direction
        if self.FACING_LEFT:
            # Create an attack rect extending to the left of the player
            attack_rect = pygame.Rect(
                self.rect.left - attack_range,  # Start slightly to the left of the player
                self.rect.top,                   # Keep the same vertical position
                attack_range,                    # Width of the attack range
                self.rect.height                 # Same height as the player
            )
        else:
            # Create an attack rect extending to the right of the player
            attack_rect = pygame.Rect(
                self.rect.right,                 # Start at the player's right edge
                self.rect.top,                   # Keep the same vertical position
                attack_range,                    # Width of the attack range
                self.rect.height                 # Same height as the player
        )
    
        # Iterate over enemies to see if any are within the attack range
        for enemy in enemies:  # Iterate over a copy of the list
            if enemy.health > 0:  # Only check if the enemy is alive
                if attack_rect.colliderect(enemy.rect):  # Check if enemy is in the attack range
                    # Apply damage to the enemy
                    enemy.health = max(0, enemy.health - attack_damage)
                    print(f"Enemy hit! Health: {enemy.health}")

                    # Check if the enemy’s health has dropped to zero
                    if enemy.health <= 0:
                        print("Enemy has died!")
                        enemy.kill() # Remove dead enemy from the list
    
    # method for dealing with portal interaction
    def portal_hits(self, portals):
        collisions = self.get_hits(portals) # get portals currently colliding with

        for portal in collisions:
            # check if player has map piece
            if self.foundPainting == 1:
                print("MOVING TO NEXT LEVEL")
            else:
                print("NEED TO FIND MAP PIECE")

    # Method to draw health bar with heart overlay
    def draw_health_bar(self, surface):
        bar_width = 92  # Total width of the health bar
        bar_height = 8  # Height of the health bar
        health_ratio = self.health / self.max_health  # Ratio of current to max health
        
        # Calculate the width of the current health portion
        current_bar_width = int(bar_width * health_ratio)
        
        # Set the position of the health bar in the top-left corner of the screen
        bar_x = 25  # Offset the health bar to the right of the heart overlay
        bar_y = 20

        # Position the overlay image
        self.health_overlay_rect.topleft = (5, 0)  # Position the heart at a fixed position

        # Draw the background bar (max health) in red
        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        # Draw the foreground bar (current health) in green
        pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, current_bar_width, bar_height))

        # Draw the heart overlay image to the left of the health bar
        surface.blit(self.health_overlay, self.health_overlay_rect)
    
    # Method for shooting fireballs
    def fire_fireball(self):
        # make sure player is not attacking
        if not self.is_attacking:
            # create a new fireball
            fireball = Projectile.Projectile(
                image= None,
                pos= (self.offsetRect.centerx + 35, self.offsetRect.centery + 30),
                vel=(-5 if self.FACING_LEFT else 5, 0),  # Direction based on facing
                animated = True,
                anims = Animations.Animations(utils.load_separate_frames_from_img("Projectiles/Fireball", 5), 60) # give fireball animations 

            )
            self.projectiles.add(fireball)