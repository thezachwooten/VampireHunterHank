import pygame

class Tilemap:
    def __init__(self, tile_size=16):
        self.tile_size = tile_size
        self.tilemap = {} # ON SCREEN
        self.offgrid_tiles = [] # OFF SCREEN

        for i in range(10):
            self.tilemap[str(3 + i) + ';10'] = {'typeL'}