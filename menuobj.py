# crucial functions
import func as f
# pygame and math
import pygame as pg
import math as m


class Button:
    clicked = False
    hover = False
    prop = 1

    def __init__(self, x: f.coord, y: f.coord, width: f.number, height: f.number, text: str, text_s: int, text_c: f.colors, job: str):
        self.image = pg.Surface((width, height)).convert_alpha()
        f.draw_txt(self.image, f.game_fonts[text_s], text, text_c, (width / 2, height / 2), "m", "m")
        self.text_s = text_s
        self.text_c = text_c
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.job = job

    def tick(self, mouse_pos: f.position, mouse_down: bool):
        if self.clicked:
            self.clicked = False
        if self.hover:
            self.hover = False
        if m.fabs(self.x - mouse_pos[0]) < self.prop * self.width / 2:
            if m.fabs(self.y - mouse_pos[1]) < self.prop * self.height / 2:
                self.hover = True
                if mouse_down:
                    self.clicked = True
        if self.hover:
            if m.fabs(self.prop - 1.25) < 0.01:
                if self.prop != 1.25:
                    self.prop = 1.25
            else:
                self.prop += (1.25 - self.prop) / 3
        else:
            if m.fabs(self.prop - 1) < 0.01:
                if self.prop != 1:
                    self.prop = 1
            else:
                self.prop += (1 - self.prop) / 3

    def render(self) -> f.rendering:
        image_fade = pg.Surface((self.width, self.height)).convert_alpha()
        image_fade.fill(self.text_c)
        image_fade.set_alpha(int(42.5 + (42.5 * ((self.prop - 1) / 0.25))))
        image = pg.Surface((self.width, self.height)).convert_alpha()
        image.blit(image_fade, (0, 0))
        image.blit(self.image, (0, 0))
        if self.prop > 1:
            image_final = pg.transform.smoothscale(image, (int(self.prop * self.width), int(self.prop * self.height)))
        else:
            image_final = image
        image_pos = (self.x - (0.5 * self.prop * self.width), self.y - (0.5 * self.prop * self.height))
        return image_final, image_pos


class Slider:
    clicked = False
    hover = False
    prop = 1
    follow = 0
    value = 0
    value_max = 0

    def __init__(self, x: f.coord, y: f.coord, width: f.number, height: f.number, text: str, text_s: int, text_c: f.colors,  value: int, value_max: int, job: str):
        self.image = pg.Surface((width, height)).convert_alpha()
        f.draw_txt(self.image, f.game_fonts[text_s], text, text_c, (width / 2, height / 2), "m", "m")
        self.text_s = text_s
        self.text_c = text_c
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.value = value
        self.value_max = value_max
        self.job = job

    def tick(self, mouse_pos: f.position, mouse_down: bool):
        if self.clicked:
            self.clicked = False
        if self.hover:
            self.hover = False
        if m.fabs((self.x + (self.width * self.value / self.value_max) - (self.width / 2)) - mouse_pos[0]) < 20:
            if m.fabs(self.y - mouse_pos[1]) < self.prop * (self.height / 2):
                self.hover = True
                if mouse_down:
                    self.follow = 10
        if self.hover:
            if m.fabs(self.prop - 1.25) < 0.01:
                if self.prop != 1.25:
                    self.prop = 1.25
            else:
                self.prop += (1.25 - self.prop) / 3
        else:
            if m.fabs(self.prop - 1) < 0.01:
                if self.prop != 1:
                    self.prop = 1
            else:
                self.prop += (1 - self.prop) / 3
        if self.follow > 0:
            self.clicked = True
            self.follow -= 1
            self.value = int(self.value_max * (mouse_pos[0] - (self.x - (self.width / 2))) / self.width)
            if self.value < 0:
                self.value = 0
            if self.value > self.value_max:
                self.value = self.value_max

    def render(self) -> f.rendering:
        image_fade = pg.Surface((self.width, self.height)).convert_alpha()
        image_fade.fill(self.text_c)
        image_fade.set_alpha(43)
        image_bar = pg.Surface((self.width, self.height)).convert_alpha()
        prop = (self.width * self.value / self.value_max)
        pg.draw.line(image_bar, self.text_c, (prop, 0), (prop, self.height), 20)
        image_bar.set_alpha(int(42.5 + (42.5 * ((self.prop - 1) / 0.25))))
        image = pg.Surface((self.width, self.height)).convert_alpha()
        image.blit(image_fade, (0, 0))
        image.blit(image_bar, (0, 0))
        image.blit(self.image, (0, self.height * -0.1))
        pos = (self.width / 2, (self.height / 2) + (self.height * 0.25))
        f.draw_txt(image, f.game_fonts[self.text_s + 1], str(self.value), self.text_c, pos, "m", "m")
        image_pos = (self.x - (self.width / 2), self.y - (self.height / 2))
        return image, image_pos
