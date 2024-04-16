class Particle:
    def __init__(self, game, p_type, pos, velocity=[0,0], frame=0):
        self.game = game
        self.type = p_type
        self.pos = list(pos)
        self.velocity = list(velocity)
        self.animation = self.game.assets[self.type].copy()
        self.animation.frame = frame

    def update(self):
        kill = False
        if self.animation.done:
            kill = True

        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        self.animation.update()

        return kill
    
    def render(self, surf, offset=(0,0)):
        img = self.animation.img()
        surf.blit(img, self.pos)

class Sword:
    def __init__(self, game, player):
        self.game = game
        self.player = player
        self.animation = self.game.assets['attack']

    def update(self):
        kill = False
        if self.animation.done:
            kill = True

        self.pos = self.player.pos
        self.animation.update()
        
        return kill