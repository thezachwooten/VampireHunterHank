import pygame
import os

BASE_IMG_PATH = 'Data/Images/'

# Helps load images
def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert_alpha()
    return img

# Helps load and slice spritesheet
def load_spritesheet(path, frame_width, frame_height, num_frames):
    spritesheet = pygame.image.load(BASE_IMG_PATH + path).convert_alpha()  # Load spritesheet
    frames = []

    for i in range(num_frames):
        # Get each frame by slicing the spritesheet
        frame = spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
        frames.append(frame)

    return frames