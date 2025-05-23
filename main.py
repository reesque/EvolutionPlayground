import math

from App import IDGenerator, GameState
from Entity import Food
from UIElement import *


class Simulation:
    def __init__(self):
        # Backend services
        self.sl = SpriteLoader()
        self.idg = IDGenerator()
        self.cm = ConditionManager()

        # Initialize Pygame
        pygame.init()
        self.window = Window(self.sl, self.cm)

        # Params
        self.initial_food_amount = 100
        self.initial_population = 10
        self.food_replenish_const = 1
        self.mutation_chance = 0.1
        self.mutation_strength = 0.5
        self.max_offspring = 4

        # Game states
        self.game_state = GameState.MAIN_MENU
        self.ui_parent1, self.ui_parent2 = None, None
        self.ui_offspring_confirmed = False
        self.is_auto = False
        self.generation = 0
        self.prev_gen = None
        self.offsprings = None
        self.card_choices = None
        self.sprite = EntitySprite.CHICKEN
        self.agents = [Agent(self.window, self.sl, self.cm,
                             self.sprite, self.idg(), self.generation) for _ in range(self.initial_population)]
        self.foods = [Food(self.window, self.sl, self.cm) for _ in range(self.initial_food_amount)]

        # UI Elements
        self.ui_pause_box = PauseBox(self.window)
        self.ui_sim_bar = SimulationInformation(self.window, self.ui_callback_back_to_menu)
        self.ui_agent_card = ParentsSelection(self.window, self.sl)
        self.ui_offspring_card = Offspring(self.window, self.sl)
        self.ui_condition_card = ConditionOverview(self.window, self.sl)
        self.ui_main_menu = MainMenu(self.window, self.sl, self.cm, self.ui_callback_init_population_changed,
                                     self.ui_callback_init_food_changed, self.ui_callback_sprite_changed,
                                     self.ui_callback_game_reset, self.ui_callback_mutation_chance_changed,
                                     self.ui_callback_mutation_strength_changed)
        self.ui_game_over = GameOver(self.window, self.ui_callback_back_to_menu)
        self.ui_agent_inspect = None

        self.run()
        pygame.quit()

    def run_simulation(self, events, is_paused: bool):
        agents_moved = 0

        if len(self.foods) == 0:
            return True

        # Update agents
        for agent in self.agents:
            if not is_paused and agent.move(self.foods.copy()):
                agents_moved = agents_moved + 1

            agent.render(events, self.ui_callback_inspect_called)

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
            food.render()

        # Termination if all out of energy
        if agents_moved == 0 and not is_paused:
            return True

        return False

    def blend_crossover(self, parent1: Agent, parent2: Agent):
        alpha = random.uniform(0.3, 0.7)
        child_speed = alpha * parent1.speed + (1 - alpha) * parent2.speed
        child_size = alpha * parent1.size + (1 - alpha) * parent2.size
        return Agent(self.window, self.sl, self.cm, self.sprite, self.idg(), self.generation,
                     speed=child_speed, size=child_size, parent1=parent1, parent2=parent2)

    def mutate(self, agent: Agent):
        speed_mutation = 0
        size_mutation = 0
        mutated = random.random() < self.mutation_chance
        if mutated:
            speed_mutation = round(random.uniform(-self.mutation_strength, self.mutation_strength), 2)
            size_mutation = round(random.uniform(-self.mutation_strength, self.mutation_strength), 2)
            agent.speed += speed_mutation
            agent.size += size_mutation

            agent.mutated = True
            agent.mutation_speed_offset = speed_mutation
            agent.mutation_size_offset = size_mutation

        return mutated, speed_mutation, size_mutation

    def child_policy_distribution(self, fitness):
        child_choices = np.linspace(1, self.max_offspring, self.max_offspring, dtype=int)

        distances = np.abs(child_choices - fitness / (self.max_offspring + 1))
        weights = np.exp(-distances)
        probabilities = weights / np.sum(weights)

        return child_choices, probabilities

    def next_generation(self, events):
        if len(self.prev_gen) > 1:
            # Child policy
            if not self.is_auto:
                if self.card_choices is None:
                    self.card_choices = np.random.choice(self.prev_gen, min(len(self.prev_gen), 4), replace=False).tolist()
                    self.ui_parent1, self.ui_parent2 = None, None

                if self.ui_parent1 is None or self.ui_parent2 is None:
                    self.window.clear()
                    self.ui_agent_card.render(self.card_choices, events, self.ui_callback_parents_chose)
                    self.window.tick()
            else:
                self.ui_parent1 = np.random.choice(self.prev_gen)
                self.ui_parent2 = np.random.choice(self.prev_gen)

            if self.ui_parent1 is not None and self.ui_parent2 is not None:
                child_choices, child_policy = self.child_policy_distribution(self.ui_parent1.eaten + self.ui_parent2.eaten)
                self.offsprings = []
                for _ in range(np.random.choice(child_choices, p=child_policy)):
                    child = self.blend_crossover(self.ui_parent1, self.ui_parent2)
                    mutated, speed_mutation, size_mutation = self.mutate(child)
                    self.offsprings.append((child, mutated, speed_mutation, size_mutation))
                    self.agents.append(child)

                if self.ui_parent1 in self.prev_gen:
                    self.prev_gen.remove(self.ui_parent1)

                if self.ui_parent2 in self.prev_gen:
                    self.prev_gen.remove(self.ui_parent2)

                self.ui_parent1, self.ui_parent2 = None, None

                self.ui_offspring_confirmed = False
                self.game_state = GameState.OFFSPRING_OVERVIEW
        else:
            # Spawn new food
            replenish_const = self.food_replenish_const
            if self.cm.current == Condition.RAIN:
                replenish_const *= 3

            food_replenish_count = (self.initial_food_amount * replenish_const /
                                    (max(1, len(self.agents) - self.food_replenish_const)))
            food_replenish_count *= random.uniform(0.9, 1.1)

            for _ in range(int(food_replenish_count)):
                self.foods.append(Food(self.window, self.sl, self.cm))

            if self.cm.current == Condition.DROUGHT:
                random.shuffle(self.foods)
                self.foods = self.foods[0:len(self.foods) // 3]

            self.game_state = GameState.SIM_RUNNING
            self.is_auto = False

    def generation_eval(self):
        i = 0
        while i < len(self.agents):
            # Check if agent is fit enough
            if self.agents[i].eaten == 0:
                self.agents.pop(i)
                continue

            i += 1

        self.prev_gen = self.agents.copy()
        self.agents = []
        self.cm()
        self.game_state = GameState.GAME_END_EVAL

    def run(self):
        # Main loop
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                elif event.type == pygame.KEYDOWN:
                    #if event.key == pygame.K_ESCAPE:
                    #    pygame.quit()
                    #    return

                    if event.key == pygame.K_SPACE:
                        if self.game_state == GameState.SIM_RUNNING:
                            self.game_state = GameState.SIM_PAUSED
                        elif self.game_state == GameState.SIM_PAUSED:
                            self.game_state = GameState.SIM_RUNNING

            if self.game_state == GameState.MAIN_MENU:
                self.window.clear()
                self.ui_main_menu.render(events)
                self.window.tick()

            elif self.game_state == GameState.GENERATION_EVAL:
                self.generation_eval()

            elif self.game_state == GameState.CONDITION_OVERVIEW:
                self.window.clear()
                self.ui_condition_card.render(self.cm.current, events, self.ui_callback_condition_confirmed)
                self.window.tick()

            elif self.game_state == GameState.PARENTS_SELECTION:
                self.next_generation(events)

            elif self.game_state == GameState.OFFSPRING_OVERVIEW:
                if not self.is_auto:
                    if not self.ui_offspring_confirmed:
                        self.window.clear()
                        self.ui_offspring_card.render(self.offsprings, events, self.ui_callback_offspring_confirmed)
                        self.window.tick()
                    else:
                        self.game_state = GameState.PARENTS_SELECTION
                else:
                    self.game_state = GameState.PARENTS_SELECTION

            elif self.game_state == GameState.GAME_END_EVAL:
                if len(self.agents) >= 2 or len(self.prev_gen) >= 2:
                    self.game_state = GameState.CONDITION_OVERVIEW
                    continue

                self.window.clear()
                self.ui_game_over.render(events, self.generation)
                self.window.tick()

            elif self.game_state == GameState.AGENT_TREE:
                self.window.clear()
                self.ui_agent_inspect.render(events, self.ui_callback_inspect_confirm, self.ui_callback_inspect_called)
                self.window.tick()

            elif self.game_state == GameState.SIM_RUNNING or self.game_state == GameState.SIM_PAUSED:
                self.window.clear()
                done = self.run_simulation(events, self.game_state == GameState.SIM_PAUSED)

                if self.game_state == GameState.SIM_PAUSED:
                    self.ui_pause_box.render()

                if done:
                    self.game_state = GameState.GENERATION_EVAL
                    self.generation += 1
                    continue

                self.ui_sim_bar.render(events, self.generation, len(self.agents), len(self.foods))
                self.window.tick()

    def reset(self):
        self.generation = 0
        self.prev_gen = []
        self.offsprings = []
        self.idg.reset()
        self.cm.reset()
        self.ui_agent_inspect = None
        self.agents = [Agent(self.window, self.sl, self.cm,
                             self.sprite, self.idg(), self.generation) for _ in range(self.initial_population)]
        self.foods = [Food(self.window, self.sl, self.cm) for _ in range(self.initial_food_amount)]

    def ui_callback_game_reset(self):
        self.reset()
        self.game_state = GameState.SIM_RUNNING

    def ui_callback_parents_chose(self, p1: Agent, p2: Agent, is_auto: bool):
        self.ui_parent1, self.ui_parent2 = p1, p2
        self.is_auto = is_auto
        self.card_choices = None
        self.ui_agent_card.reset()

    def ui_callback_condition_confirmed(self):
        self.game_state = GameState.PARENTS_SELECTION

    def ui_callback_offspring_confirmed(self):
        self.ui_offspring_confirmed = True

    def ui_callback_init_population_changed(self, value: int):
        self.initial_population = int(value)

    def ui_callback_init_food_changed(self, value: int):
        self.initial_food_amount = int(value)

    def ui_callback_sprite_changed(self, sprite: EntitySprite):
        self.sprite = sprite

    def ui_callback_back_to_menu(self):
        self.reset()
        self.game_state = GameState.MAIN_MENU

    def ui_callback_mutation_chance_changed(self, value: int):
        self.mutation_chance = value / 10

    def ui_callback_mutation_strength_changed(self, value: int):
        self.mutation_strength = value / 10

    def ui_callback_inspect_confirm(self):
        self.ui_agent_inspect = None
        self.game_state = GameState.SIM_PAUSED

    def ui_callback_inspect_called(self, agent: Agent):
        self.ui_agent_inspect = InspectAgent(self.window, self.sl, agent)
        self.game_state = GameState.AGENT_TREE


if __name__ == "__main__":
    Simulation()
