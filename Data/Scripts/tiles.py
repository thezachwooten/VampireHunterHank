import pygame, csv, os, pytmx

class Tilemap():
    def __init__(self, tmx_file):
        # Load the TMX file using pytmx
        self.tiled_map = pytmx.load_pygame(tmx_file)

    def draw(self, screen):
        # Draw the tilemap on the screen
        for layer in self.tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tiled_map.get_tile_image_by_gid(gid)
                    if tile:
                        screen.blit(tile, (x * self.tiled_map.tilewidth, y * self.tiled_map.tileheight))

    def get_map_size(self):
        # Returns the dimensions of the tilemap
        width = self.tiled_map.width * self.tiled_map.tilewidth
        height = self.tiled_map.height * self.tiled_map.tileheight
        return width, height