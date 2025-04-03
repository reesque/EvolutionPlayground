import math

from tabulate import tabulate
from App import Window
from Entity import Agent, Food
from SpriteProcessor import *
import random

from UIElement import *


class GameState(Enum):
    MAIN_MENU = 0
    GAME_OVER = 1
    SIM_RUNNING = 2
    SIM_PAUSED = 3
    GENERATION_SHIFT = 4

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
        self.foods = [Food(self.window, self.sl) for _ in range(self.initial_food_amount)]
        self.max_offspring = 4

        self.sim_state = 1
        self.ui_parent1, self.ui_parent2 = None, None
        self.ui_offspring_confirmed = False
        self.is_auto = False

        # UI Elements
        self.ui_pause_box = PauseBox(self.window)
        self.ui_sim_bar = SimulationInformation(self.window)
        self.ui_agent_card = ParentsSelection(self.window, self.sl)
        self.ui_offspring_card = Offspring(self.window, self.sl)

        self.run()
        pygame.quit()

    def run_simulation(self, is_paused: bool):
        agents_moved = 0

        if len(self.foods) == 0:
            return True

        # Update agents
        for agent in self.agents:
            if not is_paused and agent.move(self.foods.copy()):
                agents_moved = agents_moved + 1

            agent.draw()

        # Food be eaten
        if not is_paused:
            for agent in self.agents:
                for food in self.foods.copy():
                    # Euclidean dist
                    dist = math.sqrt((agent.position.x - food.position.x) ** 2 +
                                     (agent.position.y - food.position.y) ** 2)

                    if dist <= (food.size / 2):
                        agent.eaten = agent.eaten + 1
                        self.foods.remove(food)
                        break

        # Update Food
        for food in self.foods:
            food.draw()

        # Termination if all out of energy
        if agents_moved == 0 and not is_paused:
            return True

        return False

    def blend_crossover(self, parent1: Agent, parent2: Agent):
        alpha = random.uniform(0.3, 0.7)
        child_speed = alpha * parent1.speed + (1 - alpha) * parent2.speed
        child_size = alpha * parent1.size + (1 - alpha) * parent2.size
        return Agent(self.window, self.sl, self.sprite, speed=child_speed, size=child_size)

    def mutate(self, agent: Agent, mutation_rate: float = 0.1, mutation_strength: float = 0.5):
        speed_mutation = 0
        size_mutation = 0
        mutated = random.random() < mutation_rate
        if mutated:
            speed_mutation = random.uniform(-mutation_strength, mutation_strength)
            size_mutation = random.uniform(-mutation_strength, mutation_strength)
            agent.speed += speed_mutation
            agent.size += size_mutation

        return mutated, speed_mutation, size_mutation

    def child_policy_distribution(self, fitness, scale_factor=3):
        child_choices = np.linspace(1, self.max_offspring, self.max_offspring, dtype=int)

        distances = np.abs(child_choices - fitness / (self.max_offspring + 1))
        weights = np.exp(-distances)
        probabilities = weights / np.sum(weights)

        return child_choices, probabilities

    def reset(self):
        self.agents = [Agent(self.window, self.sl, self.sprite) for _ in range(self.initial_population)]
        self.foods = [Food(self.window, self.sl) for _ in range(self.initial_food_amount)]

    def choose_parents_callback(self, p1: Agent, p2: Agent, is_auto: bool):
        self.ui_parent1, self.ui_parent2 = p1, p2
        self.is_auto = is_auto

    def offspring_confirm_callback(self):
        self.ui_offspring_confirmed = True

    def next_generation(self):
        i = 0
        while i < len(self.agents):
            # Check if agent is fit enough
            if self.agents[i].eaten == 0:
                self.agents.pop(i)
                continue

            i += 1

        # Species died out
        if len(self.agents) == 0:
            self.sim_state = 2
            self.reset()
            return

        # Child policy
        agents_copy = self.agents.copy()
        self.agents = []
        while len(agents_copy) > 1:
            if not self.is_auto:
                card_choices = np.random.choice(agents_copy, min(len(agents_copy), 4), replace=False).tolist()
                self.ui_agent_card.reset()
                self.ui_parent1, self.ui_parent2 = None, None

                while self.ui_parent1 is None or self.ui_parent2 is None:
                    self.window.clear()
                    self.ui_agent_card.render(card_choices, self.choose_parents_callback)
                    self.window.tick()

                agents_copy.remove(self.ui_parent1)
                agents_copy.remove(self.ui_parent2)
            else:
                self.ui_parent1 = np.random.choice(agents_copy)
                agents_copy.remove(self.ui_parent1)
                self.ui_parent2 = np.random.choice(agents_copy)
                agents_copy.remove(self.ui_parent2)

            child_choices, child_policy = self.child_policy_distribution(self.ui_parent1.eaten + self.ui_parent2.eaten)
            offsprings = []
            for _ in range(np.random.choice(child_choices, p=child_policy)):
                child = self.blend_crossover(self.ui_parent1, self.ui_parent2)
                mutated, speed_mutation, size_mutation = self.mutate(child)
                offsprings.append((child, mutated, speed_mutation, size_mutation))
                self.agents.append(child)

            if not self.is_auto:
                self.ui_offspring_confirmed = False
                while not self.ui_offspring_confirmed:
                    self.window.clear()
                    self.ui_offspring_card.render(offsprings, self.offspring_confirm_callback)
                    self.window.tick()

        # Spawn new food
        food_replenish_count = (self.initial_food_amount  * self.food_replenish_const /
                                (max(1, len(self.agents) - self.food_replenish_const)))
        food_replenish_count *= random.uniform(0.9, 1.1)

        for _ in range(int(food_replenish_count)):
            self.foods.append(Food(self.window, self.sl))

        self.sim_state = 1
        self.is_auto = False

    def run(self):
        gen = 0
        running = True

        # Main loop
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    if event.key == pygame.K_SPACE:
                        if self.sim_state == 1:
                            self.sim_state = 2
                        elif self.sim_state == 2:
                            self.sim_state = 1

            if self.sim_state == 0 and not gen == 0:
                self.next_generation()

            if self.sim_state == 1 or self.sim_state == 2:
                self.window.clear()
                done = self.run_simulation(self.sim_state == 2)

                if self.sim_state == 2:
                    self.ui_pause_box.render()

                if done:
                    self.sim_state = 0
                    gen += 1

                self.ui_sim_bar.render(gen, len(self.agents), len(self.foods))

            self.window.tick()


if __name__ == "__main__":
    Simulation()
