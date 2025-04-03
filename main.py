import math

import numpy as np
from tabulate import tabulate
from App import Window
from Entity import Agent, Food
from SpriteProcessor import *
import random


class Simulation:
    def __init__(self):
        # Backend services
        self.sl = SpriteLoader()

        # Initialize Pygame
        pygame.init()
        self.window = Window(self.sl)

        # Params
        self.initial_food_amount = 100
        self.initial_population = 10
        self.food_replenish_const = 1

        self.sprite = EntitySprite.SHEEP
        self.agents = [Agent(self.window, self.sl, self.sprite) for _ in range(self.initial_population)]
        self.max_offspring = 3

        self.run()
        pygame.quit()

    def generate_report(self, generation: int):
        print("Generation {} Report:".format(generation))
        headers = ["Size", "Speed", "Fitness"]
        data = []
        for agent in self.agents:
            data.append([agent.size, agent.speed, agent.eaten])

        print(tabulate(data, headers=headers))

    def run_simulation(self, generation: int, food_list: list):
        running = True
        while running:
            agents_moved = 0
            if len(food_list) == 0:
                running = False
                #self.generate_report(generation)
                self.window.clear()

            self.window.clear()

            # Update agents
            for agent in self.agents:
                if agent.move(food_list.copy()):
                    agents_moved = agents_moved + 1

                agent.draw()

            # Food be eaten
            for agent in self.agents:
                for food in food_list.copy():
                    # Euclidean dist
                    dist = math.sqrt((agent.position.x - food.position.x) ** 2 +
                                     (agent.position.y - food.position.y) ** 2)

                    if dist <= (food.size / 2):
                        agent.eaten = agent.eaten + 1
                        food_list.remove(food)
                        break

            # Update Food
            for food in food_list:
                food.draw()

            # Termination if all out of energy
            if agents_moved == 0:
                running = False
                #self.generate_report(generation)
                self.window.clear()

            self.window.tick()

    def blend_crossover(self, parent1: Agent, parent2: Agent):
        alpha = random.uniform(0.3, 0.7)
        child_speed = alpha * parent1.speed + (1 - alpha) * parent2.speed
        child_size = alpha * parent1.size + (1 - alpha) * parent2.size
        return Agent(self.window, self.sl, self.sprite, speed=child_speed, size=child_size)

    def mutate(self, agent: Agent, mutation_rate: float = 0.1, mutation_strength: float = 0.5):
        if random.random() < mutation_rate:
            agent.speed += random.uniform(-mutation_strength, mutation_strength)
            agent.size += random.uniform(-mutation_strength, mutation_strength)

    def child_policy_distribution(self, fitness, scale_factor=1.5):
        child_choices = np.linspace(0, self.max_offspring, self.max_offspring, dtype=int)
        scaled_weights = np.exp(scale_factor * (fitness / np.max([fitness, 1])) * child_choices)
        probabilities = scaled_weights / np.sum(scaled_weights)

        return child_choices, probabilities

    def run(self):
        foods = [Food(self.window, self.sl) for _ in range(self.initial_food_amount)]
        gen = 0
        while True:
            if not gen == 0:
                i = 0
                while i < len(self.agents):
                    # Check if agent is fit enough
                    if self.agents[i].eaten == 0:
                        self.agents.pop(i)
                        continue

                    i += 1

                # Species died out
                if len(self.agents) == 0:
                    break

                # Child policy
                agents_copy = self.agents.copy()
                self.agents = []
                while len(agents_copy) > 1:
                    parent1 = np.random.choice(agents_copy)
                    agents_copy.remove(parent1)
                    parent2 = np.random.choice(agents_copy)
                    agents_copy.remove(parent2)

                    child_choices, child_policy = self.child_policy_distribution(parent1.eaten + parent2.eaten)
                    for _ in range(np.random.choice(child_choices, p=child_policy)):
                        child = self.blend_crossover(parent1, parent2)
                        self.mutate(child)
                        self.agents.append(child)

                # Spawn new food
                food_replenish_count = (self.initial_food_amount * self.food_replenish_const /
                                        (max(1, len(self.agents) - self.food_replenish_const)))
                food_replenish_count *= random.uniform(0.9, 1.1)
                print(food_replenish_count)

                for _ in range(int(food_replenish_count)):
                    foods.append(Food(self.window, self.sl))

            self.run_simulation(gen, foods)
            gen += 1


if __name__ == "__main__":
    Simulation()
