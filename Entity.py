import math

from Utils import Position
from App import Window
import random
from SpriteProcessor import *


class Entity:
    def __init__(self, window: Window, sl: SpriteLoader):
        self.window = window
        self.sl = sl


class MenuAgent(Entity):
    def __init__(self, window: Window, sl: SpriteLoader, sprite: EntitySprite, sprite_scale: float, callback,
                 bound: tuple[tuple[int, int], tuple[int, int]] = None):
        super().__init__(window, sl)

        self.bound_min = (0, 0)
        self.bound_max = (self.window.width, self.window.height)
        if bound is not None:
            self.bound_min = bound[0]
            self.bound_max = bound[1]

        self.sprite_scale = sprite_scale
        self.position = Position(self.bound_max[0] // 2, self.bound_max[1] // 2)

        self.speed = 2
        self.callback = callback

        # Sprite vars
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

    def draw(self, events):
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

        # Render
        self.window.screen.blit(current_sprite,
                                (self.position.x - (sprite_width / 2), self.position.y - (sprite_height / 2)))

        # Clock tick
        if pygame.time.get_ticks() % 10 == 0:
            self.current_frame = pygame.time.get_ticks() % self.sl.get_num_frame_in_entity_sprite(self.sprite)

    def _pick_direction(self):
        angle = random.uniform(0, 2 * math.pi)
        self.direction = (math.cos(angle), math.sin(angle))


class Agent(Entity):
    def __init__(self, window: Window, sl: SpriteLoader, sprite: EntitySprite, speed: int = -1, size: int = -1,
                 bound: tuple[tuple[int, int], tuple[int, int]] = None):
        super().__init__(window, sl)

        self.bound_min = (0, 0)
        self.bound_max = (self.window.width, self.window.height)
        if bound is not None:
            self.bound_min = bound[0]
            self.bound_max = bound[1]

        self.position = Position(self.bound_max[0] // 2, self.bound_max[1] // 2)

        self.size = round(size, 2)
        if size < 1:
            self.size = random.randint(20, 50)

        self.speed = round(speed, 2)
        if speed < 1:
            self.speed = round(1 / math.log(self.size, 10) * 3, 2)

        self.energy = 100
        self.color = (0, 0, 255)
        self.eaten = 0

        # Sprite vars
        self.sprite = sprite
        self.current_frame = random.randint(0, self.sl.get_num_frame_in_entity_sprite(self.sprite) - 1)

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

                if distance_to_food <= self.size:
                    # Normalize direction and move towards it
                    self.position.x += self.speed * (direction_x / distance_to_food)
                    self.position.y += self.speed * (direction_y / distance_to_food)
                else:
                    if (self.position.x <= self.bound_min[0]
                            or self.position.x >= self.bound_max[0]
                            or self.position.y <= self.bound_min[1]
                            or self.position.y >= self.bound_max[1] - 50):
                        self._pick_direction()

                    self.position.x += self.speed * self.direction[0]
                    self.position.y += self.speed * self.direction[1]

            # Clamp to screen edge
            self.position.x = max(self.bound_min[0], min(self.bound_max[0], self.position.x))
            self.position.y = max(self.bound_min[1], min(self.bound_max[1] - 50, self.position.y))

            # Cost to move
            speed_cost = 0.1 * self.speed
            size_cost = 0.00001 * self.size
            self.energy = self.energy - speed_cost - size_cost

            return True

        return False

    def draw(self):
        # Sprite orientation
        current_sprite = self.sl.get_entity_sprite_at_frame(self.sprite, self.current_frame)
        if self.direction[0] < 0:
            current_sprite = pygame.transform.flip(current_sprite, True, False)

        # Size for translation
        sprite_width, sprite_height = current_sprite.get_size()

        # Render
        self.window.screen.blit(current_sprite,
                                (self.position.x - (sprite_width / 2), self.position.y - (sprite_height / 2)))
        pygame.draw.circle(self.window.screen, (180, 0, 0), (self.position.x, self.position.y), self.size, width=2)

        # Clock tick
        if pygame.time.get_ticks() % 10 == 0:
            self.current_frame = pygame.time.get_ticks() % self.sl.get_num_frame_in_entity_sprite(self.sprite)

    def _pick_direction(self):
        angle = random.uniform(0, 2 * math.pi)
        self.direction = (math.cos(angle), math.sin(angle))


class Food(Entity):
    def __init__(self, window: Window, sl: SpriteLoader):
        super().__init__(window, sl)
        self.size = 6
        self.position = Position(random.randint(8, self.window.width - 8), random.randint(8, self.window.height - 58))
        self.sprite_idx = sl.get_random_food_index()

    def draw(self):
        sprite = self.sl.get_food_sprite(self.sprite_idx)
        sprite_width, sprite_height = sprite.get_size()
        self.window.screen.blit(sprite, (self.position.x - (sprite_width // 2), self.position.y - (sprite_height // 2)))
