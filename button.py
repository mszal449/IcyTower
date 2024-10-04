import pygame
import random
from CONST import *


class Button:
    def __init__(self, x, y, text, clicable=True):
        self.text = pygame.font.Font('font.ttf', BUTTON_FONT_SIZE).render(text, True, (0, 0, 0))
        self.text_rect = self.text.get_rect()
        self.text_rect.center = (x, y)
        self.rect = pygame.Rect(0, 0, BUTTON_SIZE[0], BUTTON_SIZE[1])
        self.rect.center = (x, y)
        self.state = "normal"
        self.clicked = False
        self.clickable = clicable
        self.active = True
        self.sound_to_play = None

    def update(self, mouse, sounds):
        self.sound_to_play = None
        # sprawdzanie czy przycisk jest klikniety czy najechalismy na niego myszka
        if self.clickable and self.active:
            if self.rect.colliderect(mouse.rect):
                if mouse.click_switch:
                    if self.state == "normal":
                        self.sound_to_play = "touch"
                    self.state = "touched"
                else:
                    self.state = "clicked"
                if mouse.click and not self.clicked:
                    self.state = "clicked"
                    self.clicked = True
                    self.sound_to_play = "click"
            else:
                self.state = 'normal'
        if not mouse.click:
            self.clicked = False
