import math

from Utils import Position
from App import Window
import random
import pygame


class Entity:
    def __init__(self, window: Window):
        self.window = window


class Agent(Entity):
    def __init__(self, window: Window, speed: int = -1, size: int = -1):
        super().__init__(window)
        self.position = Position(self.window.width // 2, self.window.height // 2)

        self.size = round(size, 2)
        if size < 1:
            self.size = random.randint(5, 30)

        self.speed = round(speed, 2)
        if speed < 1:
            self.speed = round(1/math.log(self.size, 10) * 2, 2)

        self.energy = 100
        self.color = (0, 0, 255)
        self.eaten = 0

    def move(self, foods: list):
        if self.energy > 0:
            # Move
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
                self.position.x += self.speed * random.randint(-1, 1)
                self.position.y += self.speed * random.randint(-1, 1)

            # Clamp to screen edge
            self.position.x = max(self.size, min(self.window.width - self.size, self.position.x))
            self.position.y = max(self.size, min(self.window.height - self.size, self.position.y))

            # Cost to move
            speed_cost = 0.1*self.speed
            size_cost = 0.00001*self.size
            self.energy = self.energy - speed_cost - size_cost

            return True

        return False

    def draw(self):
        pygame.draw.circle(self.window.screen, self.color, (self.position.x, self.position.y), 4)
        pygame.draw.circle(self.window.screen, (255, 0, 0), (self.position.x, self.position.y), self.size, width=2)


class Food(Entity):
    def __init__(self, window: Window):
        super().__init__(window)
        self.size = 4
        self.position = Position(random.randint(8, self.window.width - 8), random.randint(8, self.window.height - 8))
        self.color = (255, 255, 255)

    def draw(self):
        pygame.draw.circle(self.window.screen, self.color, (self.position.x, self.position.y), self.size)