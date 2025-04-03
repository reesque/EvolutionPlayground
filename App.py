import pygame

from SpriteProcessor import SpriteLoader


class Window:
    def __init__(self, sl: SpriteLoader, width: int = 800, height: int = 600, fps: int = 60, r: int = 50, g: int = 50, b: int = 50):
        self.width = width
        self.height = height
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.bg_color = (r, g, b)
        self.sl = sl

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Evolution Playground")

        self.tile_ground = []
        for x in range(0, self.width, self.sl.get_tile_size()):
            row = []
            for y in range(0, self.height, self.sl.get_tile_size()):
                row.append((self.sl.get_random_tile_sprite(), x, y))
            self.tile_ground.append(row)

        self.clear()

    def clear(self):
        self.screen.fill(self.bg_color)

        for i in range(len(self.tile_ground)):
            for j in range(len(self.tile_ground[0])):
                sprite, x, y = self.tile_ground[i][j]
                self.screen.blit(sprite, (x, y))

    def tick(self):
        pygame.display.flip()
        self.clock.tick(self.fps)

