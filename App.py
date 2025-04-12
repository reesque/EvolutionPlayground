import math

import numpy as np
import pygame

import random
from enum import Enum
from PIL import Image, ImageSequence


class GameState(Enum):
    MAIN_MENU = 0
    GAME_END_EVAL = 1
    SIM_RUNNING = 2
    SIM_PAUSED = 3
    GENERATION_EVAL = 4
    PARENTS_SELECTION = 5
    OFFSPRING_OVERVIEW = 6
    CONDITION_OVERVIEW = 7
    AGENT_TREE = 8


class EntitySprite(Enum):
    CHICKEN = 'Chicken'
    CRAB = 'Crab'
    TOAD = 'Toad'
    PIG = 'Pig'
    GOOSE = 'Goose'
    FROG = 'Frog'
    BOAR = 'Boar'
    CAT = 'Cat'
    SHEEP = 'Sheep'
    TURTLE = 'Turtle'
    FOX = 'Fox'
    PORCUPINE = 'Porcupine'
    SKUNK = 'Skunk'
    WOLF = 'Wolf'

    def get_path(self):
        return f"{self.name.capitalize()}.gif"


class TileType(Enum):
    GRASS = (72, 156, 76)
    SNOW = (230, 228, 228)
    DRY = (202, 179, 88)
    WET = (50, 118, 53)


class Condition(Enum):
    NONE = ('None', None, TileType.GRASS)
    WIND = ('Wind', 'A strong gust of wind is travelling through the region. '
                    'Movement is pushed slightly to one direction', TileType.GRASS)
    SNOW = ('Snow', 'The white snow has started to fall from the sky. '
                    'Movement in the region is more limited', TileType.SNOW)
    DROUGHT = ('Drought', 'The region is exposed to a prolonged dry weather condition. '
                          'Food abundancy is reduced', TileType.DRY)
    RAIN = ('Rain', 'The heavy rain inside the region has stimulated the growth of plants. '
                    'Food has massively replenished', TileType.GRASS)

    def __init__(self, label, desc, tile_type):
        self.label = label
        self.desc = desc
        self.tile_type = tile_type

    def get_path(self):
        return f"{self.name.capitalize()}.png"

    @staticmethod
    def get_probability():
        return [0.65, 0.1, 0.1, 0.1, 0.05]


class ConditionManager:
    def __init__(self):
        self.current = Condition.NONE

        # Only applicable for Wind
        self.direction = (0, 0)

    def __call__(self, *args, **kwargs):
        self.current = np.random.choice(list(Condition), p=Condition.get_probability())

        if self.current == Condition.WIND:
            self._pick_direction()
        else:
            self.direction = (0, 0)

    def reset(self):
        self.current = Condition.NONE
        self.direction = (0, 0)

    def _pick_direction(self):
        angle = random.uniform(0, 2 * math.pi)
        self.direction = (math.cos(angle), math.sin(angle))


class IDGenerator:
    def __init__(self):
        self.max_id = 0
        self.next = []
        self.reset()

    def __call__(self, *args, **kwargs):
        if len(self.next) == 0:
            self.next = list(range(self.max_id, self.max_id * 10))
            random.shuffle(self.next)
            self.max_id *= 10

        return self.next.pop()

    def reset(self):
        self.max_id = 100
        self.next = list(range(0, self.max_id))
        random.shuffle(self.next)


class SpriteLoader:
    def __init__(self):
        # Entity
        self.entity_sprite = {}

        for _, item in enumerate(EntitySprite):
            gif = Image.open(f'assets/Entity/{item.get_path()}')

            frames = [pygame.image.frombytes(frame.convert("RGBA").tobytes(), frame.size, "RGBA")
                      for frame in ImageSequence.Iterator(gif)]

            self.entity_sprite[item.name] = frames

        # Tile
        self.tile_sprite = []
        for i in range(1, 5):
            tile = Image.open(f'assets/Tile/Tile{i}.png')
            self.tile_sprite.append(pygame.image.frombytes(tile.convert("RGBA").tobytes(), tile.size, "RGBA"))

        # Food
        self.food_sprite = []
        for i in range(1, 7):
            food = Image.open(f'assets/Food/Food{i}.png')
            self.food_sprite.append(pygame.image.frombytes(food.convert("RGBA").tobytes(), food.size, "RGBA"))

        # Condition
        self.condition_sprite = {}
        for _, item in enumerate(Condition):
            if item == Condition.NONE:
                continue

            sheet = Image.open(f"assets/Condition/{item.get_path()}").convert("RGBA")

            tile_width, tile_height = 16, 16
            sheet_width, sheet_height = sheet.size
            num_frames = sheet_height // tile_height

            frames = []
            for i in range(num_frames):
                # Crop a 16x16 tile from each vertical position
                frame = sheet.crop((0, i * tile_height, tile_width, (i + 1) * tile_height))
                surface = pygame.image.frombytes(frame.tobytes(), frame.size, "RGBA")
                frames.append(surface.copy())

            self.condition_sprite[item.name] = frames

    def get_condition_sprite_at_frame(self, sprite, frame):
        frame = min(len(self.condition_sprite[sprite.name]) - 1, max(frame, 0))
        return self.condition_sprite[sprite.name][frame]

    def get_num_frame_in_condition_sprite(self, sprite):
        return len(self.condition_sprite[sprite.name])

    def get_entity_sprite_at_frame(self, sprite, frame):
        frame = min(len(self.entity_sprite[sprite.name]) - 1, max(frame, 0))
        return self.entity_sprite[sprite.name][frame]

    def get_num_frame_in_entity_sprite(self, sprite):
        return len(self.entity_sprite[sprite.name])

    def get_random_tile_index(self):
        return np.random.choice([0, 1, 2, 3], p=[0.05, 0.5, 0.05, 0.40])

    def get_tile_size(self):
        return self.tile_sprite[0].get_height()

    def get_tile_at(self, idx: int):
        return self.tile_sprite[idx]

    def get_random_food_index(self):
        return np.random.randint(0, len(self.food_sprite))

    def get_food_sprite(self, idx):
        return self.food_sprite[idx]


class Window:
    def __init__(self, sl: SpriteLoader, cm: ConditionManager, fps: int = 60):
        self.width = 1000
        self.height = 600
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.sl = sl
        self.cm = cm

        self.screen = pygame.display.set_mode((self.width, self.height), pygame.SCALED | pygame.HWACCEL)
        pygame.display.set_caption("Evolution Playground")

        self.tile_ground = []
        for x in range(0, self.width, self.sl.get_tile_size()):
            row = []
            for y in range(0, self.height, self.sl.get_tile_size()):
                row.append((self.sl.get_random_tile_index(), x, y))
            self.tile_ground.append(row)

        self.clear()

    def clear(self):
        self.screen.fill(self.cm.current.tile_type.value)

        for i in range(len(self.tile_ground)):
            for j in range(len(self.tile_ground[0])):
                idx, x, y = self.tile_ground[i][j]
                sprite = self.sl.get_tile_at(idx)
                self.screen.blit(sprite, (x, y))

    def tick(self):
        pygame.display.flip()
        self.clock.tick(self.fps)
