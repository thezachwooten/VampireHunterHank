import pygame, csv, os, pytmx

class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y, width, height):
        super().__init__()
        self.image = image
        self.rect = pygame.Rect(x, y, width, height)
        self.mask = pygame.mask.from_surface(image)  # Create a mask from the image surface

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
        # Debug: Draw the tile collision boxes
        for rect in self.get_tile_rects():
            pygame.draw.rect(screen, (255, 0, 0, 100), rect, 2)  # Red rectangle with transparency


    def get_map_size(self):
        # Returns the dimensions of the tilemap
        width = self.tiled_map.width * self.tiled_map.tilewidth
        height = self.tiled_map.height * self.tiled_map.tileheight
        return width, height
    
    def get_tile_rects(self):
        #Return a list of rectangles for specific tiles in the tilemap 
        tile_rects = []
        for layer in self.tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    # Check the properties directly from the tile set
                    tile_properties = self.tiled_map.get_tile_properties_by_gid(gid)
                    
                    # Check for the custom attribute "collision"
                    if tile_properties and tile_properties.get('collision', False):  # Assuming 'collision' is a boolean
                        rect = pygame.Rect(x * self.tiled_map.tilewidth, 
                                           y * self.tiled_map.tileheight, 
                                           self.tiled_map.tilewidth, 
                                           self.tiled_map.tileheight)
                        tile_rects.append(rect)
        return tile_rects
    
    def get_tile_objects_with_masks(self):
        """Returns a group of tiles as sprites with rects and masks for collision."""
        tile_sprites = pygame.sprite.Group()  # Use a sprite group to hold Tile objects
        for layer in self.tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile_image = self.tiled_map.get_tile_image_by_gid(gid)
                    tile_properties = self.tiled_map.get_tile_properties_by_gid(gid)
                    
                    # Only process tiles with the 'collision' property
                    if tile_image and tile_properties and tile_properties.get('collision', False):
                        # Create a Tile object with image, rect, and mask
                        tile = Tile(tile_image, 
                                    x * self.tiled_map.tilewidth, 
                                    y * self.tiled_map.tileheight, 
                                    self.tiled_map.tilewidth, 
                                    self.tiled_map.tileheight)
                        tile_sprites.add(tile)  # Add the tile to the sprite group
        return tile_sprites  # Return sprite group with masks for pixel-perfect collision