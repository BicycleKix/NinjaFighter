import sys
import random
import math
import os

import pygame

from scripts.utils import load_image, load_images, load_player, Animation
from scripts.tilemap import Tilemap
from scripts.player import Player

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

        self.movement1 = [False, False]
        self.movement2 = [False, False]

        self.flip = [False, True]

        self.tilemap = Tilemap(self)

    def start(self):

        self.choice = [0, 0]
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
                        self.choice[0] = (self.choice[0] + 1) % self.character_count
                    if event.key == pygame.K_d:
                        self.choice[0] = (self.choice[0] - 1) % self.character_count
                    if event.key == pygame.K_w:
                        confirm[0] = not confirm[0]
                    if event.key == pygame.K_LEFT:
                        self.choice[1] = (self.choice[1] + 1) % self.character_count
                    if event.key == pygame.K_RIGHT:
                        self.choice[1] = (self.choice[1] - 1) % self.character_count
                    if event.key == pygame.K_UP:
                        confirm[1] = not confirm[1]

            self.display.blit(pygame.transform.scale(self.assets['players'][self.choice[0]], (160, 160)), (0, 40))
            self.display.blit(pygame.transform.flip(pygame.transform.scale(self.assets['players'][self.choice[1]], (160, 160)), True, False), (150, 40))

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)

    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        self.player_assets = {
            'player1': {
                'idle': Animation(load_images('players/red/idle', alt=True), img_dur=30),
                'run': Animation(load_images('players/red/run', alt=True), img_dur=4),
                'jump': Animation(load_images('players/red/jump', alt=True)),
                'attack': Animation(load_images('players/red/attack', alt=True), img_dur=4, loop=False),
                'slide': Animation(load_images('players/red/slide', alt=True)),
                'dash': Animation(load_images('players/red/dash', alt=True)),
            },
            'player2': {
                'idle': Animation(load_images('players/yellow/idle', alt=True), img_dur=30),
                'run': Animation(load_images('players/yellow/run', alt=True), img_dur=4),
                'jump': Animation(load_images('players/yellow/jump', alt=True)),
                'attack': Animation(load_images('players/yellow/attack', alt=True), img_dur=4, loop=False),
                'slide': Animation(load_images('players/yellow/slide', alt=True)),
                'dash': Animation(load_images('players/yellow/dash', alt=True)),
            },
        }

        self.player1 = Player(self, (50, 50), (6, 15), self.choice[0])
        self.player2 = Player(self, (50, 50), (6, 15), self.choice[1])

        spawn_points = self.tilemap.extract([('spawners', 0)])

        spawn = random.choice(spawn_points)
        self.player1.pos = spawn['pos']
        self.player1.air_time = 0
        spawn_points.remove(spawn)
        spawn = random.choice(spawn_points)
        self.player2.pos = spawn['pos']
        self.player2.air_time = 0
        spawn_points.remove(spawn)

    def run(self):
        run = True

        self.load_level('map')

        while run:
            self.display.blit(self.assets['background'], (0,0))

            self.tilemap.render(self.display)

            self.player1.update(self.tilemap, (self.movement1[1]-self.movement1[0], 0))
            self.player1.render(self.display)
            self.player2.update(self.tilemap, (self.movement2[1]-self.movement2[0], 0))
            self.player2.render(self.display)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_w:
                        if self.player1.jump():
                            pass
                    if event.key == pygame.K_a:
                        self.movement1[0] = True
                    if event.key == pygame.K_d:
                        self.movement1[1] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement1[0] = False
                    if event.key == pygame.K_d:
                        self.movement1[1] = False

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)


Game().start()