import random
from CONST import *
from properties import *

class Particle:
    def __init__(self, pos):
        self.pos = pos
        self.pos.x += CHARACTER_FRAME_SIZE // 2 + random.randint(-PARTICLE_START_POINT_RANDOM,PARTICLE_START_POINT_RANDOM)
        self.pos.y += CHARACTER_FRAME_SIZE + random.randint(-PARTICLE_START_POINT_RANDOM,PARTICLE_START_POINT_RANDOM)
        self.opacity = 255
        color = random.choice(PARTICLE_COLORS)
        self.color = (color[0],color[1],color[2],self.opacity)
        self.size = random.randint(PARTICLE_SIZE[0],PARTICLE_SIZE[1])
        self.velocity = 0


    def update(self, dt):
        self.velocity += GRAVITY * dt * PARTICLE_SPEED
        self.pos.y += self.velocity * dt
        self.opacity -= dt *  PARTICLE_OPACITY_SPEED
        self.opacity = max(0,self.opacity)
        self.color = (self.color[0], self.color[1], self.color[2], self.opacity)


