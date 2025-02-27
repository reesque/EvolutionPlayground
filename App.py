import pygame


class Window:
    def __init__(self, width: int = 800, height: int = 600, fps: int = 60, r: int = 50, g: int = 50, b: int = 50):
        self.width = width
        self.height = height
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.bg_color = (r, g, b)

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Evolution Playground")

        self.clear()

    def clear(self):
        self.screen.fill(self.bg_color)

    def tick(self):
        pygame.display.flip()
        self.clock.tick(self.fps)

