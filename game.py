import sys
import random
import math
import os

import pygame

from scripts.utils import load_image, load_images, load_player, Animation
from scripts.tilemap import Tilemap
from scripts.player import Player
from scripts.particle import Particle


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Ninja Fighter')
        self.screen = pygame.display.set_mode((640, 480), pygame.RESIZABLE)
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.character_count = len(os.listdir('data/images/player_selection'))

        self.player_dir = os.listdir('data/images/player_selection/')
        self.characters = []

        for file in self.player_dir:
            if file.endswith('.png'):
                name = file.replace('player/', '').replace('.png', '')
                self.characters.append(name)

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'background': pygame.transform.scale(load_image('background.png'),self.display.get_size()),
            'clouds': load_images('clouds'),
            'players': load_images('player_selection', alt=True),
            'attack': Animation(load_images('attack', alt=True), img_dur=3, loop=False),
        }

        self.player_size = (8, 15)

        self.movement1 = [False, False]
        self.movement2 = [False, False]

        self.flip = [False, True]

        self.tilemap = Tilemap(self)

    def start(self):

        self.choice = [0, 0]
        confirm = [False, False]

        start = True

        while start:
            self.display.blit(self.assets['background'], (0,0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and all(confirm):
                        start = False
                        break
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_a and not confirm[0]:
                        self.choice[0] = (self.choice[0] + 1) % self.character_count
                    if event.key == pygame.K_d and not confirm[0]:
                        self.choice[0] = (self.choice[0] - 1) % self.character_count
                    if event.key == pygame.K_w:
                        confirm[0] = not confirm[0]
                    if event.key == pygame.K_LEFT and not confirm[1]:
                        self.choice[1] = (self.choice[1] + 1) % self.character_count
                    if event.key == pygame.K_RIGHT and not confirm[1]:
                        self.choice[1] = (self.choice[1] - 1) % self.character_count
                    if event.key == pygame.K_UP:
                        confirm[1] = not confirm[1]

            self.display.blit(pygame.transform.scale(self.assets['players'][self.choice[0]], (160, 160)), (0, 40))
            self.display.blit(pygame.transform.flip(pygame.transform.scale(self.assets['players'][self.choice[1]], (160, 160)), True, False), (150, 40))

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)

        self.load_level('map')
        self.run()

    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        self.player_assets = {
            'player1': {
                'idle': Animation(load_images('players/' + str(self.characters[self.choice[0]]) + '/idle', alt=True), img_dur=30),
                'run': Animation(load_images('players/' + str(self.characters[self.choice[0]]) + '/run', alt=True), img_dur=4),
                'jump': Animation(load_images('players/' + str(self.characters[self.choice[0]]) + '/jump', alt=True)),
                'slide': Animation(load_images('players/' + str(self.characters[self.choice[0]]) + '/slide', alt=True)),
                'dash': Animation(load_images('players/' + str(self.characters[self.choice[0]]) + '/dash', alt=True)),
            },
            'player2': {
                'idle': Animation(load_images('players/' + str(self.characters[self.choice[1]]) + '/idle', alt=True), img_dur=30),
                'run': Animation(load_images('players/' + str(self.characters[self.choice[1]]) + '/run', alt=True), img_dur=4),
                'jump': Animation(load_images('players/' + str(self.characters[self.choice[1]]) + '/jump', alt=True)),
                'slide': Animation(load_images('players/' + str(self.characters[self.choice[1]]) + '/slide', alt=True)),
                'dash': Animation(load_images('players/' + str(self.characters[self.choice[1]]) + '/dash', alt=True)),
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

        self.swords = []

    def run(self):
        run = True

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
                    if event.key == pygame.K_e:
                        self.player1.attack()

                    if event.key == pygame.K_UP:
                        if self.player2.jump():
                            pass
                    if event.key == pygame.K_LEFT:
                        self.movement2[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement2[1] = True

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement1[0] = False
                    if event.key == pygame.K_d:
                        self.movement1[1] = False

                    if event.key == pygame.K_LEFT:
                        self.movement2[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement2[1] = False

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)


Game().start()