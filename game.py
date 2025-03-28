import sys
import random
import os
import json
import math

import pygame

from scripts.utils import load_image, load_images, draw_rect, icon, load_png, Animation, Blit
from scripts.tilemap import Tilemap
from scripts.player import Player

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.font1 = pygame.font.SysFont("comicsans", 30)
        self.font2 = pygame.font.SysFont("comicsans", 20)
        self.font3 = pygame.font.SysFont("comicsans", 13, bold=True)
        self.font4 = pygame.font.SysFont('monolisa', 32)

        self.green = (0, 155, 0)
        self.dark_green = (40, 70, 40)

        pygame.display.set_caption('Ninja Fighter')
        self.screen = pygame.display.set_mode((640, 480), pygame.RESIZABLE)
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()
        self.open_game = False

        # joystick_count = pygame.joystick.get_count()
        self.controllers = []

        # for i in range(joystick_count):
        #     joystick = pygame.joystick.Joystick(i)
        #     joystick.init()
        #     self.controllers.append(joystick)
        #     print("Joystick", i + 1, ":", joystick.get_name())

        self.character_count = len(os.listdir('data/images/player_selection'))

        self.player_dir = os.listdir('data/images/player_selection/')
        self.characters = []

        for file in self.player_dir:
            if file.endswith('.png'):
                name = file.replace('player/', '').replace('.png', '')
                self.characters.append(name)

        self.sfx = {
            'jump':pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash':pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit':pygame.mixer.Sound('data/sfx/hit.wav'),
            'select':pygame.mixer.Sound('data/sfx/shoot.wav'),
            'intro':pygame.mixer.Sound('data/sfx/intro_audio.wav'),
            'lobby':pygame.mixer.Sound('data/sfx/lobby.wav'),
        }

        self.sfx['select'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.7)
        self.sfx['intro'].set_volume(0.5)

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'background': pygame.transform.scale(load_image('background.png'), self.display.get_size()),
            'clouds': load_images('clouds'),
            'players': load_images('player_selection', alt=True),
            'attack': Animation(load_images('attack', alt=True), img_dur=3, loop=False),
            'bomb': load_png('icons/bomb.png'),
        }

        self.blits = {
            'p1_attack': Blit(self, (10, 10), cooldown=90),
            'p2_attack': Blit(self, (294, 10), cooldown=90),
            'p1_dash': Blit(self, (30, 10), cooldown=120),
            'p2_dash': Blit(self, (274, 10), cooldown=120),
            'p1_bomb': Blit(self, (50, 10), cooldown=300),
            'p2_bomb': Blit(self, (254, 10), cooldown=300),
        }

        self.rects = {
            'attack1': {'color': (170, 0, 0), 'pos': (9, 9)},
            'attack2': {'color': (170, 0, 0), 'pos': (293, 9)},
            'dash1': {'color': (0, 100, 220), 'pos': (29, 9)},
            'dash2': {'color': (0, 100, 220), 'pos': (273, 9)},
            'bomb1': {'color': (150, 140, 110), 'pos': (49, 9)},
            'bomb2': {'color': (150, 140, 110), 'pos': (253, 9)},
        }

        self.icons = {
            'sword1': {'img': load_png('icons/sword.png'), 'pos': (11, 11)},
            'sword2': {'img': load_png('icons/sword.png'), 'pos': (295, 11)},
            'dash1': {'img': load_png('icons/dash.png'), 'pos': (31, 11)},
            'dash2': {'img': load_png('icons/dash.png'), 'pos': (275, 11)},
            'bomb1': {'img': load_png('icons/bomb.png'), 'pos': (51, 11)},
            'bomb2': {'img': load_png('icons/bomb.png'), 'pos': (255, 11)},
        }

        self.player_stats = {}
        self.load_stats_from_file("data/stats.json")

        self.player_size = (8, 15)

        self.movement = [[False, False], [False, False]]

        self.tilemap = Tilemap(self)

        self.bombs = []
        self.smoke = []
        self.bomb_effect = []
        self.smoke_effect_radius = 25

    def load_stats_from_file(self, filename):
        try:
            with open(filename, 'r') as file:
                self.player_stats = json.load(file)
        except FileNotFoundError:
            print("File not found. No stats loaded.")
        except Exception as e:
            print("Error loading stats:", e)

    def save_stats_to_file(self, filename):
        try:
            with open(filename, 'w') as file:
                json.dump(self.player_stats, file)
        except Exception as e:
            print("Error saving stats:", e)

    def quit(self):
        self.save_stats_to_file('data/stats.json')
        pygame.quit()
        sys.exit()

    def main_menu(self):

        selection = 0

        title_font = self.font1.render('Ninja Fighter', 0, 'white')

        menu_options = [self.start, self.stats, self.options, self.quit]

        if not self.open_game:
            self.sfx['intro'].play()
            self.open_game = True
            pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
        
        menu_rects = [
            [self.green, (110, 70), (100, 30)],
            [self.green, (110, 110), (100, 30)],
            [self.green, (110, 150), (100, 30)],
            [self.green, (110, 190), (100, 30)],
        ]

        menu_text = [
            self.font2.render('Start', 0, 'white'),
            self.font2.render('Stats', 0, 'white'),
            self.font2.render('Options', 0, 'white'),
            self.font2.render('Quit', 0, 'white'),
        ]

        menu_text_pos = [
            ((menu_rects[0][1][0] + menu_rects[0][2][0] / 2) - menu_text[0].get_width()/2, (menu_rects[0][1][1] + menu_rects[0][2][1] / 2) - menu_text[0].get_height()/2),
            ((menu_rects[1][1][0] + menu_rects[1][2][0] / 2) - menu_text[1].get_width()/2, (menu_rects[1][1][1] + menu_rects[1][2][1] / 2) - menu_text[1].get_height()/2),
            ((menu_rects[2][1][0] + menu_rects[2][2][0] / 2) - menu_text[2].get_width()/2, (menu_rects[2][1][1] + menu_rects[2][2][1] / 2) - menu_text[2].get_height()/2),
            ((menu_rects[3][1][0] + menu_rects[3][2][0] / 2) - menu_text[3].get_width()/2, (menu_rects[3][1][1] + menu_rects[3][2][1] / 2) - menu_text[3].get_height()/2),
        ]

        run = True

        while run:

            self.display.blit(self.assets['background'], (0,0))

            self.display.blit(title_font, ((320 - title_font.get_width())/2, 0))

            menu_rects[selection][0] = self.dark_green

            for rects in menu_rects:
                draw_rect(self.display, rects[0], rects[1], rects[2])

            for i in range(len(menu_text)):
                self.display.blit(menu_text[i], menu_text_pos[i])

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()

                if event.type == pygame.USEREVENT + 1:
                    self.sfx['lobby'].play(-1)

                if event.type == pygame.JOYDEVICEADDED:
                    joystick = pygame.joystick.Joystick(event.device_index)
                    joystick.init()
                    self.controllers.append(joystick)
                    print("Joystick", event.device_index + 1, ":", joystick.get_name())

                if event.type == pygame.JOYDEVICEREMOVED:
                    del self.controllers[event.instance_id]
                    print("Joystick", event.device_index + 1, ":", joystick.get_name(), "removed")

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.quit()
                    if event.key in (pygame.K_s, pygame.K_DOWN):
                        menu_rects[selection][0] = self.green
                        selection = (selection + 1) % len(menu_rects)
                        self.sfx['select'].play()
                    if event.key in (pygame.K_w, pygame.K_UP):
                        menu_rects[selection][0] = self.green
                        selection = (selection - 1) % len(menu_rects)
                        self.sfx['select'].play()
                    if event.key == pygame.K_RETURN:
                        self.sfx['select'].play()
                        menu_options[selection]()

                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        self.sfx['select'].play()
                        menu_options[selection]()
                    if event.button == 1:
                        self.quit()

                if event.type == pygame.JOYHATMOTION:
                    direction = event.value

                    menu_rects[selection][0] = self.green
                    selection = (selection - direction[1]) % len(menu_rects)
                    if direction[1] != 0:
                        self.sfx['select'].play()

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)

    def stats(self):

        selection = 0

        menu_options = [self.add_player, self.main_menu]
        
        menu_rects = [
            [self.green, (20, 70), (100, 30)],
            [self.green, (20, 110), (100, 30)],
        ]

        menu_text = [
            self.font2.render('Add Player', 0, 'white'),
            self.font3.render('Back to Menu', 0, 'white'),
        ]

        menu_text_pos = [
            ((menu_rects[0][1][0] + menu_rects[0][2][0] / 2) - menu_text[0].get_width()/2, (menu_rects[0][1][1] + menu_rects[0][2][1] / 2) - menu_text[0].get_height()/2),
            ((menu_rects[1][1][0] + menu_rects[1][2][0] / 2) - menu_text[1].get_width()/2, (menu_rects[1][1][1] + menu_rects[1][2][1] / 2) - menu_text[1].get_height()/2),
        ]

        run = True

        temp_text = self.font3.render('stats coming soon', 0, 'white')

        while run:

            self.display.blit(self.assets['background'], (0,0))
            self.display.blit(temp_text, (150, 100))

            menu_rects[selection][0] = self.dark_green

            for rects in menu_rects:
                draw_rect(self.display, rects[0], rects[1], rects[2])

            for i in range(len(menu_text)):
                self.display.blit(menu_text[i], menu_text_pos[i])

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                
                if event.type == pygame.KEYDOWN:
                    self.sfx['select'].play()
                    if event.key == pygame.K_ESCAPE:
                        return
                    if event.key in (pygame.K_s, pygame.K_DOWN):
                        menu_rects[selection][0] = self.green
                        selection = (selection + 1) % len(menu_rects)
                    if event.key in (pygame.K_w, pygame.K_UP):
                        menu_rects[selection][0] = self.green
                        selection = (selection - 1) % len(menu_rects)
                    if event.key == pygame.K_RETURN:
                        menu_options[selection]()

                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        self.sfx['select'].play()
                        menu_options[selection]()
                    if event.button == 1:
                        return

                if event.type == pygame.JOYHATMOTION:
                    direction = event.value

                    menu_rects[selection][0] = self.green
                    selection = (selection - direction[1]) % len(menu_rects)
                    if direction[1] != 0:
                        self.sfx['select'].play()

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)
            

    def add_player(self):

        text = ''
        text_rect = pygame.Rect(60, 50, 200, 50)
        color = pygame.Color('dodgerblue2')

        length_text = self.font2.render('Max 16 Characters', 0, 'white')

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if text not in self.player_stats:
                            self.player_stats[text] = ( {'gp': 0, 'w': 0, 'l': 0} )
                            return
                    elif event.key == pygame.K_ESCAPE:
                        #don't save
                        return
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    elif len(text) < 16:
                        text += event.unicode

                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        if text not in self.player_stats:
                            self.player_stats[text] = ( {'gp': 0, 'w': 0, 'l': 0} )
                            return
                    if event.button == 1:
                        #don't save
                        return

            self.display.fill((30, 30, 30))
            pygame.draw.rect(self.display, color, text_rect, 2)

            text_surface = self.font4.render(text, 0, color)
            self.display.blit(text_surface, (text_rect.x + 5, text_rect.y + 5))
            self.display.blit(length_text, (160 - length_text.get_width()/2, 120 - length_text.get_height()/2))

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)


    def options(self):
        print('menu not available')
        return

    def start(self):

        self.choice = [0, 0]
        self.player_choice = [0, 0]
        confirm = [False, False]
        player_confirm = [False, False]

        self.users = list(self.player_stats.keys())

        start = True
        
        title_font = self.font2.render('Choose Your Figther and User', 0, 'white')
        confirm_text = self.font3.render('Press W / Up, S / Down to Toggle Confirm', 0, 'white')

        while start:
            self.display.blit(self.assets['background'], (0,0))

            self.display.blit(title_font, ((320 - title_font.get_width())/2, 20))
            self.display.blit(confirm_text, ((320 - confirm_text.get_width())/2, 200))

            self.display.blit(pygame.transform.scale(self.assets['players'][self.choice[0]], (160, 160)), (0, 40))
            self.display.blit(pygame.transform.flip(pygame.transform.scale(self.assets['players'][self.choice[1]], (160, 160)), True, False), (150, 40))

            player_text = [self.font3.render(str(self.users[self.player_choice[0]]), 0, 'white'), self.font3.render(str(self.users[self.player_choice[1]]), 0, 'white')]
            self.display.blit(player_text[0], ((self.assets['players'][0].get_width() * 5 - player_text[0].get_width()) / 2, 170))
            self.display.blit(player_text[1], (150 + (self.assets['players'][0].get_width() * 5 - player_text[1].get_width()) / 2, 170))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN:
                    self.sfx['select'].play()
                    if event.key == pygame.K_RETURN and all(player_confirm):
                        self.load_level('map')
                    if event.key == pygame.K_ESCAPE:
                        return
                    if event.key == pygame.K_a:
                        if not confirm[0]:
                            self.choice[0] = (self.choice[0] + 1) % self.character_count
                        elif not player_confirm[0]:
                            self.player_choice[0] = (self.player_choice[0] + 1) % len(self.users)
                    if event.key == pygame.K_d:
                        if not confirm[0]:
                            self.choice[0] = (self.choice[0] - 1) % self.character_count
                        elif not player_confirm[0]:
                            self.player_choice[0] = (self.player_choice[0] - 1) % len(self.users)
                    if event.key == pygame.K_w:
                        if not confirm[0]:
                            confirm[0] = True
                        else:
                            player_confirm[0] = True
                    if event.key == pygame.K_s:
                        if player_confirm[0]:
                            player_confirm[0] = False
                        else:
                            confirm[0] = False
                    if event.key == pygame.K_LEFT:
                        if not confirm[1]:
                            self.choice[1] = (self.choice[1] + 1) % self.character_count
                        elif not player_confirm[1]:
                            self.player_choice[1] = (self.player_choice[1] + 1) % len(self.users)
                    if event.key == pygame.K_RIGHT:
                        if not confirm[1]:
                            self.choice[1] = (self.choice[1] - 1) % self.character_count
                        elif not player_confirm[1]:
                            self.player_choice[1] = (self.player_choice[1] - 1) % len(self.users)
                    if event.key == pygame.K_UP:
                        if not confirm[1]:
                            confirm[1] = True
                        else:
                            player_confirm[1] = True
                    if event.key == pygame.K_DOWN:
                        if player_confirm[1]:
                            player_confirm[1] = False
                        else:
                            confirm[1] = False

                for i, controller in enumerate(self.controllers):
                    if event.type == pygame.JOYHATMOTION:
                        if event.joy == controller.get_id():
                            direction = event.value
                            if any(value != 0 for value in direction):
                                self.sfx['select'].play()

                            if not confirm[i]:
                                self.choice[i] = (self.choice[i] + direction[0]) % self.character_count
                            elif not player_confirm[i]:
                                self.player_choice[i] = (self.player_choice[i] + direction[0]) % len(self.users)

                    if event.type == pygame.JOYBUTTONDOWN:
                        if event.joy == controller.get_id():
                            self.sfx['select'].play()
                            if event.button == 0:
                                if not confirm[i]:
                                    confirm[i] = True
                                else:
                                    player_confirm[i] = True
                            elif event.button == 1:
                                if player_confirm[i]:
                                    player_confirm[i] = False
                                elif confirm[i]:
                                    confirm[i] = False
                                elif all(not confirmed for confirmed in confirm):
                                    return
                        if event.button == 0 and all(player_confirm):
                            self.load_level('map')

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)

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

        self.players = [Player(self, (50, 50), (8, 15), 1), Player(self, (50, 50), (8, 15), 2)]

        self.players[0] = Player(self, (50, 50), (8, 15), 1)
        self.players[1] = Player(self, (50, 50), (8, 15), 2)

        spawn_points = self.tilemap.extract([('spawners', 0)])

        spawn = random.choice(spawn_points)
        self.players[0].pos = spawn['pos']
        self.players[0].air_time = 0
        spawn_points.remove(spawn)
        spawn = random.choice(spawn_points)
        self.players[1].pos = spawn['pos']
        self.players[1].air_time = 0
        spawn_points.remove(spawn)
        self.game()

    def pause(self):

        selection = 0

        title_font = self.font1.render('Paused', 0, 'white')

        menu_options = [self.game, self.options, self.main_menu]

        self.sfx['select'].play()
        
        menu_rects = [
            [self.green, (110, 70), (100, 30)],
            [self.green, (110, 110), (100, 30)],
            [self.green, (110, 150), (100, 30)],
        ]

        menu_text = [
            self.font2.render('Resume', 0, 'white'),
            self.font2.render('Options', 0, 'white'),
            self.font2.render('Main Menu', 0, 'white'),
        ]

        menu_text_pos = [
            ((menu_rects[0][1][0] + menu_rects[0][2][0] / 2) - menu_text[0].get_width()/2, (menu_rects[0][1][1] + menu_rects[0][2][1] / 2) - menu_text[0].get_height()/2),
            ((menu_rects[1][1][0] + menu_rects[1][2][0] / 2) - menu_text[1].get_width()/2, (menu_rects[1][1][1] + menu_rects[1][2][1] / 2) - menu_text[1].get_height()/2),
            ((menu_rects[2][1][0] + menu_rects[2][2][0] / 2) - menu_text[2].get_width()/2, (menu_rects[2][1][1] + menu_rects[2][2][1] / 2) - menu_text[2].get_height()/2),
        ]

        run = True

        while run:
            self.display.blit(self.assets['background'], (0,0))

            self.display.blit(title_font, ((320 - title_font.get_width())/2, 0))

            menu_rects[selection][0] = self.dark_green

            for rects in menu_rects:
                draw_rect(self.display, rects[0], rects[1], rects[2])

            for i in range(len(menu_text)):
                self.display.blit(menu_text[i], menu_text_pos[i])

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()

                if event.type == pygame.KEYDOWN:
                    self.sfx['select'].play()
                    if event.key == pygame.K_ESCAPE:
                        return
                    if event.key in (pygame.K_s, pygame.K_DOWN):
                        menu_rects[selection][0] = self.green
                        selection = (selection + 1) % len(menu_rects)
                    if event.key in (pygame.K_w, pygame.K_UP):
                        menu_rects[selection][0] = self.green
                        selection = (selection - 1) % len(menu_rects)
                    if event.key == pygame.K_RETURN:
                        menu_options[selection]()

                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        self.sfx['select'].play()
                        menu_options[selection]()
                    if event.button == 1:
                        return

                if event.type == pygame.JOYHATMOTION:
                    direction = event.value

                    menu_rects[selection][0] = self.green
                    selection = (selection - direction[1]) % len(menu_rects)
                    if direction[1] != 0:
                        self.sfx['select'].play()

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)

    def game(self):

        run = True
        self.sfx['lobby'].stop()

        while run:
            self.display.blit(self.assets['background'], (0,0))

            self.tilemap.render(self.display)

            self.players[0].update(self.tilemap, (self.movement[0][1]-self.movement[0][0], 0))
            self.players[0].render(self.display)
            self.players[1].update(self.tilemap, (self.movement[1][1]-self.movement[1][0], 0))
            self.players[1].render(self.display)

            for rect_data in self.rects.values():
                if 'size' in rect_data:
                    draw_rect(self.display, rect_data['color'], rect_data['pos'], rect_data['size'])
                else:
                    draw_rect(self.display, rect_data['color'], rect_data['pos'])

            for icons in self.icons.values():
                if 'size' in icons:
                    icon(self.display, icons['img'], icons['pos'], icons['size'])
                else:
                    icon(self.display, icons['img'], icons['pos'])

            for blits in self.blits.values():
                blits.update()
                blits.render(self.display)

            pygame.draw.rect(self.display, (255, 0, 0), (10, 30, 50, 10))
            pygame.draw.rect(self.display, (255, 0, 0), (260, 30, 50, 10))
            pygame.draw.rect(self.display, (0, 255, 0), (10, 30, 50*(self.players[0].health/100.), 10))
            pygame.draw.rect(self.display, (0, 255, 0), (260, 30, 50*(self.players[1].health/100.), 10))

            for attacker in self.players:
                for target in self.players:
                    if target != attacker:
                        if attacker.attacking and not attacker.hitting:
                            if attacker.attack_animation.frame in {3, 4, 5, 7, 8, 9}:
                                if pygame.Rect.colliderect(target.rect(), attacker.rect(alt=True)):
                                    target.health -= 10
                                    attacker.hitting = True
                                    self.sfx['hit'].play()
                        if abs(attacker.dashing) >= 100 and not attacker.hitting:
                            if pygame.Rect.colliderect(target.rect(), attacker.rect()):
                                target.health -= 20
                                attacker.hitting = True
                                self.sfx['hit'].play()

            if any(player.health <= 0 for player in self.players):
                for players in self.users:
                    self.player_stats[players]['gp'] += 1
                if self.players[0].health <= 0:
                    self.player_stats[self.users[1]]['w'] += 1
                    self.player_stats[self.users[0]]['l'] += 1
                else:
                    self.player_stats[self.users[1]]['l'] += 1
                    self.player_stats[self.users[0]]['w'] += 1
                self.load_level('map')

            for bomb in self.bombs:
                bomb[1][1] += 0.1
                bomb[0][0] += bomb[1][0]
                bomb[0][1] += bomb[1][1]

                entity_rect = pygame.Rect(bomb[0][0], bomb[0][1], self.assets['bomb'].get_width(), self.assets['bomb'].get_height())

                if bomb[0][1] >= 240:
                    self.bombs.remove(bomb)

                for rect in self.tilemap.physics_rects_around(bomb[0]):
                    if entity_rect.colliderect(rect) and bomb[0][1] < 240:
                        self.bomb_effect.append([bomb[0], 0])
                        for _ in range(30):
                            centrepoint = (bomb[0][0] + self.smoke_effect_radius * random.uniform(-1, 1) * 0.75, bomb[0][1] + self.smoke_effect_radius * random.uniform(-1, 1) * 0.75)
                            max_r = 15 * random.random()
                            self.smoke.append([centrepoint, max_r, 0, 0]) # (/, /, current radius, time)
                        self.bombs.remove(bomb)
                        break

                self.display.blit(self.assets['bomb'], bomb[0])

            for bomb_effect in self.bomb_effect:
                bomb_effect[1] += 1
                if bomb_effect[1] >= 300:
                    self.bomb_effect.remove(bomb_effect)

            for smoke in self.smoke:
                smoke[3] += 1
                if smoke[3] < 300:
                    smoke[2] = min(smoke[2] + 0.5, smoke[1])
                else:
                    smoke[2] = max(smoke[2] - 0.5, 0)
                if smoke[2] == 0:
                    self.smoke.remove(smoke)
                pygame.draw.circle(self.display, (200, 200, 200), smoke[0], smoke[2])

            for player in self.players:
                hitbox = player.rect()
                smoking = False
                for bomb_effect in self.bomb_effect:
                    if hitbox.top + self.player_size[1] >= bomb_effect[0][1] and hitbox.top <= bomb_effect[0][1]: #level in the y
                        if hitbox.left >= bomb_effect[0][0]: #level and to the right
                            if abs(hitbox.left - bomb_effect[0][0]) <= self.smoke_effect_radius:
                                smoking = True
                                break
                        else: #level and to the left
                            if abs(hitbox.left + self.player_size[0] - bomb_effect[0][0]) <= self.smoke_effect_radius:
                                smoking = True
                                break
                    elif hitbox.left + self.player_size[0] >= bomb_effect[0][0] and hitbox.left <= bomb_effect[0][0]: #level in the x
                        if hitbox.top >= bomb_effect[0][1]: #level and below
                            if abs(hitbox.top - bomb_effect[0][1]) <= self.smoke_effect_radius:
                                smoking = True
                                break
                        else: #level and above
                            if abs(hitbox.top + self.player_size[1] - bomb_effect[0][1]) <= self.smoke_effect_radius:
                                smoking = True
                                break
                    elif hitbox.left > bomb_effect[0][0]: #to the right
                        if hitbox.top > bomb_effect[0][1]: #below
                            if math.hypot(abs(hitbox.left-bomb_effect[0][0]), abs(hitbox.top-bomb_effect[0][1])) <= self.smoke_effect_radius:
                                smoking = True
                                break
                        else: #above
                            if math.hypot(abs(hitbox.left-bomb_effect[0][0]), abs(hitbox.top + self.player_size[1]-bomb_effect[0][1])) <= self.smoke_effect_radius:
                                smoking = True
                                break
                    else: #to the left
                        if hitbox.top > bomb_effect[0][1]: #below
                            if math.hypot(abs(hitbox.left + self.player_size[0]-bomb_effect[0][0]), abs(hitbox.top-bomb_effect[0][1])) <= self.smoke_effect_radius:
                                smoking = True
                                break
                        else: #above
                            if math.hypot(abs(hitbox.left + self.player_size[0]-bomb_effect[0][0]), abs(hitbox.top + self.player_size[1]-bomb_effect[0][1])) <= self.smoke_effect_radius:
                                smoking = True
                                break
                if smoking:
                    player.health -= 0.5

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.pause()
                        self.sfx['select'].play()

                    if event.key == pygame.K_w:
                        if self.players[0].jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_a:
                        self.movement[0][0] = True
                    if event.key == pygame.K_d:
                        self.movement[0][1] = True
                    if event.key == pygame.K_e:
                        if self.players[0].attack():
                            self.blits['p1_attack'].regenerate()
                            self.sfx['dash'].play()
                    if event.key == pygame.K_r:
                        if self.players[0].dash():
                            self.blits['p1_dash'].regenerate()
                            self.sfx['dash'].play()
                    if event.key == pygame.K_q:
                        if self.players[0].bomb():
                                    self.blits['p1_bomb'].regenerate()

                    if event.key == pygame.K_UP:
                        if self.players[1].jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_LEFT:
                        self.movement[1][0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1][1] = True
                    if event.key in (pygame.K_RCTRL, pygame.K_l):
                        if self.players[1].attack():
                            self.blits['p2_attack'].regenerate()
                            self.sfx['dash'].play()
                    if event.key == pygame.K_RSHIFT:
                        if self.players[1].dash():
                            self.blits['p2_dash'].regenerate()
                            self.sfx['dash'].play()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0][0] = False
                    if event.key == pygame.K_d:
                        self.movement[0][1] = False

                    if event.key == pygame.K_LEFT:
                        self.movement[1][0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1][1] = False

                for i, controller in enumerate(self.controllers):
                    if event.type == pygame.JOYAXISMOTION:
                        if event.joy == controller.get_id():
                            axis = event.axis
                            axis_value = event.value

                            #print(f"Controller {controller.get_id()} axis {axis} moved to {axis_value}")

                            if axis == 0:
                                #print(f"Controller {controller.get_id()} movement")
                                if axis_value > 0.2:
                                    self.movement[i][1] = True
                                    self.movement[i][0] = False
                                elif axis_value < -0.2:
                                    self.movement[i][0] = True
                                    self.movement[i][1] = False
                                else:
                                    self.movement[i][0] = False
                                    self.movement[i][1] = False

                            #print(f"Movement for controller {controller.get_id()}: {self.movement[i]}")

                    if event.type == pygame.JOYBUTTONDOWN:
                        if event.joy == controller.get_id():
                            if event.button == 7: # menu button
                                self.pause()
                            if event.button == 0:
                                if self.players[i].jump():
                                    self.sfx['jump'].play()
                            if event.button == 1:
                                if self.players[i].attack():
                                    self.blits['p' + str(controller.get_id() + 1) + '_attack'].regenerate()
                                    self.sfx['dash'].play()
                            if event.button == 2:
                                if self.players[i].dash():
                                    self.blits['p' + str(controller.get_id() + 1) + '_dash'].regenerate()
                                    self.sfx['dash'].play()
                            if event.button == 3:
                                if self.players[i].bomb():
                                    self.blits['p' + str(controller.get_id() + 1) + '_bomb'].regenerate()

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)

if __name__ == '__main__':
    Game().main_menu()