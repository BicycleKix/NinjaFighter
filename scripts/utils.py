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

def draw_rect(surf, color, pos, size=(18, 18)):
    pygame.draw.rect(surf, color, pygame.Rect(pos[0], pos[1], size[0], size[1]))

def icon(surf, img, pos, size=(14, 14)):
    surf.blit(pygame.transform.scale(img, size), pos)

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
    
class Blit:
    def __init__(self, game, pos, size=(16, 16), cooldown=60):
        self.game = game
        self.size = size
        self.cooldown = cooldown
        self.pos = pos

        self.sillhouette = 0
        self.regeneration_speed = self.size[1] / self.cooldown
        self.regenerating = False

        self.surface = pygame.Surface((320, 240), pygame.SRCALPHA)

    def regenerate(self):
        if not self.regenerating:
            self.regenerating = True
            self.sillhouette = self.size[1]

    def update(self):
        if self.regenerating:
            self.sillhouette = max(0, self.sillhouette - self.regeneration_speed)
            if self.sillhouette == 0:
                self.regenerating = False

    def render(self, surf):
        self.surface.fill((0, 0, 0, 0))
        pygame.draw.rect(self.surface, (255, 255, 255, 100), pygame.Rect(0, 0, self.size[0], int(self.sillhouette)))
        surf.blit(self.surface, self.pos)