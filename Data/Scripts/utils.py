import pygame
import os

BASE_IMG_PATH = 'Data/Images/'

def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0,0,0))
    return img