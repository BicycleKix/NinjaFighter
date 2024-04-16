import pygame
import sys, os

class Game:
    def __init__(self) -> None:
        pygame.init()

        self.screen = pygame.display.set_mode((640, 480), pygame.RESIZABLE)
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

    def run(self):
        running = True

        self.attack = Blit(self, (10, 10))

        while running:
            self.display.fill((255, 0, 0))

            pygame.draw.rect(self.display, (0, 0, 255), (10, 10, 16, 16))

            self.attack.render(self.display)
            self.attack.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_w:
                        self.attack.regenerate()

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)

class Blit:
    def __init__(self, game, pos, size=(16, 16), cooldown=60):
        self.game = game
        self.size = size
        self.cooldown = cooldown
        self.pos = pos

        self.sillhouette = self.size[1]
        self.regeneration_speed = int(self.size[1] / self.cooldown)
        self.regenerating = False

        self.surface = pygame.Surface((320, 240), pygame.SRCALPHA)

    def regenerate(self):
        if not self.regenerating:
            self.regenerating = True
            self.sillhouette = 0

    def update(self):
        if self.regenerating:
            self.sillhouette = min(self.size[1], self.sillhouette + self.regeneration_speed)
            if self.sillhouette == self.size[1]:
                self.regenerating = False

    def render(self, surf):
        pygame.draw.rect(self.surface, (0, 255, 0, 100), pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.sillhouette))

        surf.blit(self.surface, self.pos)

Game().run()