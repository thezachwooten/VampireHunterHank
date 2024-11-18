import pygame
import os

BASE_IMG_PATH = './Data/Images/'

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

# Helps load multiple separate images into frames
def load_separate_frames_from_img(path, num_imgs):
    # create frames
    frames = []
    # loop through num_imgs (starting with 0)
    for i in range(0,num_imgs):
        # load current image based on i
        cur_img = load_image(path + str(i))
        # append to frames list
        frames.append(cur_img)
    # return populated frames list
    return frames