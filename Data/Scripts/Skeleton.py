import pygame
import random # module for random choice
from Data.Scripts import Projectile 
from Data.Scripts import utils
from Data.Scripts import Animations

class Skeleton(pygame.sprite.Sprite):
    # Constructor
    def __init__(self, game, position=(0,0), scale=1.3):
        super().__init__()  # Initialize the Sprite parent class
        
        self.game = game
        self.scale = scale
        self.type = "skelly"        

        # Animations
        self.animations = {}
        # Idle
        idle_frames = utils.load_spritesheet('Enemies/Skeletons/Idle.png', 128, 128, 7)
        scaled_idle_frames = [pygame.transform.scale(frame, (int(frame.get_width() * self.scale), 
                                                             int(frame.get_height() * self.scale)))
                              for frame in idle_frames]
        self.animations['idle'] = Animations.Animations(scaled_idle_frames, 60)
        # Fire
        fire_frames = utils.load_spritesheet('Enemies/Skeletons/Shot_1.png', 128, 128, 13)
        scaled_fire_frames = [pygame.transform.scale(frame, (int(frame.get_width() * self.scale), 
                                                             int(frame.get_height() * self.scale)))
                              for frame in fire_frames]
        self.animations['fire'] = Animations.Animations(scaled_fire_frames, 240, False)

        # image 
        self.position, self.velocity = pygame.math.Vector2(position[0], position[1]), pygame.math.Vector2(0, 0)
        self.current_animation = self.animations['idle']  # Start with idle animation
        self.image = self.current_animation.get_current_frame()
        self.rect = self.image.get_rect()
        # Rect alignment
        self.update_image() # update skeleton image/mask

        self.last_move_time = 0
        self.state = 'pause'  # Start in the "pause" state
        self.FACING_LEFT = random.choice([True, False])
        self.MOVE_LEFT = False
        self.MOVE_RIGHT = False

        self.health = 100 # Initilize Skeleton health to 100
        self.isDead = False

        self.gravity, self.friction = .35, -.12
        self.acceleration = pygame.math.Vector2(0, self.gravity)

        self.is_attacking = False # Start not attacking
        self.see_player = False

        self.projectiles = pygame.sprite.Group()
        self.time_since_turn = 0

    def draw(self, surf, camera):
        # Draw the skeleton image using the camera offset
        surf.blit(self.image, camera.apply(self.rect))
        # pygame.draw.rect(surf, (255,0,0), self.rect, 2) # debug rect

        for projectile in self.projectiles:
            projectile.draw(surf, camera)


    # Helper function to update image/mask
    def update_image(self):
        # Create the mask from the full image
        self.mask = pygame.mask.from_surface(self.image)
        
        # Ensure the rect aligns with the current image and position
        self.rect = self.image.get_rect()
        self.rect.centerx = self.position.x  # Align rect with position
        self.rect.bottom = self.position.y + 15 # weird floating so added this 15 to push down. Can't move so shouldn't be an issue

    def update(self, dt, player, ground_tile, camera, playerSG):
        self.time_since_turn += 1
        self.horizontal_movement(dt)
        self.detect_player(player, 200)

        # Handle shooting logic
        if self.is_attacking:
            if self.current_animation.is_finished:  # Check if the fire animation is done
                print("Firing")
                # Release the arrow
                arrow = Projectile.Projectile(
                    image=utils.load_image("Projectiles/Arrow/0.png"),
                    pos=(self.rect.centerx - 75 if self.FACING_LEFT else self.rect.centerx + 75, 
                        self.rect.centery + 10),
                    vel=(-3 if self.FACING_LEFT else 3, 0),
                )
                self.projectiles.add(arrow)
                self.current_animation = self.animations['idle']  # Return to idle animation
                self.is_attacking = False  # Reset attacking state

        # Update the current animation
        self.current_animation.update(dt)
        self.image = self.current_animation.get_current_frame()
        if self.FACING_LEFT:
            self.image = pygame.transform.flip(self.image, 1, 0)
        self.update_image()

        # Update projectiles
        for projectile in self.projectiles:
            if not projectile.is_alive:
                projectile.kill()
            projectile.update(dt, playerSG, ground_tile, camera.camera_rect)

        # Random turn logic
        if not self.see_player and self.time_since_turn > 200:
            self.time_since_turn = 0
            self.FACING_LEFT = not self.FACING_LEFT
        # health
        if self.health <= 0:
            self.kill()


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

    # method to limit velocity
    def limit_velocity(self, max_vel):
        min(-max_vel, max(self.velocity.x, max_vel))
        if abs(self.velocity.x) < .01: self.velocity.x = 0

    # method to detect player via a invisible box
    def detect_player(self, player, attack_range):
        # Determine the attack area based on the player's facing direction
        if self.FACING_LEFT:
            # Create an attack rect extending to the left of the player
            attack_rect = pygame.Rect(
                self.rect.left - attack_range + 50,  # Start slightly to the left of the player
                self.rect.top + 75,                   # Keep the same vertical position
                attack_range,                    # Width of the attack range
                self.rect.height /2                # Same height as the player
            )
        else:
            # Create an attack rect extending to the right of the player
            attack_rect = pygame.Rect(
                self.rect.right - 50,                 # Start at the player's right edge
                self.rect.top + 75,                   # Keep the same vertical position
                attack_range,                    # Width of the attack range
                self.rect.height / 2               # Same height as the player
        ) 
            
        # detection with above rect
        if player.health > 0: # only if player is alive
            if attack_rect.colliderect(player.rect) and len(self.projectiles) < 1:
                self.see_player = True
                self.shoot_arrow()
            else:
                self.see_player = False
            
        

    # method to shoot arrow if player is detected
    def shoot_arrow(self):
        if not self.is_attacking:
            self.is_attacking = True  # Set attacking state
            self.current_animation = self.animations['fire']  # Trigger fire animation
            self.current_animation.reset()  # Reset animation to start from the beginning
