import sys
import random
import math
import os

import pygame

from scripts.utils import load_image, load_images, load_player, Animation
from scripts.tilemap import Tilemap
from scripts.entities import Player

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Ninja Fighter')
        self.screen = pygame.display.set_mode((640, 480), pygame.RESIZABLE)
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.character_count = len(os.listdir('data/images/player_selection'))
        self.characters = sorted(os.listdir('data/images/player_selection'))

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'background': pygame.transform.scale(load_image('background.png'),self.display.get_size()),
            'clouds': load_images('clouds'),
            'players': load_images('player_selection', alt=True),
        }

        self.player_size = (8, 15)

        self.movement1 = [False, False, False]
        self.movement2 = [False, False, True]

        self.tilemap = Tilemap(self)

        self.player = [Player(self, 0, (50, 50), (8, 15)), Player(self, 0, (50, 50), (8, 15))]

        self.load_level('map')

    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        spawn_points = self.tilemap.extract([('spawners', 0)]).copy()

        for player in self.player:
            player.pos = random.choice(spawn_points)
            player.air_time = 0
            spawn_points.remove(player.pos)           

    def start(self):

        choice = [0, 0]
        confirm = [False, False]

        while True:
            self.display.blit(self.assets['background'], (0,0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and all(confirm):
                        self.run()
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_a:
                        choice[0] = (choice[0] + 1) % self.character_count
                    if event.key == pygame.K_d:
                        choice[0] = (choice[0] - 1) % self.character_count
                    if event.key == pygame.K_w:
                        confirm[0] = not confirm[0]
                    if event.key == pygame.K_LEFT:
                        choice[1] = (choice[1] + 1) % self.character_count
                    if event.key == pygame.K_RIGHT:
                        choice[1] = (choice[1] - 1) % self.character_count
                    if event.key == pygame.K_UP:
                        confirm[1] = not confirm[1]

            self.display.blit(pygame.transform.scale(self.assets['players'][choice[0]], (160, 160)), (0, 40))
            self.display.blit(pygame.transform.flip(pygame.transform.scale(self.assets['players'][choice[1]], (160, 160)), True, False), (150, 40))

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)


    def run(self):
        run = True

        while run:
            self.display.blit(self.assets['background'], (0,0))

            self.tilemap.render(self.display)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)


Game().start()