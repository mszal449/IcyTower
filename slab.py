import pygame
from CONST import *
class Slab:
    def __init__(self, pos, index, width):
        self.pos = pos
        self.index = index
        self.width = width

        # hitbox schodka
        self.rect = pygame.Rect(self.pos.x, self.pos.y, SLAB_BLOCK_WIDTH * width , 16)

        # sprawdzenie czy punkty za minięcie schodka zostały naliczone
        self.points_added = False