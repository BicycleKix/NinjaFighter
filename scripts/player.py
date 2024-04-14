import pygame

from scripts.particle import Particle
class Player:
    def __init__(self, game, pos, size, char):
        self.game = game
        self.pos = list(pos)
        self.size = size
        self.char = char

        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        self.action = ''
        self.anim_offset = (-13, -9)
        self.flip = False
        self.set_action('idle')

        self.last_movement = [0, 0]

        self.air_time = 0
        self.jumps = 1
        self.dashing = 0
        self.attacking = 0

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action, alt=False):
        if action != self.action:
            self.action = action
            if alt:
                self.animation = self.game.assets[self.action].copy()
            else:
                self.animation = self.game.player_assets['player' + str(self.char + 1)][self.action].copy()

    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        self.air_time += 1

        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.last_movement = movement

        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        self.animation.update()

        if self.pos[1] > 240:
            pass

        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1

        if self.air_time > 4:
            self.set_action('jump')
        elif movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        if self.attacking:
            self.attacking = max(0, self.attacking - 1)

        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1

        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

    def render(self, surf):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] + self.anim_offset[0], self.pos[1] + self.anim_offset[1]))

    def jump(self):
        if self.jumps:
            self.velocity[1] = -3.5
            self.jumps -= 1
            self.air_time = 5
            return True
        
    def dash(self):
        if not self.dashing:
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60

    def attack(self):
        if not self.attacking:
            self.attacking = 30
            self.game.swords.append(Particle(self.game, 'attack', self.game.player1.pos, self.game.player1.velocity))