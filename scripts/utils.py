import os

import pygame

BASE_IMG_PATH = 'data/images/'

def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0,0,0))
    return img

def load_png(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert_alpha()
    return img

def load_images(path, alt=False):
    images = []
    if alt:
        for img_name in os.listdir(BASE_IMG_PATH + path):
            images.append(load_png(path + '/' + img_name))
    else:
        for img_name in os.listdir(BASE_IMG_PATH + path):
            images.append(load_image(path + '/' + img_name))
    return images

def load_player(player):
    sprite = []
    for folder in os.listdir(BASE_IMG_PATH + player):
        sprite.append(load_images(player + '/' + folder))

class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)
    
    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True
    
    def img(self):
        return self.images[int(self.frame / self.img_duration)]
    
class Blits:
    def __init__(self, game, pos, size=(16, 16), cooldown=60):
        self.game = game
        self.size = size
        self.cooldown = cooldown
        self.pos = pos

        self.sillhouette = 0

    def update(self):
        self.sillhouette = min(self.size[1], self.sillhouette + int(self.size[1]/self.cooldown))

    def render(self, surf):
        pygame.draw.rect(surf, (0, 0, 0, 155), pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.sillhouette))