import pygame


class Event:
    def __init__(self, game, player, opponent):
        self.game = game
        self.player = player
        self.opponent = opponent

    def attack(self):
        if self.player.attacking:
            if self.player.colliderect(self.player.attack_animation.img()):
                pass