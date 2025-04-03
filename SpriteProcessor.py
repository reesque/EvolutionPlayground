from enum import Enum

import pygame
from PIL import Image, ImageSequence
import numpy as np


class EntitySprite(Enum):
    CHICKEN = 0
    CRAB = 1
    TOAD = 2
    PIG = 3
    GOOSE = 4
    FROG = 5
    BOAR = 6
    CAT = 7
    SHEEP = 8
    TURTLE = 9
    FOX = 10
    PORCUPINE = 11
    SKUNK = 12
    WOLF = 13

    def get_path(self):
        return f"{self.name.capitalize()}.gif"


class SpriteLoader:
    def __init__(self):
        # Entity
        self.entity_sprite = {}

        for _, item in enumerate(EntitySprite):
            gif = Image.open(f'assets/Entity/{item.get_path()}')

            frames = [pygame.image.fromstring(frame.convert("RGBA").tobytes(), frame.size, "RGBA")
                      for frame in ImageSequence.Iterator(gif)]

            frames = [pygame.transform.scale(frame, (frame.get_width() * 1.5, frame.get_height() * 1.5))
                      for frame in frames]

            self.entity_sprite[item.name] = frames

        # Tile
        self.tile_sprite = []
        for i in range(1, 5):
            tile = Image.open(f'assets/Tile/Tile{i}.png')
            self.tile_sprite.append(pygame.image.fromstring(tile.convert("RGBA").tobytes(), tile.size, "RGBA"))

        # Food
        self.food_sprite = []
        for i in range(1, 7):
            tile = Image.open(f'assets/Food/Food{i}.png')
            self.food_sprite.append(pygame.image.fromstring(tile.convert("RGBA").tobytes(), tile.size, "RGBA"))

    def get_entity_sprite_at_frame(self, sprite, frame):
        return self.entity_sprite[sprite.name][frame]

    def get_num_frame_in_entity_sprite(self, sprite):
        return len(self.entity_sprite[sprite.name])

    def get_random_tile_sprite(self):
        return np.random.choice(self.tile_sprite, p=[0.05, 0.5, 0.05, 0.40])

    def get_tile_size(self):
        return self.tile_sprite[0].get_height()

    def get_random_food_index(self):
        return np.random.randint(0, len(self.food_sprite))

    def get_food_sprite(self, idx):
        return self.food_sprite[idx]
