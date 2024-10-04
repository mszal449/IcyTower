import pygame
from CONST import *


class Slider:
    def __init__(self, pos, length):
        self.pos = pos
        self.length = length
        self.rect = pygame.Rect(pos.x, pos.y, length, SLIDER_HEIGHT)
        self.button_rect = pygame.Rect(pos.x + (length - SLIDER_BUTTON_SIZE[0]) // 2, pos.y - (SLIDER_BUTTON_SIZE[1] - SLIDER_HEIGHT) // 2, SLIDER_BUTTON_SIZE[0], SLIDER_BUTTON_SIZE[1])
        self.touched = False
        self.activated = False
        self.value = START_VOLUME

    def update(self, mouse):
        self.touched = self.button_rect.colliderect(mouse.rect)
        self.activated = not mouse.click_switch and (self.touched or self.activated)
        if self.activated:
            self.button_rect.x = max(min(mouse.rect.x, self.pos.x + self.length - SLIDER_BUTTON_SIZE[0]), self.pos.x)
            self.value = (self.button_rect.x - self.pos.x) / (self.length - SLIDER_BUTTON_SIZE[0])
