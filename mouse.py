import pygame
from CONST import *

class Mouse:
    def __init__(self):
        self.rect = pygame.Rect(0,0,1,1)
        self.click = False
        self.click_switch = True

    def update(self, screen_size):
        # pos
        pos = pygame.mouse.get_pos()
        self.rect.x = pos[0] * DRAW_SCREEN_SIZE[0] // screen_size[0]
        self.rect.y = pos[1] * DRAW_SCREEN_SIZE[1] // screen_size[1]

        # button
        if pygame.mouse.get_pressed()[0]:
            if self.click_switch:
                self.click = True
                self.click_switch = False
            else:
                self.click = False
        else:
            self.click_switch = True
            self.click = False
