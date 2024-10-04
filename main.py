import os
import pygame
import random
import math
from character import Character
from mouse import Mouse
from slab import Slab
from particle import Particle
from CONST import *
from properties import *
from button import Button
from slider import Slider


class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()  # inicjalizacja pygame
        pygame.mixer.set_num_channels(CHANNEL_QUANTITY)
        pygame.mixer_music.load("soundtrack.wav")
        self.is_running = True  # jezeli zmienna jest prawdziwa to program działa

        # wczytanie opcji
        self.options_values = {}
        data = open("options.txt", "r").readlines()
        for line in data:
            l = line.rstrip().split(" ")
            if l[0] == "volume":
                self.options_values[l[0]] = float(l[1])
            else:
                self.options_values[l[0]] = l[1]


        # inicjalizacja ekranu
        self.max_screen_size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        if self.options_values["resolution"] == "fullscreen":
            self.screen_size = self.max_screen_size
            self.screen = pygame.display.set_mode(self.screen_size, pygame.FULLSCREEN)
        elif self.options_values["resolution"] == "1080p":
            self.screen_size = (1920, 1080)
            self.screen = pygame.display.set_mode(self.screen_size)
        elif self.options_values["resolution"] == "720p":
            self.screen_size = (1280, 720)
            self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.mode_ok(self.screen_size)
        self.draw_screen = pygame.Surface(DRAW_SCREEN_SIZE)
        pygame.display.set_caption("Icy Tower")

        # wywołanie wczytywania zasobów
        self.textures = {}
        self.load_textures()
        self.sounds = {}
        self.load_sounds()
        self.mixer_channels = {}
        self.init_sounds()
        self.font = pygame.font.Font("font.ttf", 8)

        # inicjalizacja zegara
        self.clock = pygame.time.Clock()
        self.dt = 1

        # utworzenie obiektu myszki
        self.mouse = Mouse()

        # zmienna przechowująca informację jaka "scena" jest aktualnie uruchuchomiona
        self.scene = self.main_menu

        # utworzenie ludzika
        self.character = Character()

        # inicjalizacja menu
        self.buttons = {}
        self.init_menu()
        self.esc_pressed = False


        # glowna petla gry
        while self.is_running:
            self.check_events()
            self.mouse.update(self.screen_size)
            self.scene()
            self.refresh_screen()

        file = open("options.txt", "w")
        for key in self.options_values:
            file.write(key + " " + str(self.options_values[key]) + "\n")
        file.close()

    def init_sounds(self):
        for i, name in enumerate(self.sounds):
            self.mixer_channels[name] = pygame.mixer.Channel(i)
        self.set_volume(self.options_values["volume"])
        pygame.mixer_music.play(-1)

    def set_volume(self, volume):
        pygame.mixer_music.set_volume(max(volume + MUSIC_VOLUME_DIFFERENCE, 0))
        for channel_name in self.mixer_channels:
            self.mixer_channels[channel_name].set_volume(volume)

    def init_game(self):
        self.game_timer = 0
        self.game_started = False
        self.game_end = 0
        self.game_over_pos = GAME_OVER_START_POS
        self.button_pressed = False

        # zmienna przechowująca informacje o aktualnych przesunięciu kamery
        self.scroll = 0
        self.target_scroll = 0
        self.scroll_speed = CAMERA_SCROLL_SPEED[self.options_values["difficulty"]]
        self.scroll_timer = 0

        # utworzenie listy schodków
        self.slabs = self.initiate_slabs()

        # utworzenie okna
        self.window = self.initiate_window()

        # utworzenie licznika wyniku
        self.score = 0
        self.combo_steps = 0
        self.jump_height = 0
        self.current_index = 0
        self.last_index = 0
        self.combo_timer = 0
        self.timer_start = False
        self.combo_caption_timer = 0
        self.combo_caption_steps = 0
        self.combo_caption_pos = 0

        # particle
        self.particles = []

        # zmienne animacji
        self.actual_clock_distortion_x = 0
        self.actual_clock_distortion_y = 0

        self.character.pos = pygame.Vector2(148, 120)
        self.score = 0
        self.floors = 0
        self.max_combo = 0

    def init_menu(self):

        # przyciski menu głównego
        menu_buttons = {}
        menu_buttons["exit"] = Button(262, 144, 'Exit')
        menu_buttons["options"] = Button(262, 122, 'Options')
        menu_buttons["high_score"] = Button(262, 101, 'High scores')
        menu_buttons["start_game"] = Button(262, 79, 'Start game')
        self.buttons["menu"] = menu_buttons

        # przyciski zmiany rozdzielczości
        options_buttons = {}
        options_buttons["720p"] = Button(48, 36, '720p')
        options_buttons["720p"].active = False
        options_buttons["1080p"] = Button(48, 36, '1080p')
        options_buttons["1080p"].active = False
        options_buttons["fullscreen"] = Button(48, 36, 'fullscreen')
        options_buttons["fullscreen"].active = False
        options_buttons["resolution"] = Button(48, 18, 'Resolution', False)
        options_buttons[self.options_values["resolution"]].active = True

        # przyciski właczania napisów po combo
        options_buttons["combo_on"] = Button(240, 36, 'ON')
        options_buttons["combo_on"].active = False
        options_buttons["combo_off"] = Button(240, 36, 'OFF')
        options_buttons["combo_off"].active = False
        options_buttons["combo_caption"] = Button(240, 18, 'Combo Caption', False)
        options_buttons["combo_" + self.options_values["combo_caption"]].active = True

        # przyciski zmiany particle
        options_buttons["particles"] = Button(144, 18, 'Particles', False)
        options_buttons["none"] = Button(144, 36, 'none')
        options_buttons["none"].active = False
        options_buttons["some"] = Button(144, 36, 'some')
        options_buttons["some"].active = False
        options_buttons["lots"] = Button(144, 36, 'lots')
        options_buttons["lots"].active = False
        options_buttons[self.options_values["particles"]].active = True

        # przyciski poziomu trudności
        options_buttons["hard"] = Button(240, 81, 'Hard')
        options_buttons["medium"] = Button(144, 81, 'Medium')
        options_buttons["easy"] = Button(48, 81, 'Easy')
        options_buttons["difficulty"] = Button(96, 63, 'Difficulty', False)

        # przycisk od głośności
        options_buttons["volume"] = Button(96, 108, 'Volmue', False)
        options_buttons["exit"] = Button(262, 144, 'Exit')
        self.buttons["options"] = options_buttons

        # przycisk tytułowy high score
        high_score_buttons = {}
        high_score_buttons["high_score"] = Button(112, 18, 'High scores', False)
        high_score_buttons["exit"] = Button(262, 144, 'Exit')
        self.buttons["high_score"] = high_score_buttons

        # suwak głośności
        self.volume_slider = Slider(pygame.Vector2((46, 130)), 100)

    def initiate_slabs(self):
        slabs = [Slab(pygame.Vector2(66, 165), 0,
                      12)]  # zaczynamy od schodka o indeksie 1, żeby działała funkcja update_slabs()
        for i in range(1, 8):
            width = random.randint(3, MAX_SLAB_WIDTH[self.options_values["difficulty"]])
            position_x = random.randint(0, 8)
            if position_x + width > 11:
                position_x -= (position_x + width - 11)
            slabs.append(Slab(pygame.Vector2(position_x * SLAB_BLOCK_WIDTH + 70, slabs[i - 1].pos.y - SLABS_DISTANCE),
                              slabs[i - 1].index + 1, width))
        return slabs

    def update_slabs(self):
        if (self.slabs[0].index + 1) * SLABS_DISTANCE < self.scroll:
            # usunięcie dolnego schodka
            self.slabs.pop(0)

            # dodanie górnego schodka
            width = random.randint(3, MAX_SLAB_WIDTH[self.options_values["difficulty"]])
            position_x = random.randint(0, 8)
            # ustawienie długości schodka tak, aby tabliczka z indeksem była po środku
            if (self.slabs[len(self.slabs) - 1].index % 10 == 9) and width % 2 == 0:
                width += 1
            # sprawdzenie, czy schodek nie wychodzi poza krawędź
            if position_x + width > 11:
                position_x -= (position_x + width - 11)
            # każda platforma przy nowym poziomie jest pełnej długości
            if self.slabs[len(self.slabs) - 1].index % BIG_SLAB_DISTANCE == BIG_SLAB_DISTANCE - 1:
                width = 13
                position_x = -0.8
            self.slabs.append(Slab(pygame.Vector2(position_x * SLAB_BLOCK_WIDTH + 70,
                                                  self.slabs[len(self.slabs) - 1].pos.y - SLABS_DISTANCE),
                                   self.slabs[len(self.slabs) - 1].index + 1, width))

    def initiate_window(self):
        position_x = random.randint(320 // 2 + 32, 320 - 70 - 32)
        position_y = -WINDOW_DISTANCE
        return pygame.Vector2(position_x, position_y)

    def update_window(self):
        if -self.window.y < (self.scroll // PARALLAX_DEPTH) - 180:
            self.window.x = random.randint(320 // 2 + 32, 320 - 70 - 32)
            self.window.y -= WINDOW_DISTANCE

    def load_textures(self):
        # wczytywanie tekstur do słownika "textures"

        for texture_name in os.listdir("textures"):
            if texture_name != "character.png":
                texture = pygame.image.load("textures/" + texture_name)
                self.textures[texture_name.replace(".png", "")] = texture

    def load_sounds(self):
        for folder in os.listdir("sounds"):
            sounds = []
            for sound in os.listdir("sounds/" + folder):
                sounds.append(pygame.mixer.Sound("sounds/" + folder + "/" + sound))
            self.sounds[folder] = sounds

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            if not self.esc_pressed:
                if self.scene == self.main_menu:
                    self.is_running = False
                else:
                    self.scene = self.main_menu
            self.esc_pressed = True
        else:
            self.esc_pressed = False

    def game(self):
        if self.game_end > SCREEN_SHAKE_DURATION + SCREEN_SHAKE_INTERLUDE:
            if pygame.key.get_pressed()[pygame.K_SPACE]:

                # Wczytywanie najwyzszych wynikow z pliku
                with open("high_score.txt", "r") as f:
                    lines = f.readlines()
                    numbers = [int(line.strip()) for line in lines]
                    numbers.append(self.score)
                    numbers = sorted(numbers, reverse=True)
                    numbers = numbers[:10]

                # Aktualizowanie pliku wraz z nowym wynikiem
                with open("high_score.txt", "w") as file:
                    # Write the new content to the file
                    for i in range(len(numbers)):
                        file.write(str(numbers[i]) + "\n")

                # Zmiana sceny
                self.scene = self.main_menu
        else:
            # odswiezenie ludzika
            self.character.update(self.dt)
            for sound in self.character.sounds_to_play:
                self.mixer_channels[sound].play(random.choice(self.sounds[sound]))

            # odświeżenie listy schodków
            self.update_slabs()

            # odświeżenie listy okien
            self.update_window()

            # sprawdzenie kolizji z otoczeniem
            self.check_collisions()

            # sprawdzenie wyniku
            self.score_counting()

            # odswiezanie scrolla
            self.update_scroll()

            if self.combo_caption_steps >= list(COMBO_CAPTION_TYPES.keys())[0]:
                if self.combo_caption_timer == 0:
                    self.mixer_channels["combo_get"].play(random.choice(self.sounds["combo_get"]))
                self.combo_caption_timer += self.dt
                if self.combo_caption_timer > COMBO_CAPTION_TIME:
                    self.combo_caption_timer = 0
                    self.combo_caption_steps = 0
                    self.combo_caption_pos = 0
            else:
                self.combo_caption_steps = 0
                self.combo_caption_pos = 0

            if self.character.animation == "rotate":
                if self.options_values["particles"] != "none":
                    self.particle_timer = 0
                    for i in range(max(int(PARTICLE_SPAWN_AMOUNT[self.options_values["particles"]] * self.dt), 1)):
                        self.particles.append(Particle(self.character.pos.copy()))

            for particle in self.particles:
                particle.update(self.dt)
                if particle.pos.y + self.scroll > 180 or particle.opacity == 0:
                    self.particles.remove(particle)

            if self.game_end < SCREEN_SHAKE_INTERLUDE and self.character.pos.y + self.scroll > 180 + UNDER_SCREEN_TOLERANCE:
                self.draw_game(draw_score=False)
                self.draw_screen_copy = self.draw_screen.copy()
                if self.game_end == 0:
                    self.mixer_channels["game_over"].play(self.sounds["game_over"][0])
                self.game_end += self.dt
            elif self.game_end >= SCREEN_SHAKE_INTERLUDE:
                self.game_end += self.dt
                self.game_over_pos += (GAME_OVER_POS - self.game_over_pos) / CAMERA_SMOOTH * self.dt
                self.draw_screen_shake()
            else:
                self.draw_game()

    def update_scroll(self):
        if self.game_started:
            self.game_timer += self.dt
            self.scroll_timer += self.dt
            if self.scroll_timer >= TIME_SPEED_UP_INTERLUDE[self.options_values["difficulty"]]:
                self.scroll_timer = 0
                self.scroll_speed *= SPEED_UP_MULTIPLIER[self.options_values["difficulty"]]
        if self.game_timer > 0:
            self.target_scroll += self.dt * self.scroll_speed
        self.target_scroll = max(self.target_scroll, -self.character.pos.y + CAMERA_SCROLL_SHIFT)
        self.scroll += (self.target_scroll - self.scroll) / CAMERA_SMOOTH * self.dt

    def main_menu(self):

        self.update_buttons("menu")

        if self.buttons["menu"]["start_game"].clicked:
            self.init_game()
            self.scene = self.game
        elif self.buttons["menu"]["exit"].clicked:
            self.is_running = False
        elif self.buttons["menu"]["options"].clicked:
            self.scene = self.options
        elif self.buttons["menu"]["high_score"].clicked:
            self.scene = self.high_score

        self.draw_main_menu()

    def options(self):
        self.update_buttons("options")
        self.volume_slider.update(self.mouse)
        self.options_values["volume"] = self.volume_slider.value
        self.set_volume(self.options_values["volume"])

        if self.buttons["options"]["exit"].clicked:
            self.scene = self.main_menu
        elif self.buttons["options"]["combo_on"].clicked:
            self.options_values["combo_caption"] = "off"
            self.buttons["options"]["combo_on"].active = False
            self.buttons["options"]["combo_off"].active = True
        elif self.buttons["options"]["combo_off"].clicked:
            self.options_values["combo_caption"] = "on"
            self.buttons["options"]["combo_off"].active = False
            self.buttons["options"]["combo_on"].active = True
        elif self.buttons["options"]["720p"].clicked:
            self.screen_size = (1920, 1080)
            pygame.display.set_mode(self.screen_size)
            self.options_values["resolution"] = "1080p"
            self.buttons["options"]["720p"].active = False
            self.buttons["options"]["1080p"].active = True
        elif self.buttons["options"]["1080p"].clicked:
            self.screen_size = self.max_screen_size
            pygame.display.set_mode(self.screen_size, pygame.FULLSCREEN)
            self.options_values["resolution"] = "fullscreen"
            self.buttons["options"]["1080p"].active = False
            self.buttons["options"]["fullscreen"].active = True
        elif self.buttons["options"]["fullscreen"].clicked:
            self.screen_size = (1280, 720)
            pygame.display.set_mode(self.screen_size)
            self.options_values["resolution"] = "720p"
            self.buttons["options"]["fullscreen"].active = False
            self.buttons["options"]["720p"].active = True
        elif self.buttons["options"]["none"].clicked:
            self.options_values["particles"] = "some"
            self.buttons["options"]["none"].active = False
            self.buttons["options"]["some"].active = True
        elif self.buttons["options"]["some"].clicked:
            self.options_values["particles"] = "lots"
            self.buttons["options"]["some"].active = False
            self.buttons["options"]["lots"].active = True
        elif self.buttons["options"]["lots"].clicked:
            self.options_values["particles"] = "none"
            self.buttons["options"]["lots"].active = False
            self.buttons["options"]["none"].active = True
        elif self.buttons["options"]["hard"].clicked:
            self.options_values["difficulty"] = "hard"
        elif self.buttons["options"]["medium"].clicked:
            self.options_values["difficulty"] = "medium"
        elif self.buttons["options"]["easy"].clicked:
            self.options_values["difficulty"] = "easy"

        self.draw_options()


    def high_score(self):
        self.update_buttons("high_score")

        if self.buttons["high_score"]["exit"].clicked:
            self.scene = self.main_menu

        self.draw_high_score()

    def draw_game(self, draw_score=True):
        def rotation(image, angle):
            orig_rect = image.get_rect()
            rot_image = pygame.transform.rotate(image, angle)
            rot_rect = orig_rect.copy()
            rot_rect.center = rot_image.get_rect().center
            rot_image = rot_image.subsurface(rot_rect).copy()
            return rot_image

        # tło
        self.draw_screen.blit(self.textures["background"], (0, (self.scroll // PARALLAX_DEPTH) % 180 - 180))
        self.draw_screen.blit(self.textures["background"], (0, (self.scroll // PARALLAX_DEPTH) % 180))

        # okna
        self.draw_screen.blit(self.textures["window"], (self.window.x, self.window.y + (self.scroll // PARALLAX_DEPTH)))
        self.draw_screen.blit(self.textures["window"],
                              (320 - self.window.x - 32, self.window.y + (self.scroll // PARALLAX_DEPTH)))

        # schodki
        for slab in self.slabs:

            # lewy koniec
            self.draw_screen.blit(self.textures["block_left" + str(min(5, (slab.index // NEW_FLOOR_DISTANCE) + 1))],
                                  (slab.pos.x, slab.pos.y + self.scroll))
            # bloki w środku
            for i in range(slab.width - 2):
                self.draw_screen.blit(
                    self.textures["block_middle" + str(min(5, (slab.index // NEW_FLOOR_DISTANCE) + 1))], (
                        slab.pos.x + (i + 1) * SLAB_BLOCK_WIDTH, slab.pos.y + self.scroll))

                # tabliczka z numerem schodka
                if slab.index > 0 and slab.index % 10 == 0 and i == (slab.width - 2) // 2:
                    self.draw_screen.blit(self.textures["slab_sign"],
                                          (slab.pos.x + (i + 1) * SLAB_BLOCK_WIDTH, slab.pos.y + self.scroll))

                    # liczba na tabliczce
                    text = self.font.render(str(slab.index), False, (255, 255, 255))
                    rect = text.get_rect(
                        center=(slab.pos.x + (i + 1) * SLAB_BLOCK_WIDTH + 9, slab.pos.y + self.scroll + 8))
                    self.draw_screen.blit(text, rect)

            # prawy koniec
            self.draw_screen.blit(self.textures["block_right" + str(min(5, (slab.index // NEW_FLOOR_DISTANCE) + 1))], (
                slab.pos.x + (slab.width - 1) * SLAB_BLOCK_WIDTH, slab.pos.y + self.scroll))

        # postać

        # print(self.character.actual_frame)
        character_frame = self.textures["character_" + self.character.animation + str(self.character.actual_frame + 1)].copy()
        if self.character.animation == "rotate":
            character_frame = rotation(character_frame, self.character.angle)
        elif self.character.velocity.x < 0:
            character_frame = pygame.transform.flip(character_frame, True, False)
        self.draw_screen.blit(character_frame, (self.character.pos.x, self.character.pos.y + self.scroll))

        # rysowanie hitboxa postaci
        # pygame.draw.rect(self.draw_screen, (255, 0, 0), self.character.rect)

        # rysowanie hitboxa platform
        # pygame.draw.rect(self.draw_screen, (255, 0, 0), slab.rect)

        # particle
        for particle in self.particles:
            s = pygame.Surface((particle.size, particle.size), pygame.SRCALPHA)
            s.fill(particle.color)
            self.draw_screen.blit(s, (particle.pos.x, particle.pos.y + self.scroll))

        # murki po bokach
        self.draw_screen.blit(self.textures["walls"], (0, self.scroll % 180 - 180))
        self.draw_screen.blit(self.textures["walls"], (0, self.scroll % 180))

        if draw_score:
            if self.combo_steps > 0:
                distortion_amount = int(
                    (abs(self.character.velocity.x) + abs(self.character.velocity.y)) * CLOCK_SHAKE_INTENSITY)
                distortion_x = random.randint(-distortion_amount, distortion_amount) + int(
                    (math.sin(self.game_timer * CLOCK_WAVING_SPEED)) * CLOCK_WAVING_INTENSITY)
                distortion_y = random.randint(-distortion_amount, distortion_amount) + int(
                    (math.cos(self.game_timer * CLOCK_WAVING_SPEED)) * CLOCK_WAVING_INTENSITY)
            else:
                distortion_x = 0
                distortion_y = 0

            self.actual_clock_distortion_x += (distortion_x - self.actual_clock_distortion_x) / CLOCK_WAVING_SMOOTH
            self.actual_clock_distortion_y += (distortion_y - self.actual_clock_distortion_y) / CLOCK_WAVING_SMOOTH

            # zegar
            self.draw_screen.blit(self.textures["clock"],
                                  (20 + int(self.actual_clock_distortion_x), 10 + int(self.actual_clock_distortion_y)))
            angle = self.scroll_timer / TIME_SPEED_UP_INTERLUDE[self.options_values["difficulty"]] * -360
            self.draw_screen.blit(rotation(self.textures["clock_hand"], angle),
                                  (20 + int(self.actual_clock_distortion_x), 14 + int(self.actual_clock_distortion_y)))

            # combo
            if self.combo_steps > 0:

                # czas combo
                bars_amount = int((1 - self.combo_timer) * 32)
                timer_bar = pygame.Rect(29 + int(self.actual_clock_distortion_x),
                                        76 + int(self.actual_clock_distortion_y), 7, 1)
                for i in range(bars_amount):
                    color = (229, 48, 43)
                    if i % 2 == 1:
                        color = (218, 41, 44)
                    pygame.draw.rect(self.draw_screen, color, timer_bar)
                    timer_bar.y -= 1

                # gwiazdka
                self.draw_screen.blit(self.textures["combo_star"], (
                    20 + int(self.actual_clock_distortion_x), 75 + int(self.actual_clock_distortion_y)))
                combo_print = self.font.render(str(self.combo_steps), False, (255, 255, 255))
                combo_print_rect = combo_print.get_rect()
                combo_print_rect.center = (
                    33 + int(self.actual_clock_distortion_x), 90 + int(self.actual_clock_distortion_y))
                self.draw_screen.blit(combo_print, combo_print_rect)

            # rysowanie wyniku
            score_print = self.font.render("Score: " + str(self.score // 1), False, (255, 255, 255))
            score_print_rect = score_print.get_rect()
            score_print_rect.topleft = (16, 166)
            self.draw_screen.blit(score_print, score_print_rect)

            # napisy combo
            if self.options_values["combo_caption"] == "on":
                if self.combo_caption_steps > 0:
                    self.draw_combo_caption()

    def draw_screen_shake(self):
        shadow = pygame.Surface(DRAW_SCREEN_SIZE, pygame.SRCALPHA)
        shadow.fill((0, 0, 0,
                     min(int((self.game_end - SCREEN_SHAKE_INTERLUDE) / SCREEN_SHAKE_DURATION * DARKEN_INTENSITY),
                         255)))
        draw_screen_darken = self.draw_screen_copy.copy()
        draw_screen_darken.blit(shadow, (0, 0))
        intensity = int(SCREEN_SHAKE_INTESITY * (SCREEN_SHAKE_DURATION + SCREEN_SHAKE_INTERLUDE) / self.game_end)
        self.draw_screen.blit(draw_screen_darken, (random.randint(-intensity, intensity),
                                                   random.randint(-intensity, intensity)))

        # rysowanie napisu game over
        self.draw_screen.blit(self.textures["game_over"], (90, self.game_over_pos - 5))

        # rysowanie wyniku
        score_print = self.font.render("Score: " + str(self.score // 1), False, (255, 255, 255))
        score_print_rect = score_print.get_rect()
        score_print_rect.center = (160, self.game_over_pos + 35)
        self.draw_screen.blit(score_print, score_print_rect)

        score_print = self.font.render("Best Combo: " + str(self.max_combo // 1), False, (255, 255, 255))
        score_print_rect = score_print.get_rect()
        score_print_rect.center = (160, self.game_over_pos + 45)
        self.draw_screen.blit(score_print, score_print_rect)

        score_print = self.font.render("Floors: " + str((self.floors - 1) // 1), False, (255, 255, 255))
        score_print_rect = score_print.get_rect()
        score_print_rect.center = (160, self.game_over_pos + 55)
        self.draw_screen.blit(score_print, score_print_rect)

        tip_print = self.font.render("Press SPACE or ESC to continue", False, (255, 255, 255,))
        tip_print_rect = tip_print.get_rect()
        tip_print_rect.center = (160, self.game_over_pos * 3 - 45)
        self.draw_screen.blit(tip_print, tip_print_rect)

    def draw_main_menu(self):
        self.draw_screen.blit(self.textures["main_menu"], (0, 0))
        self.draw_buttons("menu")

    def draw_options(self):
        self.draw_screen.blit(self.textures["menu_brick"], (0, 0))
        self.draw_buttons("options")

        # suwak
        shadow = self.volume_slider.rect.copy()
        shadow.width += 2
        shadow.height += 2
        pygame.draw.rect(self.draw_screen, (0, 0, 0), shadow, border_radius=SLIDER_BORDER_RADIUS)
        shadow.width -= 1
        shadow.height -= 1
        pygame.draw.rect(self.draw_screen, (199, 199, 199), shadow, border_radius=SLIDER_BORDER_RADIUS)
        pygame.draw.rect(self.draw_screen, SLIDER_COLOR, self.volume_slider.rect, border_radius=SLIDER_BORDER_RADIUS)
        if self.volume_slider.activated:
            shadow = self.volume_slider.button_rect.copy()
            shadow.width += 2
            shadow.height += 2
            pygame.draw.rect(self.draw_screen, SLIDER_BUTTON_COLOR_TOUCHED, shadow, border_radius=SLIDER_BORDER_RADIUS)
            shadow.width -= 1
            shadow.height -= 1
            pygame.draw.rect(self.draw_screen, (199, 199, 199), shadow, border_radius=SLIDER_BORDER_RADIUS)
            pygame.draw.rect(self.draw_screen, SLIDER_BUTTON_COLOR_ACTIVATED, self.volume_slider.button_rect,
                             border_radius=SLIDER_BORDER_RADIUS)
        else:
            shadow = self.volume_slider.button_rect.copy()
            shadow.width += 2
            shadow.height += 2
            pygame.draw.rect(self.draw_screen, (0, 0, 0), shadow, border_radius=SLIDER_BORDER_RADIUS)
            shadow.width -= 1
            shadow.height -= 1
            pygame.draw.rect(self.draw_screen, (199, 199, 199), shadow, border_radius=SLIDER_BORDER_RADIUS)
            if self.volume_slider.touched:
                pygame.draw.rect(self.draw_screen, SLIDER_BUTTON_COLOR_TOUCHED, self.volume_slider.button_rect,
                                 border_radius=SLIDER_BORDER_RADIUS)
            else:
                pygame.draw.rect(self.draw_screen, SLIDER_BUTTON_COLOR, self.volume_slider.button_rect,
                                 border_radius=SLIDER_BORDER_RADIUS)

    def draw_high_score(self):
        self.draw_screen.blit(self.textures["menu_brick"], (0, 0))
        self.draw_buttons("high_score")

        # tło
        HIGH_SCORE_BACKGROUND_RECT = (72, 32, 80, 130, 7)
        pygame.draw.rect(self.draw_screen, (0, 0, 0),
                         pygame.Rect(HIGH_SCORE_BACKGROUND_RECT[0], HIGH_SCORE_BACKGROUND_RECT[1],
                                     HIGH_SCORE_BACKGROUND_RECT[2], HIGH_SCORE_BACKGROUND_RECT[3]),
                         border_radius=HIGH_SCORE_BACKGROUND_RECT[4])
        pygame.draw.rect(self.draw_screen, (199, 199, 199),
                         pygame.Rect(HIGH_SCORE_BACKGROUND_RECT[0], HIGH_SCORE_BACKGROUND_RECT[1],
                                     HIGH_SCORE_BACKGROUND_RECT[2] - 1, HIGH_SCORE_BACKGROUND_RECT[3] - 1),
                         border_radius=HIGH_SCORE_BACKGROUND_RECT[4])
        pygame.draw.rect(self.draw_screen, (255, 255, 255),
                         pygame.Rect(HIGH_SCORE_BACKGROUND_RECT[0], HIGH_SCORE_BACKGROUND_RECT[1],
                                     HIGH_SCORE_BACKGROUND_RECT[2] - 2, HIGH_SCORE_BACKGROUND_RECT[3] - 2),
                         border_radius=HIGH_SCORE_BACKGROUND_RECT[4])

        # Wypisywanie najlepszych wynikow
        with open("high_score.txt", "r") as file:
            lines = file.readlines()
            numbers = [int(x) for x in lines]
        for i in range(len(numbers)):
            score_print = self.font.render("#" + str(i + 1) + " " * (10 - len(str(i + 1) * 3)) + str(numbers[i]), False,
                                           (0, 0, 0))
            score_print_rect = score_print.get_rect()
            score_print_rect.topleft = (95, 40 + 12 * i)
            self.draw_screen.blit(score_print, score_print_rect)

    def draw_buttons(self, menu_type):
        for button_name in self.buttons[menu_type]:
            button = self.buttons[menu_type][button_name]
            if button.active:
                if button.sound_to_play == "touch":
                    self.mixer_channels["click"].play(self.sounds["click"][0])
                elif button.sound_to_play == "click":
                    self.mixer_channels["click"].play(self.sounds["click"][1])
                if self.options_values["difficulty"] == button_name:
                    self.draw_screen.blit(self.textures["menu_button_clicked"], button.rect)
                else:
                    self.draw_screen.blit(self.textures["menu_button_" + button.state], button.rect)
                self.draw_screen.blit(button.text, button.text_rect)

    def draw_combo_caption(self):


        if self.combo_caption_timer < COMBO_CAPTION_TIME / 2:
            self.combo_caption_pos += (COMBO_CAPTION_POS[1] - self.combo_caption_pos) / COMBO_CAPTION_SMOOTH
        else:
            self.combo_caption_pos += (DRAW_SCREEN_SIZE[1] + COMBO_CAPTION_MARGIN - self.combo_caption_pos) / COMBO_CAPTION_SMOOTH * COMBO_CAPTION_LEFT_SPEED_MULTIPLIER
        caption = self.textures[COMBO_CAPTION_TYPES[min(self.combo_caption_steps // 10 * 10, 50)]].copy()
        if COMBO_CAPTION_POS[1] - self.combo_caption_pos < 40:
            distortion_x = int(math.sin(self.game_timer * COMBO_CAPTION_WAVING_SPEED) * COMBO_CAPTION_WAVING_INTENSITY)
            distortion_y = int(math.cos(self.game_timer * COMBO_CAPTION_WAVING_SPEED) * COMBO_CAPTION_WAVING_INTENSITY)
        else:
            distortion_x = 0
            distortion_y = 0


        caption_rect = caption.get_rect()
        caption_rect.center = (COMBO_CAPTION_POS[0] + distortion_x, self.combo_caption_pos + distortion_y)
        self.draw_screen.blit(caption, caption_rect)

    def update_buttons(self, menu_type):
        for button_name in self.buttons[menu_type]:
            self.buttons[menu_type][button_name].update(self.mouse, self.sounds)

    def refresh_screen(self):
        # funkcja odswiezajaca ekran oraz obliczaja delta time
        self.screen.blit(pygame.transform.scale(self.draw_screen, self.screen_size), (0, 0))
        pygame.display.update()
        self.dt = self.clock.tick(FRAMERATE) * 60 / 1000

    def check_collisions(self):
        for slab in self.slabs:
            if slab.rect.collidepoint(self.character.rect.bottomleft) or slab.rect.collidepoint(
                    self.character.rect.bottomright):
                if self.character.velocity.y > 0:
                    self.character.rect.bottom = slab.rect.top
                    self.character.pos.y = slab.rect.top - 24
                    if not self.character.is_standing:
                        if slab.index == 0 and not self.game_started:
                            self.mixer_channels["hi"].play(random.choice(self.sounds["hi"]))
                        else:
                            self.mixer_channels["fall"].play(random.choice(self.sounds["fall"]))

                    self.character.is_standing = True

                    self.character.velocity.y = 0
                    self.current_index = slab.index

                    if slab.index != 0:
                        self.game_started = True

        if self.character.velocity.y != 0:
            self.character.is_standing = False

    def score_counting(self):
        # obliczenie wysokości skoku
        if self.last_index != self.current_index:
            self.jump_height = self.current_index - self.last_index

        self.last_index = self.current_index

        # odliczanie sekundy na wykonanie kolejnego skoku
        if self.timer_start == True:
            self.combo_timer += self.dt * COMBO_TIMER_SPEED

        # resetowanie czasu przy lądowaniu
        if self.character.is_standing:
            self.timer_start = True

        else:
            self.timer_start = False

        # zakończenie combo po upływie czasu
        if self.combo_timer > 1:
            self.score += self.combo_steps ** 2
            self.max_combo = max(self.max_combo, self.combo_steps)
            self.combo_caption_steps = max(self.combo_steps, self.combo_caption_steps)
            self.combo_steps = 0
            self.combo_timer = 0

        # system liczenia punktów
        if self.jump_height > 0:

            # liczenie punktów
            self.score += self.jump_height * 10
            self.floors += self.jump_height

            # dodanie punktów do combo i przedłużenie czasu
            if self.jump_height > 1 and self.combo_timer < 1:
                self.combo_steps += self.jump_height
                self.combo_timer = 0

            else:
                self.score += self.combo_steps ** 2
                self.max_combo = max(self.max_combo, self.combo_steps)
                self.combo_caption_steps = max(self.combo_steps, self.combo_caption_steps)
                self.combo_steps = 0
                self.combo_timer = 0

        elif self.jump_height < 0:
            self.score += self.combo_steps ** 2
            self.max_combo = max(self.max_combo, self.combo_steps)
            self.combo_caption_steps = max(self.combo_steps, self.combo_caption_steps)
            self.combo_steps = 0

        self.jump_height = 0


# utworzenie obiektu gry
if __name__ == "__main__":
    Game()
