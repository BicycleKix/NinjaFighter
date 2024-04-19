import pygame
import sys
from scripts.utils import load_png
class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('testing')
        self.screen = pygame.display.set_mode((640, 480), pygame.RESIZABLE)

        self.clock = pygame.time.Clock()

        self.anim_offset = (-1, 0)
        self.attack_offset = (-11, -5)
        self.player = load_png('players/red/idle/00.png')
        self.sword = load_png('attack/00.png')

        if self.player is None or self.sword is None:
            print("Error loading images!")
            pygame.quit()
            sys.exit()

    def main(self):
        run = True
        while run:
            self.screen.fill((255, 255, 255))

            self.screen.blit(pygame.transform.flip(pygame.transform.scale(self.player, (100, 150)), True, False), (100 + self.anim_offset[0]*10, 100 + self.anim_offset[1]*10))
            self.screen.blit(pygame.transform.flip(pygame.transform.scale(self.sword, (190, 200)), True, False), (100 + self.attack_offset[0]*10, 100 + self.attack_offset[1]*10))            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_f:
                        pygame.display.toggle_fullscreen()

            pygame.display.flip()
            self.clock.tick(60)

Game().main()