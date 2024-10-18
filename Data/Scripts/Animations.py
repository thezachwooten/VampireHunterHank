import pygame

class Animations:
    def __init__(self, frames, frame_rate):
        self.frames = frames  # List of frames
        self.frame_rate = frame_rate  # Frame rate (frames per second)
        self.current_frame = 0  # Current frame in the animation
        self.time_elapsed = 0  # Time since last frame change

    def update(self, dt):
        # Update the animation frame based on the time elapsed
        self.time_elapsed += dt
        if self.time_elapsed >= 1000 / self.frame_rate:  # Time per frame (in milliseconds)
            self.time_elapsed = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)  # Loop through frames

    def get_current_frame(self):
        return self.frames[self.current_frame]  # Return the current frame to draw
