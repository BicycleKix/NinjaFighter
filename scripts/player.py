import pygame

class Player:
    def __init__(self, game, pos, size, char):
        self.game = game
        self.pos = list(pos)
        self.size = size
        self.char = char

        self.dead = False

        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        self.action = ''
        self.anim_offset = (-1, 0)
        self.attack_offset = (0, -5)
        self.attack_offset_flip = (-11, -5)
        self.flip = False
        self.set_action('idle')

        self.last_movement = [0, 0]

        self.air_time = 0
        self.jumps = 1
        self.dashing = 0
        self.attacking = False

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    
    def set_action(self, action, alt=False):
        if action != self.action:
            self.action = action
            if alt:
                self.animation = self.game.assets[self.action].copy()
            else:
                self.animation = self.game.player_assets['player' + str(self.char)][self.action].copy()

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

        self.attacking = max(0, self.attacking - 1)

        if self.pos[1] > 240:
            self.dead = True

        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1

        if abs(self.dashing) > 170:
            self.set_action('dash')
        elif self.air_time > 4:
            self.set_action('jump')
        elif movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 160:
            self.velocity[0] = abs(self.dashing) / self.dashing * 5
            if abs(self.dashing) == 161:
                self.velocity[0] *= 0.1

        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

    def render(self, surf):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] + self.anim_offset[0], self.pos[1] + self.anim_offset[1]))

        if self.attacking > 35:
            if not self.attack_animation.done:
                self.attack_animation.update()
                if self.flip:
                    surf.blit(pygame.transform.flip(self.attack_animation.img(), self.flip, False), (self.pos[0] + self.attack_offset_flip[0], self.pos[1] + self.attack_offset_flip[1]))
                else:
                    surf.blit(pygame.transform.flip(self.attack_animation.img(), self.flip, False), (self.pos[0] + self.attack_offset[0], self.pos[1] + self.attack_offset[1]))

    def jump(self):
        if self.jumps:
            self.velocity[1] = -3.5
            self.jumps -= 1
            self.air_time = 5
            return True
        
    def dash(self):
        if not self.dashing and self.attacking <= 51:
            if self.flip:
                self.dashing = -180
            else:
                self.dashing = 180
            return True

    def attack(self):
        if not self.attacking and self.dashing <= 160:
            self.attacking = 90
            self.attack_animation = self.game.assets['attack'].copy()
            return True