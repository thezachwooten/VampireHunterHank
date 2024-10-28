import pygame

class Animations:
    def __init__(self, frames, frame_rate, loop=True):
        self.frames = frames
        self.frame_rate = frame_rate
        self.current_frame = 0
        self.time_elapsed = 0
        self.is_finished = False  # Add finished flag
        self.loop = loop # defaults to true

    def update(self, dt):
        if self.is_finished:
            return  # Stop updating if animation is finished

        # not looping
        if not self.loop:
            self.time_elapsed += dt
            if self.time_elapsed >= 1000 / self.frame_rate:
                self.time_elapsed = 0
                self.current_frame += 1
                if self.current_frame >= len(self.frames):  # Reached the last frame
                    self.is_finished = True  # Mark animation as finished
                    self.current_frame = len(self.frames) - 1  # Keep on the last frame
        else: # loop
            self.time_elapsed += dt
            if self.time_elapsed >= 1000 / self.frame_rate:
                self.time_elapsed = 0
                self.current_frame += 1
                if self.current_frame >= len(self.frames):  # Reached the last frame
                    self.current_frame = 0  # Keep on the last frame

    def get_current_frame(self):
        return self.frames[self.current_frame]
    
    def get_duration(self):
        return len(self.frames) * (1000 // self.frame_rate)

    def reset(self):
        self.current_frame = 0
        self.time_elapsed = 0
        self.is_finished = False  # Reset finished flag