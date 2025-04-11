import math

import pygame

from App import Window, ConditionManager, SpriteLoader, EntitySprite, Condition
from Utils import Position
import random
from typing import Optional


class Entity:
    def __init__(self, window: Window, sl: SpriteLoader, cm: ConditionManager):
        self.window = window
        self.sl = sl
        self.cm = cm


class MenuAgent(Entity):
    def __init__(self, window: Window, sl: SpriteLoader, cm: ConditionManager, sprite: EntitySprite,
                 sprite_scale: float, callback,
                 bound: tuple[tuple[int, int], tuple[int, int]] = None):
        super().__init__(window, sl, cm)

        self.bound_min = (0, 0)
        self.bound_max = (self.window.width, self.window.height)
        if bound is not None:
            self.bound_min = bound[0]
            self.bound_max = bound[1]

        self.sprite_scale = sprite_scale
        self.position = Position(self.bound_max[0] // 2, self.bound_max[1] // 2)
        self.speed = 2
        self.callback = callback

        # Sprite vars & font
        self.font1 = pygame.font.Font('assets/PressStart2P-Regular.ttf', 12)
        self.sprite = sprite
        self.current_frame = random.randint(0, self.sl.get_num_frame_in_entity_sprite(self.sprite) - 1)

        self._pick_direction()

    def move(self):
        # Move
        if (self.position.x <= self.bound_min[0]
                or self.position.x >= self.bound_max[0]
                or self.position.y <= self.bound_min[1]
                or self.position.y >= self.bound_max[1]):
            self._pick_direction()

        self.position.x += self.speed * self.direction[0]
        self.position.y += self.speed * self.direction[1]

        # Clamp to screen edge
        self.position.x = max(self.bound_min[0], min(self.bound_max[0], self.position.x))
        self.position.y = max(self.bound_min[1], min(self.bound_max[1], self.position.y))

    def render(self, events):
        # Sprite orientation
        current_sprite = self.sl.get_entity_sprite_at_frame(self.sprite, self.current_frame)
        current_sprite = pygame.transform.scale(current_sprite,
                                                (current_sprite.get_width() * self.sprite_scale,
                                                 current_sprite.get_height() * self.sprite_scale))
        if self.direction[0] < 0:
            current_sprite = pygame.transform.flip(current_sprite, True, False)

        # Size for translation
        sprite_width, sprite_height = current_sprite.get_size()

        # Check on-click
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                x, y = event.pos
                if (self.position.x - 20 <= x <= self.position.x + sprite_width + 20
                        and self.position.y - 20 <= y <= self.position.y + sprite_height + 20):
                    sp = list(EntitySprite)
                    index = (sp.index(self.sprite) + 1) % len(sp)
                    self.sprite = sp[index]
                    self.callback(self.sprite)

        # Text
        name_size = self.font1.size(self.sprite.value)
        name = self.font1.render(f'{self.sprite.value}', True, (0, 0, 0))

        # Render
        sprite_pos = (self.position.x - (sprite_width / 2), self.position.y - (sprite_height / 2))
        text_pos = (sprite_pos[0] + (sprite_width // 2) - (name_size[0] // 2), sprite_pos[1] + 60)
        self.window.screen.blit(current_sprite, sprite_pos)
        self.window.screen.blit(name, text_pos)

        # Clock tick
        if pygame.time.get_ticks() % 10 == 0:
            self.current_frame = pygame.time.get_ticks() % self.sl.get_num_frame_in_entity_sprite(self.sprite)

    def _pick_direction(self):
        angle = random.uniform(0, 2 * math.pi)
        self.direction = (math.cos(angle), math.sin(angle))


class Agent(Entity):
    def __init__(self, window: Window, sl: SpriteLoader, cm: ConditionManager, sprite: EntitySprite, agent_id: int,
                 speed: int = -1, size: int = -1, bound: tuple[tuple[int, int], tuple[int, int]] = None,
                 parent1: Optional["Agent"] = None, parent2: Optional["Agent"] = None):
        super().__init__(window, sl, cm)

        # Bound
        self.bound_min = (0, 0)
        self.bound_max = (self.window.width, self.window.height)
        if bound is not None:
            self.bound_min = bound[0]
            self.bound_max = bound[1]

        # Properties
        self.id = agent_id
        self.position = Position(self.bound_max[0] // 2, self.bound_max[1] // 2)

        self.size = round(size, 2)
        if size < 1:
            self.size = random.randint(20, 50)

        self.speed = round(speed, 2)
        if speed < 1:
            self.speed = round(1 / math.log(self.size, 10) * 4, 2)

        self.energy = 100
        self.color = (0, 0, 255)
        self.eaten = 0

        # Parents (Optional)
        self.parent1 = parent1
        self.parent2 = parent2

        # Sprite vars
        self.sprite = sprite
        self.current_frame = random.randint(0, self.sl.get_num_frame_in_entity_sprite(self.sprite) - 1)

        self.sprite_scale = self.size / 20

        self._pick_direction()

    def change_sprite(self, sprite):
        self.sprite = sprite

    def move(self, foods: list):
        if self.energy > 0:
            # Move
            if not len(foods) == 0:
                closest_food = foods[0]
                closest_dist = math.inf
                for food in foods:
                    dist = math.sqrt((self.position.x - food.position.x) ** 2 +
                                     (self.position.y - food.position.y) ** 2)
                    if dist < closest_dist:
                        closest_food = food
                        closest_dist = dist

                direction_x = closest_food.position.x - self.position.x
                direction_y = closest_food.position.y - self.position.y
                distance_to_food = (direction_x ** 2 + direction_y ** 2) ** 0.5

                speed_modifier = 1

                if self.cm.current == Condition.SNOW:
                    speed_modifier = 0.5

                if self.cm.current == Condition.WIND:
                    self.position.x += self.cm.direction[0] * 1.5
                    self.position.y += self.cm.direction[1] * 1.5

                if distance_to_food <= self.size:
                    # Normalize direction and move towards it
                    self.position.x += self.speed * speed_modifier * (direction_x / distance_to_food)
                    self.position.y += self.speed * speed_modifier * (direction_y / distance_to_food)
                else:
                    if (self.position.x <= self.bound_min[0]
                            or self.position.x >= self.bound_max[0]
                            or self.position.y <= self.bound_min[1]
                            or self.position.y >= self.bound_max[1] - 50):
                        self._pick_direction()

                    self.position.x += self.speed * speed_modifier * self.direction[0]
                    self.position.y += self.speed * speed_modifier * self.direction[1]

            # Clamp to screen edge
            self.position.x = max(self.bound_min[0], min(self.bound_max[0], self.position.x))
            self.position.y = max(self.bound_min[1], min(self.bound_max[1] - 50, self.position.y))

            # Cost to move
            speed_cost = 0.1 * self.speed
            size_cost = 0.00001 * self.size
            self.energy = self.energy - speed_cost - size_cost

            return True

        return False

    def render(self):
        # Sprite orientation
        current_sprite = self.sl.get_entity_sprite_at_frame(self.sprite, self.current_frame)
        current_sprite = pygame.transform.scale(current_sprite,
                                                (current_sprite.get_width() * self.sprite_scale,
                                                 current_sprite.get_height() * self.sprite_scale))
        if self.direction[0] < 0:
            current_sprite = pygame.transform.flip(current_sprite, True, False)

        # Size for translation
        sprite_width, sprite_height = current_sprite.get_size()

        # Render
        self.window.screen.blit(current_sprite,
                                (self.position.x - (sprite_width / 2), self.position.y - (sprite_height / 2)))

        circle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(circle_surface, (180, 0, 0) + (int((self.energy / 100) * 255),),
                           (self.size, self.size), self.size, width=2)
        self.window.screen.blit(circle_surface, (self.position.x - self.size, self.position.y - self.size))

        # Clock tick
        if pygame.time.get_ticks() % 10 == 0:
            self.current_frame = pygame.time.get_ticks() % self.sl.get_num_frame_in_entity_sprite(self.sprite)

    def _pick_direction(self):
        angle = random.uniform(0, 2 * math.pi)
        self.direction = (math.cos(angle), math.sin(angle))


class Food(Entity):
    def __init__(self, window: Window, sl: SpriteLoader, cm: ConditionManager):
        super().__init__(window, sl, cm)
        self.size = 6
        self.position = Position(random.randint(8, self.window.width - 8), random.randint(8, self.window.height - 58))
        self.sprite_idx = sl.get_random_food_index()

    def render(self):
        sprite = self.sl.get_food_sprite(self.sprite_idx)
        sprite_width, sprite_height = sprite.get_size()
        self.window.screen.blit(sprite, (self.position.x - (sprite_width // 2), self.position.y - (sprite_height // 2)))
