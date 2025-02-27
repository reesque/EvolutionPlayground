import math
import random

from tabulate import tabulate
import pygame
from App import Window
from Entity import Agent, Food

# Initialize Pygame
pygame.init()
window = Window()

# Params
generations = 10
food_amount = 100
population = 10

agents = [Agent(window) for _ in range(population)]


def generate_report(generation: int):
    print("Generation {} Report:".format(generation))
    headers = ["Size", "Speed", "Fitness"]
    data = []
    for agent in agents:
        data.append([agent.size, agent.speed, agent.eaten])

    print(tabulate(data, headers=headers))


def run_simulation(generation: int, foods: list):
    running = True
    while running:
        agents_moved = 0
        if len(foods) == 0:
            generate_report(generation)
            window.clear()
            break

        window.clear()

        # Update agents
        for agent in agents:
            if agent.move(foods.copy()):
                agents_moved = agents_moved + 1

            agent.draw()

        # Food be eaten
        for agent in agents:
            for food in foods.copy():
                # Euclidean dist
                dist = math.sqrt((agent.position.x - food.position.x) ** 2 +
                                 (agent.position.y - food.position.y) ** 2)

                if dist <= (food.size / 2):
                    agent.eaten = agent.eaten + 1
                    foods.remove(food)
                    break

        # Update Food
        for food in foods:
            food.draw()

        # Termination if all out of energy
        if agents_moved == 0:
            generate_report(generation)
            window.clear()
            break

        window.tick()


def parent_selection():
    total_fitness = sum(agent.eaten for agent in agents)
    pick = random.uniform(0, total_fitness)

    current = 0
    for agent in agents:
        current += agent.eaten
        if current >= pick:
            return agent


def blend_crossover(parent1: Agent, parent2: Agent):
    alpha = random.uniform(0.3, 0.7)
    child_speed = alpha * parent1.speed + (1 - alpha) * parent2.speed
    child_size = alpha * parent1.size + (1 - alpha) * parent2.size
    return Agent(window, speed=child_speed, size=child_size)


def mutate(agent: Agent, mutation_rate: float = 0.1, mutation_strength: float = 0.5):
    if random.random() < mutation_rate:
        agent.speed += random.uniform(-mutation_strength, mutation_strength)
        agent.size += random.uniform(-mutation_strength, mutation_strength)


for gen in range(generations):
    if not gen == 0:
        offspring = []

        major = math.floor(population * 0.8)
        minor = population - major

        for _ in range(major):
            parent1 = parent_selection()
            parent2 = parent_selection()
            child = blend_crossover(parent1, parent2)
            mutate(child)
            offspring.append(child)

        for _ in range(minor):
            offspring.append(Agent(window))

        agents = offspring

    foods = [Food(window) for _ in range(food_amount)]
    run_simulation(gen, foods)

pygame.quit()
