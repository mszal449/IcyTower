import pygame
from CONST import *
from properties import *


class Character:
    def __init__(self):
        self.pos = pygame.Vector2(148, 156)
        self.animation = "idle"
        self.actual_frame = 0
        self.animation_timer = 0
        self.rect = pygame.Rect(self.pos.x + 12, self.pos.y, 12, 24)
        self.velocity = pygame.Vector2(0, 0)
        self.is_standing = True
        self.jump_mult = 1 # mnożnik wysokości skoku
        self.rotating_speed = 0
        self.angle = 0
        self.walking_speed = 0
        self.in_combo = False
        self.sounds_to_play = []

    def update(self, dt):
        self.sounds_to_play = []

        # liczenie mnożnika skoku
        if self.velocity.x < 0:
            self.jump_mult = 0.5 * self.velocity.x
        else:
            self.jump_mult = -0.5 * self.velocity.x

        if self.jump_mult < -1:
            self.jump_mult *= 2

        # reakcja na wciśnięcie przycisku
        keys = pygame.key.get_pressed()

        # ruch w bok
        if keys[pygame.K_RIGHT]:
            if self.rect.right < 249:
                self.velocity.x += ACCELERATION * dt

        elif keys[pygame.K_LEFT]:
            if self.rect.left > 70:
                self.velocity.x -= ACCELERATION * dt

        # zwalnianie
        else:
            if self.velocity.x >= 1.5 * DECELERATION and self.velocity.x > 0:
                self.velocity.x -= DECELERATION * dt

            elif self.velocity.x > 0:
                self.velocity.x = 0

            elif self.velocity.x < 1.5 * DECELERATION and self.velocity.x < 0:
                self.velocity.x += DECELERATION * dt

            elif self.velocity.x < 0:
                self.velocity.x = 0

        if self.rect.left < 70:
            self.pos.x = 66
            self.velocity.x *= -WALL_BOUNCE
            self.sounds_to_play.append("bounce")

        elif self.rect.right > 249:
            self.pos.x = 230
            self.velocity.x *= -WALL_BOUNCE
            self.sounds_to_play.append("bounce")

        # skok
        if keys[pygame.K_SPACE]:
            if self.is_standing:
                self.angle = 0
                self.velocity.y = JUMP_SPEED + self.jump_mult
                self.is_standing = False
                self.animation = "jump"
                self.rotating_speed = (abs(self.velocity.x) + abs(self.velocity.y)) * ROTATION_SPEED * dt
                if abs(self.velocity.x) + abs(self.velocity.y) > ROTATION_START:
                    self.sounds_to_play.append("combo")
                self.sounds_to_play.append("jump")

        self.pos.x += self.velocity.x * dt
        self.rect.x = self.pos.x + 6
        self.pos.y += self.velocity.y * dt
        self.rect.y = self.pos.y
        self.velocity.y += GRAVITY * dt

        self.update_animation(dt)

    def update_animation(self, dt):
        if not self.is_standing:
            if abs(self.velocity.x) + abs(self.velocity.y) > ROTATION_START or self.animation == "rotate":
                self.in_combo = True
                self.rotating_speed -= self.rotating_speed / ROTATE_SPEED_SMOOTH * dt
                self.rotating_speed = abs(self.rotating_speed)
                if self.velocity.x > 0:
                     self.rotating_speed *= -1
                self.animation = "rotate"
                self.angle += self.rotating_speed
            else:
                self.in_combo = False
                if self.velocity.x == 0:
                    self.animation = "jump-up"
                else:
                    if abs(self.velocity.y) < JUMP_MIDDLE_ANIMATION_TIME:
                        self.animation = "jump-middle"
                    elif self.velocity.y < JUMP_MIDDLE_ANIMATION_TIME:
                        self.animation = "jump-start"
                    else:
                        self.animation = "jump-end"
        else:
            if self.velocity.x == 0:
                self.animation = "idle"
            else:
                self.animation = "walk"

            self.animation_timer += dt
            if self.animation_timer >= FRAMERATE / ANIMATION_SPEED[self.animation] * dt:
                self.actual_frame += 1

                self.animation_timer = 0
                if self.animation == "walk" and self.actual_frame % 2 == 0:
                    self.sounds_to_play.append("step")


        if self.actual_frame >= ANIMATION_FRAME_NUMBERS[self.animation]:
            self.actual_frame = 0
