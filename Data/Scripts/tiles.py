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
        self.name = None

    def draw(self, screen, camera):
        # Draw the tilemap on the screen with camera offset
        for layer in self.tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tiled_map.get_tile_image_by_gid(gid)
                    if tile:
                        # Apply the camera offset when drawing each tile
                        screen.blit(tile, camera.apply(pygame.Rect(
                            x * self.tiled_map.tilewidth,
                            y * self.tiled_map.tileheight,
                            self.tiled_map.tilewidth,
                            self.tiled_map.tileheight
                        )))


    def get_map_size(self):
        # Returns the dimensions of the tilemap
        width = self.tiled_map.width * self.tiled_map.tilewidth
        height = self.tiled_map.height * self.tiled_map.tileheight
        return width, height
    
    def get_tile_objects_with_masks(self, layer_name=None, property_name="collision"):
        """Returns a group of tiles as sprites with rects and masks for collision.
        Can filter by layer name and property name.
        """
        tile_sprites = pygame.sprite.Group()  # Use a sprite group to hold Tile objects
        for layer in self.tiled_map.visible_layers:
            # Filter by layer name if specified
            if isinstance(layer, pytmx.TiledTileLayer) and (layer_name is None or layer.name == layer_name):
                for x, y, gid in layer:
                    tile_image = self.tiled_map.get_tile_image_by_gid(gid)
                    tile_properties = self.tiled_map.get_tile_properties_by_gid(gid)
                    
                    # Only process tiles with the specified property
                    if tile_image and tile_properties and tile_properties.get(property_name, False):
                        # Create a Tile instance with position and size
                        tile = Tile(tile_image, 
                                    x * self.tiled_map.tilewidth, 
                                    y * self.tiled_map.tileheight, 
                                    self.tiled_map.tilewidth, 
                                    self.tiled_map.tileheight)
                        
                        # Assign a mask to the tile for pixel-perfect collision
                        tile.mask = pygame.mask.from_surface(tile.image)
                        
                        tile_sprites.add(tile)  # Add the tile to the sprite group
        return tile_sprites  # Return sprite group with masks for pixel-perfect collision