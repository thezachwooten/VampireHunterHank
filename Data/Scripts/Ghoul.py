import pygame
from Data.Scripts import utils
from Data.Scripts import Animations

class Ghoul(pygame.sprite.Sprite):
    # Constructor
    def __init__(self, game, position=(0,0)):
        super().__init__()  # Initialize the Sprite parent class
        self.game = game

        self.animations = {}

        # Load spritesheets and create animations
        self.animations['idle'] = Animations.Animations(utils.load_spritesheet('Enemies/Ghoul/Idle.png', 32, 32, 4), 60)  # 4 frames at 60 fps
        self.animations['walk'] = Animations.Animations(utils.load_spritesheet('Enemies/Ghoul/Walk.png', 32, 32, 8), 60)  # 8 frames at 60 fps
        self.animations['hit'] = Animations.Animations(utils.load_spritesheet('Enemies/Ghoul/Hit.png', 32, 32, 4), 60, False)  # 4 frames at 60 fps
        self.animations['death'] = Animations.Animations(utils.load_spritesheet('Enemies/Ghoul/Death.png', 32, 32, 6), 60, False)  # 6 frames at 60 fps
        self.animations['attack'] = Animations.Animations(utils.load_spritesheet('Enemies/Ghoul/Attack.png', 32, 32, 6), 60, False)  # 6 frames at 60 fps

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
        self.isDead = False # Ghoul is not dead
        self.is_dying = False # Ghoul is not dying 

        self.is_attacking = False # Ghoul is not attacking  
        self.attack_cooldown = 500  # cooldown in milliseconds
        self.last_attack_time = 0 # 0 since last attack

        self.player_detected = False # player is not detected

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


    def update(self, dt, player):
        self.horizontal_movement(dt)
        # check if player is deteced
        self.move_ai() # move
        self.check_attack(player) # check if player can be attacked and attack if so
        # check if health reaches zero
        if self.health <= 0:
            # Set current animation to death
            self.current_animation = self.animations['death']
            # Get current time and animation length
            self.death_start_time = pygame.time.get_ticks()
            self.animation_length = self.current_animation.get_duration()
    
            # Update a flag to indicate that the sprite is in the "dying" state
            self.is_dying = True
        
        # In your update method
        if self.is_dying:
            # Calculate elapsed time since the death animation started
            elapsed_time = pygame.time.get_ticks() - self.death_start_time
            # Check if the elapsed time exceeds the animation length
            if elapsed_time >= self.animation_length:
                # Delete the sprite after the animation completes
                self.kill()
            return 
        # Update the current animation
        self.current_animation.update(dt)
        self.image = self.current_animation.get_current_frame()
        if self.FACING_LEFT == True:
            self.image = pygame.transform.flip(self.image,1,0)
        self.update_image()

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
                self.current_animation = self.animations['walk']

        # Move left state
        elif self.state == 'move_left':
            self.MOVE_LEFT = True
            self.MOVE_RIGHT = False
            if current_time - self.last_move_time >= 2000:  # 2 seconds
                self.MOVE_LEFT = False
                self.last_move_time = current_time
                self.state = 'pause'  # Switch to "pause" state
                self.current_animation = self.animations['idle']

        # Move right state
        elif self.state == 'move_right':
            self.MOVE_LEFT = False
            self.MOVE_RIGHT = True
            if current_time - self.last_move_time >= 2000:  # 2 seconds
                self.MOVE_RIGHT = False
                self.last_move_time = current_time
                self.state = 'pause'  # Switch to "pause" state
                self.current_animation = self.animations['idle']

    def attack(self):
        current_time = pygame.time.get_ticks()
        if not self.is_attacking and current_time - self.last_attack_time >= self.attack_cooldown:
            self.is_attacking = True
            self.last_attack_time = current_time
            self.current_animation = self.animations['attack']
            self.update_image()
            # Do not reset here; let the update method handle the animation progression

    # method for checking attack hits
    def check_attack_hits(self, player):
        if player.health > 0:  # Only check if the player is alive
                if pygame.sprite.collide_mask(self, player):
                    if self.FACING_LEFT:
                        if self.rect.left - player.rect.right < 20:  # Check distance to the player
                            player.health -= 10  # Damage dealt
                            print("Player hit! Health:", player.health)
                    else:
                        if player.rect.left - self.rect.right < 20:
                            player.health -= 10
                            print("player hit! Health:", player.health)

                    # Check if enemy health is now zero or below
                    if player.health <= 0:
                        print("player has died!")
                        player.kill() # kill player sprite
    
    def check_attack(self, player):
        current_time = pygame.time.get_ticks()
        
        # Check if within attack cooldown
        if self.is_attacking and current_time - self.last_attack_time < self.attack_cooldown:
            return
        
        # Collision-based attack initiation
        if pygame.sprite.collide_mask(self, player):  # Pixel-perfect collision check
            # Initiate attack if collision occurs
            self.is_attacking = True
            self.last_attack_time = current_time
            self.current_animation = self.animations['attack']
            
            # Deal damage to the player
            if player.health > 0:
                player.health -= 20  # Apply damage
                print(f"Player hit! Health: {player.health}")
                
                # Apply knockback based on enemy's position relative to the player
                if self.rect.centerx < player.rect.centerx:
                    player.velocity.x += 10  # Knockback to the right
                else:
                    player.velocity.x -= 10  # Knockback to the left

            # Check if the player's health reaches zero
            if player.health <= 0:
                print("Player has died!")
        else:
            # Reset attacking state if not colliding
            self.is_attacking = False