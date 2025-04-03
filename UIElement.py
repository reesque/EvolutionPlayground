import random

import numpy as np
import pygame

import App
import SpriteProcessor
from Entity import Agent


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
    def __init__(self, window: App):
        super().__init__(window)
        self.font = pygame.font.Font('assets/PressStart2P-Regular.ttf', 14)
        self.box = pygame.Rect(15, self.window.height - 50, self.window.width - 30, 40)
        self.new_btn = Button(window, self.window.width - 80, self.window.height - 45, 55, 30, 'New',
                              13, (9, 9))
        self.stat_btn = Button(window, self.window.width - 230, self.window.height - 45, 135, 30, 'Statistic',
                               13, (9, 9))

    def render(self, gen, num_agent, num_food):
        pygame.draw.rect(self.window.screen, (0, 0, 0), self.box.inflate(0, 0), border_radius=3)

        gen_text = self.font.render(f'Generation: {gen}  |  '
                                    f'Population: {num_agent}  |  '
                                    f'Food: {num_food}', True, (255, 255, 255))
        self.window.screen.blit(gen_text, (30, self.window.height - 36))

        self.new_btn.render()
        self.stat_btn.render()


class Button(UIElement):
    def __init__(self, window: App, x, y, w, h, title, font_size, text_offset):
        super().__init__(window)
        self.box = pygame.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.text_offset = text_offset
        self.active = True
        self.font = pygame.font.Font('assets/PressStart2P-Regular.ttf', font_size)
        self.text = self.font.render(title, True, (0, 0, 0))

    def render(self):
        pygame.draw.rect(self.window.screen, (255, 255, 255) if self.active else (100, 100, 100),
                         self.box.inflate(0, 0), border_radius=3)
        self.window.screen.blit(self.text, (self.x + self.text_offset[0], self.y + self.text_offset[1]))

    def set_active(self, is_active: bool):
        self.active = is_active

    def collidepoint(self, pos):
        return self.box.collidepoint(pos) and self.active


class AgentCard(UIElement):
    def __init__(self, window: App, sl: SpriteProcessor, idx: int):
        super().__init__(window)
        self.idx = idx
        self.sl = sl
        self.font1 = pygame.font.Font('assets/PressStart2P-Regular.ttf', 16)
        self.font2 = pygame.font.Font('assets/PressStart2P-Regular.ttf', 9)
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
    def __init__(self, window: App, sl: SpriteProcessor):
        super().__init__(window)

        self.font = pygame.font.Font('assets/PressStart2P-Regular.ttf', 25)
        self.title = self.font.render('Choose 2 Parents', True, (0, 0, 0))

        self.random_btn = Button(window, 375, 510, 115, 40, 'Random', 15, (13, 13))
        self.confirm_btn = Button(window, 505, 510, 115, 40, 'Confirm', 15, (13, 13))
        self.card = [AgentCard(window, sl, c) for c in range(4)]
        self.active = [False for _ in range(4)]

    def reset(self):
        self.active = [False for _ in range(4)]

    def render(self, parents: list[Agent], callback):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.confirm_btn.collidepoint(event.pos):
                    parents_idx = np.where(self.active)[0]
                    prs = np.array(parents)[parents_idx].tolist()
                    callback(prs[0], prs[1], False)

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
    def __init__(self, window: App, sl: SpriteProcessor):
        super().__init__(window)

        self.font = pygame.font.Font('assets/PressStart2P-Regular.ttf', 25)
        self.title = self.font.render('Result Offsprings', True, (0, 0, 0))

        self.confirm_btn = Button(window, 455, 510, 85, 40, 'Okay', 15, (13, 13))
        self.card = [AgentCard(window, sl, c) for c in range(4)]

    def render(self, offsprings: list[(Agent, bool, int, int)], callback):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.confirm_btn.collidepoint(event.pos):
                    callback()

        self.window.screen.blit(self.title, (290, 50))

        for i in range(len(offsprings)):
            agent, is_mutate, speed_mutate, size_mutate = offsprings[i]
            self.card[i].render_mutate(agent, is_mutate, speed_mutate, size_mutate)

        self.confirm_btn.render()
