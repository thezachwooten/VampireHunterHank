import pygame
import random # module for random choice
from Data.Scripts import utils
from Data.Scripts import Animations
from Data.Scripts import Projectile

class Vampire(pygame.sprite.Sprite):
    # Constructor
    def __init__(self, game, position=(0,0)):
        super().__init__()  # Initialize the Sprite parent class
        self.game = game

        self.animations = {}

        # Load spritesheets and create animations
        self.animations['idle'] = Animations.Animations(utils.load_spritesheet('Enemies/Countess_Vampire/Idle.png', 128, 128, 5), 60)  # 5 frames at 60 fps
        self.animations['walk'] = Animations.Animations(utils.load_spritesheet('Enemies/Countess_Vampire/Walk.png', 128, 128, 6), 60)  # 5 frames at 60 fps
        self.animations['attack'] = Animations.Animations(utils.load_spritesheet('Enemies/Countess_Vampire/Attack_1.png', 128, 128, 6), 120, False)
        self.animations['death'] = Animations.Animations(utils.load_spritesheet('Enemies/Countess_Vampire/Dead.png', 128, 128, 8), 60, False) # Death

        self.position, self.velocity = pygame.math.Vector2(position[0], position[1]), pygame.math.Vector2(0, 0)
        self.current_animation = self.animations['idle']  # Start with idle animation
        self.image = self.current_animation.get_current_frame()
        self.rect = self.image.get_rect()
        
        self.update_image() # update Vampire image/mask

        self.last_move_time = random.randint(0,5) # random time since last move
        self.state = 'pause'  # Start in the "move_left" state
        self.previous_state = 'move_left'
        self.FACING_LEFT = random.choice([True, False])
        self.MOVE_LEFT = False
        self.MOVE_RIGHT = False
        self.on_ground = False
        self.gravity, self.friction = .35, -.12
        
        self.acceleration = pygame.math.Vector2(0, self.gravity)

        self.health = 100 # Initilize vamp health to 100
        self.isDead = False # vamp is not dead
        self.is_dying = False # vamp is not dying 

        self.is_attacking = False # vamp is not attacking  
        self.attack_cooldown = 1.0  # Time between attacks
        self.last_attack_time = 0
        self.attack_width = 50  # Width of attack rect
        self.attack_height = 50  # Height of attack rect
        self.range_width = 200 # width of ranged rect
        self.ranged_height = self.attack_height # set ranged rect height == attack_rect_height

        self.player_detected = False # player is not detected 
        self.projectiles = pygame.sprite.Group()

    def draw(self, surf, camera):
        # Draw the Vampire image using the camera offset
        surf.blit(self.image, camera.apply(self.rect))
        for projectile in self.projectiles:
            projectile.draw(surf, camera) # draw 
        # debug for range rect
        range_rect = self.get_ranged_rect()
        pygame.draw.rect(surf, (255, 0, 0), camera.apply(range_rect), 1) 

    # Helper function to update image/mask
    def update_image(self):
        self.rect = self.image.get_rect()
        self.rect.center = self.position


    def update(self, dt, player, ground_tile, camera, playerSG):
        # check if player is deteced
        if not self.is_dying:
            self.horizontal_movement(dt)
            self.move_ai() # move
            if self.state == 'pause': # if vamp is paused, draw the detection rect in order to fire
                if self.can_attack_range(player): # check if player can be seen ranged
                    self.fireball() # shoot fireball
            if self.can_attack(player): # check if player can be attacked and attack if so
                self.attack(player)
        # check if health reaches zero
        if self.health <= 0 and not self.is_dying:
            # Set the current animation to death
            self.current_animation = self.animations['death']
            self.death_start_time = pygame.time.get_ticks()
            self.animation_length = self.current_animation.get_duration()
            self.is_dying = True
        
        # In your update method
        if self.is_dying:
            self.velocity.x = 0
            # Check if the animation has reached end and is the death animation
            if self.current_animation.is_finished and self.current_animation == self.animations['death']:
                # Delete the sprite after the animation completes
                self.kill()
        # Update projectiles
        for projectile in self.projectiles:
            if not projectile.is_alive:
                projectile.kill()
            projectile.update(dt, playerSG, ground_tile, camera.camera_rect)
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
            if current_time - self.last_move_time >= 5000:  # 5 seconds
                self.last_move_time = current_time
                # Toggle between moving left and right after each pause
                self.state = 'move_right' if self.previous_state == 'move_left' else 'move_left'
                self.previous_state = self.state  # Update the previous state for tracking
                self.current_animation = self.animations['walk']

        # Move left state
        elif self.state == 'move_left':
            self.MOVE_LEFT = True
            self.MOVE_RIGHT = False
            if current_time - self.last_move_time >= 5000:  # 5 seconds
                self.MOVE_LEFT = False
                self.last_move_time = current_time
                self.state = 'pause'  # Switch to "pause" state
                self.current_animation = self.animations['idle']

        # Move right state
        elif self.state == 'move_right':
            self.MOVE_LEFT = False
            self.MOVE_RIGHT = True
            if current_time - self.last_move_time >= 5000:  # 5 seconds
                self.MOVE_RIGHT = False
                self.last_move_time = current_time
                self.state = 'pause'  # Switch to "pause" state
                self.current_animation = self.animations['idle']
    
    # method for attack (melee) detection rect
    def get_attack_rect(self):
        if self.FACING_LEFT:  # Left
            return pygame.Rect((self.rect.left - self.attack_width + 50), self.rect.top + (self.rect.height /2 ), self.attack_width, self.attack_height)
        else:
            return pygame.Rect(self.rect.right - 50, self.rect.top + (self.rect.height /2 ), self.attack_width, self.attack_height)

    def can_attack(self, player):
        now = pygame.time.get_ticks() / 1000  # Current time in seconds
        if now - self.last_attack_time < self.attack_cooldown:
            return False  # Still on cooldown

        # Check if the player is inside the attack rect
        attack_rect = self.get_attack_rect()
        return attack_rect.colliderect(player.rect)

    def attack(self, player):
        # attack animation
        current_time = pygame.time.get_ticks()
        self.is_attacking = True
        self.last_attack_time = current_time
        self.current_animation = self.animations['attack']
        # Determine direction and execute attack logic
        if player.rect.centerx > self.rect.centerx:
            player.velocity.x += 10  # Knockback to the right
            print("Attacking player to the right!")
        else:
            player.velocity.x -= 10  # Knockback to the left
            print("Attacking player to the left!")

        # Example: Reduce player's health or apply effects
        player.health -= 10  # Example damage value

        # Reset attack cooldown
        self.last_attack_time = pygame.time.get_ticks() / 1000

    # method for attack (fireball) rect detection
    def get_ranged_rect(self):
        if self.FACING_LEFT:  # Left
            return pygame.Rect((self.rect.left - self.range_width + 50), self.rect.top + (self.rect.height /2 ), self.range_width, self.ranged_height)
        else:
            return pygame.Rect(self.rect.right - 50, self.rect.top + (self.rect.height /2 ), self.range_width, self.ranged_height)
    # method to check if able to attack rn
    def can_attack_range(self, player):
        now = pygame.time.get_ticks() / 1000  # Current time in seconds
        if now - self.last_attack_time < self.attack_cooldown:
            return False  # Still on cooldown

        # Check if the player is inside the attack rect
        range_rect = self.get_ranged_rect()
        return range_rect.colliderect(player.rect)
    # method to fire fireball
    def fireball(self):
        # Start the attack animation if not already attacking
        if not self.is_attacking and len(self.projectiles) < 1:
            self.is_attacking = True
            self.current_animation = self.animations['attack']
            self.attack_start_time = pygame.time.get_ticks()  # Record when the animation started

        # Check if the animation has finished
        animation_duration = self.current_animation.get_duration()  # Get the total duration of the attack animation
        elapsed_time = pygame.time.get_ticks() - self.attack_start_time  # Calculate how much time has passed

        if elapsed_time >= animation_duration + 200:
            # Create the fireball after the animation is complete
            fireball = Projectile.Projectile(
                image=None,
                pos=(self.rect.right if not self.FACING_LEFT else self.rect.left, self.rect.centery + 10),
                vel=(-3 if self.FACING_LEFT else 3, 0),  # Direction based on facing
                animated=True,
                anims=Animations.Animations(utils.load_separate_frames_from_img("Projectiles/Fireball", 5), 60)  # Fireball animations
            )
            self.projectiles.add(fireball)

            # Reset the attack state
            self.is_attacking = False
            self.last_attack_time = pygame.time.get_ticks() / 1000  # Reset cooldown timer
