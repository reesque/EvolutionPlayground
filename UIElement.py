import random

import numpy as np
import pygame

import App
from Entity import MenuAgent, Agent
from SpriteProcessor import SpriteLoader, EntitySprite


class UIElement:
    def __init__(self, window: App):
        self.window = window


class PauseBox(UIElement):
    def __init__(self, window: App):
        super().__init__(window)
        self.window = window
        self.font = pygame.font.Font('assets/PressStart2P-Regular.ttf', 15)
        self.text = self.font.render("PAUSED", True, (255, 255, 255))
        self.box = pygame.Rect((self.window.width // 2) - 60, (self.window.height // 2) - 20, 120, 40)

    def render(self):
        pygame.draw.rect(self.window.screen, (0, 0, 0), self.box.inflate(0, 0), border_radius=3)
        self.window.screen.blit(self.text, ((self.window.width // 2) - (self.text.get_width() // 2),
                                            (self.window.height // 2) - (self.text.get_height() // 2)))


class SimulationInformation(UIElement):
    def __init__(self, window: App, menu_callback):
        super().__init__(window)
        self.font = pygame.font.Font('assets/PressStart2P-Regular.ttf', 14)
        self.box = pygame.Rect(15, self.window.height - 50, self.window.width - 30, 40)
        self.menu_callback = menu_callback
        self.menu_btn = Button(window, self.window.width - 90, self.window.height - 45, 70, 30, 'Menu',
                               13, (9, 9))
        self.stat_btn = Button(window, self.window.width - 240, self.window.height - 45, 135, 30, 'Statistic',
                               13, (9, 9))

    def render(self, events, gen, num_agent, num_food):
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                if self.menu_btn.collidepoint(event.pos):
                    self.menu_callback()

        pygame.draw.rect(self.window.screen, (0, 0, 0), self.box.inflate(0, 0), border_radius=3)

        gen_text = self.font.render(f'Generation: {gen}  |  '
                                    f'Population: {num_agent}  |  '
                                    f'Food: {num_food}', True, (255, 255, 255))
        self.window.screen.blit(gen_text, (30, self.window.height - 36))

        self.menu_btn.render()
        self.stat_btn.render()


class Button(UIElement):
    def __init__(self, window: App, x: int, y: int, w: int, h: int, title: str,
                 font_size: int, text_offset: tuple[int, int],
                 button_color: tuple[int, int, int] = (255, 255, 255),
                 text_color: tuple[int, int, int] = (0, 0, 0)):
        super().__init__(window)
        self.box = pygame.Rect(x, y, w, h)
        self.x, self.y = x, y
        self.color = button_color
        self.text_offset = text_offset
        self.active = True
        self.font = pygame.font.Font('assets/PressStart2P-Regular.ttf', font_size)
        self.text = self.font.render(title, True, text_color)

    def render(self):
        pygame.draw.rect(self.window.screen, self.color if self.active else (100, 100, 100),
                         self.box.inflate(0, 0), border_radius=3)
        self.window.screen.blit(self.text, (self.x + self.text_offset[0], self.y + self.text_offset[1]))

    def set_active(self, is_active: bool):
        self.active = is_active

    def collidepoint(self, pos):
        return self.box.collidepoint(pos) and self.active


class AgentCard(UIElement):
    def __init__(self, window: App, sl: SpriteLoader, idx: int):
        super().__init__(window)
        self.idx = idx
        self.sl = sl
        self.font1 = pygame.font.Font('assets/PressStart2P-Regular.ttf', 16)
        self.font2 = pygame.font.Font('assets/PressStart2P-Regular.ttf', 10)
        self.box = pygame.Rect(28 + idx * 240, 120, 220, 350)

        self.current_frame = -1

    def render(self, agent: Agent, is_active: bool):
        if self.current_frame == -1:
            self.current_frame = random.randint(0, self.sl.get_num_frame_in_entity_sprite(agent.sprite) - 1)

        title = self.font1.render(f'{agent.sprite.value} {self.idx + 1}', True, (255, 255, 255))
        speed = self.font2.render(f'Speed: {agent.speed:.2G}', True, (255, 255, 255))
        awareness = self.font2.render(f'Sight: {agent.size:.2G}', True, (255, 255, 255))
        fitness = self.font2.render(f'Food Gathered: {agent.eaten}', True, (255, 255, 255))

        # Render
        current_sprite = self.sl.get_entity_sprite_at_frame(agent.sprite, self.current_frame)
        pygame.draw.rect(self.window.screen, (0, 0, 0), self.box.inflate(0, 0), border_radius=5)
        self.window.screen.blit(pygame.transform.scale(
            current_sprite, (current_sprite.get_width() * 3,
                             current_sprite.get_height() * 3)), (self.box.x + 75, self.box.y + 40))

        self.window.screen.blit(title, (self.box.x + 25, self.box.y + 180))
        self.window.screen.blit(speed, (self.box.x + 25, self.box.y + 210))
        self.window.screen.blit(awareness, (self.box.x + 25, self.box.y + 235))
        self.window.screen.blit(fitness, (self.box.x + 25, self.box.y + 260))
        if is_active:
            pygame.draw.rect(self.window.screen, (180, 0, 0), self.box, 5, border_radius=5)

        if pygame.time.get_ticks() % 10 == 0:
            self.current_frame = pygame.time.get_ticks() % self.sl.get_num_frame_in_entity_sprite(agent.sprite)

    def render_mutate(self, agent: Agent, is_mutate: bool, speed_mutation: float = 0.0, size_mutation: float = 0.0):
        if self.current_frame == -1:
            self.current_frame = random.randint(0, self.sl.get_num_frame_in_entity_sprite(agent.sprite) - 1)

        title = self.font1.render(f'{agent.sprite.value} {self.idx + 1}', True, (255, 255, 255))
        if is_mutate:
            speed = self.font2.render(f'Speed: {(agent.speed - speed_mutation):.2G} ({speed_mutation:+.2G})',
                                      True, (255, 255, 255))
            awareness = self.font2.render(f'Sight: {(agent.size - size_mutation):.2G} ({size_mutation:+.2G})',
                                          True, (255, 255, 255))
        else:
            speed = self.font2.render(f'Speed: {agent.speed:.2G}', True, (255, 255, 255))
            awareness = self.font2.render(f'Sight: {agent.size:.2G}', True, (255, 255, 255))
        mutated = pygame.transform.rotate(self.font1.render('Mutated', True, (255, 255, 0)), 348)

        # Render
        current_sprite = self.sl.get_entity_sprite_at_frame(agent.sprite, self.current_frame)
        pygame.draw.rect(self.window.screen, (0, 0, 0), self.box.inflate(0, 0), border_radius=5)
        self.window.screen.blit(pygame.transform.scale(
            current_sprite, (current_sprite.get_width() * 3,
                             current_sprite.get_height() * 3)), (self.box.x + 75, self.box.y + 40))

        self.window.screen.blit(title, (self.box.x + 25, self.box.y + 180))
        self.window.screen.blit(speed, (self.box.x + 25, self.box.y + 210))
        self.window.screen.blit(awareness, (self.box.x + 25, self.box.y + 235))
        if is_mutate:
            pygame.draw.rect(self.window.screen, (255, 255, 0), self.box, 5, border_radius=5)
            self.window.screen.blit(mutated, (self.box.x + 55, self.box.y + 282))
        else:
            pygame.draw.rect(self.window.screen, (200, 200, 200), self.box, 5, border_radius=5)

        if pygame.time.get_ticks() % 10 == 0:
            self.current_frame = pygame.time.get_ticks() % self.sl.get_num_frame_in_entity_sprite(agent.sprite)

    def collidepoint(self, pos):
        return self.box.collidepoint(pos)


class ParentsSelection(UIElement):
    def __init__(self, window: App, sl: SpriteLoader):
        super().__init__(window)

        self.font = pygame.font.Font('assets/PressStart2P-Regular.ttf', 25)
        self.title = self.font.render('Choose 2 Parents', True, (0, 0, 0))

        self.random_btn = Button(window, 375, 510, 115, 40, 'Random', 15, (13, 13))
        self.confirm_btn = Button(window, 505, 510, 115, 40, 'Confirm', 15, (13, 13))
        self.card = [AgentCard(window, sl, c) for c in range(4)]
        self.active = [False for _ in range(4)]

    def reset(self):
        self.active = [False for _ in range(4)]

    def render(self, parents: list[Agent], events, callback):
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                if self.confirm_btn.collidepoint(event.pos):
                    parents_idx = np.where(self.active)[0]
                    prs = np.array(parents)[parents_idx].tolist()
                    callback(prs[0], prs[1], False)

                    # Prevent clicking on button underneath
                    setattr(event, 'handled', True)

                if self.random_btn.collidepoint(event.pos):
                    prs = np.random.choice(parents, 2, replace=False)
                    callback(prs[0], prs[1], True)

                for i in range(len(self.card)):
                    if self.card[i].collidepoint(event.pos):
                        if self.active[i]:
                            self.active[i] = False
                        elif sum(self.active) < 2:
                            self.active[i] = True

        self.window.screen.blit(self.title, (305, 50))

        for i in range(len(parents)):
            self.card[i].render(parents[i], self.active[i])

        self.confirm_btn.set_active(sum(self.active) == 2)
        self.confirm_btn.render()

        self.random_btn.render()


class Offspring(UIElement):
    def __init__(self, window: App, sl: SpriteLoader):
        super().__init__(window)

        self.font = pygame.font.Font('assets/PressStart2P-Regular.ttf', 25)
        self.title = self.font.render('Result Offsprings', True, (0, 0, 0))

        self.confirm_btn = Button(window, 455, 510, 85, 40, 'Okay', 15, (13, 13))
        self.card = [AgentCard(window, sl, c) for c in range(4)]

    def render(self, offsprings: list[(Agent, bool, int, int)], events, callback):
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                # Prevent clicking on button underneath
                if self.confirm_btn.collidepoint(event.pos) and not getattr(event, 'handled', False):
                    callback()

        self.window.screen.blit(self.title, (290, 50))

        for i in range(len(offsprings)):
            agent, is_mutate, speed_mutate, size_mutate = offsprings[i]
            self.card[i].render_mutate(agent, is_mutate, speed_mutate, size_mutate)

        self.confirm_btn.render()


class SeekBar(UIElement):
    def __init__(self, window: App, x, y, w, h, min_lim, max_lim, init_value, callback):
        super().__init__(window)

        self.x, self.y, self.w, self.h = x, y, w, h
        self.min, self.max = min_lim, max_lim
        self.callback = callback

        self.bar = pygame.Rect(x, y, w, h)

        self.init_value = init_value
        self.slider_x = x + ((init_value - min_lim) * w // (max_lim - min_lim))
        self.value = init_value

        self.x_min = self.x + (self.h // 2)
        self.x_max = (self.x + self.w) - (self.h // 2)

    def render(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP and self.y <= event.pos[1] <= self.y + self.h:
                self.slider_x = max(self.x_min, min(event.pos[0], self.x_max))
                self.value = ((self.slider_x - self.x_min) * (self.max - self.min) / (
                        self.x_max - self.x_min)) + self.min
                self.callback(self.value)

        pygame.draw.rect(self.window.screen, (255, 255, 255), self.bar.inflate(0, 0), border_radius=10)
        pygame.draw.circle(self.window.screen,
                           (0, 0, 0),
                           (self.slider_x, self.y + 7.5), (self.h // 2) + 0.75)


class MainMenu(UIElement):
    def __init__(self, window: App, sl: SpriteLoader, population_callback, food_count_callback,
                 sprite_callback, game_start_callback, mutation_chance_callback, mutation_strength_callback):
        super().__init__(window)
        self.sl = sl

        self.game_start_callback = game_start_callback

        self.font1 = pygame.font.Font('assets/PressStart2P-Regular.ttf', 35)
        self.font2 = pygame.font.Font('assets/PressStart2P-Regular.ttf', 15)

        self.population_seekbar = SeekBar(self.window, 268, 180, 200, 14, 1,
                                          20, 10, population_callback)
        self.food_count_seekbar = SeekBar(self.window, 192, 210, 200, 14, 1,
                                          150, 100, food_count_callback)
        self.mutation_chance_seekbar = SeekBar(self.window, 360, 240, 200, 14, 0,
                                               10, 1, mutation_chance_callback)
        self.mutation_strength_seekbar = SeekBar(self.window, 390, 270, 200, 14, 0,
                                                 30, 5, mutation_strength_callback)
        self.title = self.font1.render('Genetics Playground', True, (0, 0, 0))
        self.start_btn = Button(window, 40, 310, 125, 44, 'Start', 20, (13, 13))

        self.menu_agent = MenuAgent(window, sl, EntitySprite.CHICKEN, 2.0, sprite_callback,
                                    bound=((25, self.window.height - 220),
                                           (self.window.width - 25, self.window.height - 25)))

    def render(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                if self.start_btn.collidepoint(event.pos):
                    self.game_start_callback()

        population = self.font2.render(f'Population: {int(self.population_seekbar.value):02d}', True, (0, 0, 0))
        food = self.font2.render(f'Food: {int(self.food_count_seekbar.value):03d}', True, (0, 0, 0))
        mutation_chance = self.font2.render(f'Mutation Chance: {int(self.mutation_chance_seekbar.value) * 10}%',
                                            True, (0, 0, 0))
        mutation_strength = self.font2.render(f'Mutation Strength: {self.mutation_strength_seekbar.value / 10:.2g}',
                                              True, (0, 0, 0))

        self.menu_agent.move()
        self.menu_agent.draw(events)

        self.window.screen.blit(self.title, (40, 100))
        self.window.screen.blit(population, (40, 180))
        self.window.screen.blit(food, (40, 210))
        self.window.screen.blit(mutation_chance, (40, 240))
        self.window.screen.blit(mutation_strength, (40, 270))

        self.population_seekbar.render(events)
        self.food_count_seekbar.render(events)
        self.mutation_chance_seekbar.render(events)
        self.mutation_strength_seekbar.render(events)

        self.start_btn.render()


class GameOver(UIElement):
    def __init__(self, window: App, menu_callback):
        super().__init__(window)
        self.menu_callback = menu_callback

        self.font1 = pygame.font.Font('assets/PressStart2P-Regular.ttf', 35)
        self.font2 = pygame.font.Font('assets/PressStart2P-Regular.ttf', 15)

        self.title = self.font1.render('Game Over', True, (0, 0, 0))
        self.menu_btn = Button(window, 400, 360, 210, 44, 'Back to Menu', 15, (16, 16))

    def render(self, events, generation: int):
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                if self.menu_btn.collidepoint(event.pos):
                    self.menu_callback()

        g_text = 'generations' if generation > 1 else 'generation'
        gen = self.font2.render(f'Your species was extinct after {generation:02d} {g_text}', True, (0, 0, 0))

        self.window.screen.blit(self.title, (350, 240))
        self.window.screen.blit(gen, (170, 310))

        self.menu_btn.render()
