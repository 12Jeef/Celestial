# directory collecting
import os
# pygame and math
import pygame as pg
import math as m

# pygame init
pg.mixer.pre_init(44100, -16, 1, 512)
pg.init()

# gets main directory
main_dir = os.path.split(os.path.abspath(__file__))[0]

# loads game fonts
game_font = os.path.join(main_dir, "Fonts", "Nexa Bold.ttf")
game_font = "Arial"
game_fonts = [100, 50, 25, 10, 5, 1]
for idx in range(len(game_fonts)):
    game_fonts[idx] = pg.font.SysFont(game_font, int(game_fonts[idx] * 0.5))
game_fonts_large = [1000, 500, 200, 150, 100]
for idx in range(len(game_fonts_large)):
    game_fonts_large[idx] = pg.font.SysFont(game_font, int(game_fonts_large[idx] * 0.5))
del game_font


# game constants
position = tuple[(float, int), (float, int)]
colors = tuple[(float, int), (float, int), (float, int)]
number = (float, int)
coord = number
rendering = tuple[pg.Surface, position]


def load_image(name: str, surface: pg.Surface) -> pg.Surface:
    # loads image in Graphics folder
    path = os.path.join(main_dir, "Graphics", name)
    return pg.image.load(path).convert(surface)


def play_sound(name: str):
    # plays sound
    path = os.path.join(main_dir, "Sounds", name)
    sound = pg.mixer.Sound(path)
    sound.set_volume(0)
    """
    pg.mixer.Sound.play(sound)
    """
    return sound


class Sound:
    playing = True

    def __init__(self, name: str, x: coord, y: coord, vol: number):
        self.name = name
        self.x = x
        self.y = y
        self.vol = vol
        self.vol_val = 1
        self.vol_player = 0
        self.vol_final = 0
        sound = play_sound(name)
        self.sound = sound
        self.time = sound.get_length()

    def tick(self, player: object):
        if player.x is None:
            player.x = 0
        if player.y is None:
            player.y = 0
        if distance(self.x, self.y, player.x, player.y) < 900:
            self.vol_player = 1 - (distance(self.x, self.y, player.x, player.y) / 900)
            global_sound_vol = 0.1
            if self.sound.get_volume != self.vol * self.vol_val * self.vol_player * global_sound_vol:
                self.sound.set_volume(self.vol * self.vol_val * self.vol_player * global_sound_vol)
        else:
            if self.sound.get_volume() > 0:
                self.sound.set_volume(0)
        if self.playing:
            self.time -= 1 / 60
            if self.time < 0:
                self.time = 0
                self.playing = False

    def set_volume(self, value: number):
        if self.vol_val != value:
            self.vol_val = value


def point_towards(x1: coord, y1: coord, x2: coord, y2: coord) -> float:
    # point towards xy2 from xy1
    return (180 / m.pi) * -m.atan2(y2 - y1, x2 - x1)


def distance(x1: coord, y1: coord, x2: coord, y2: coord) -> float:
    # distance from xy1 to xy2
    return m.sqrt(m.pow(x1 - x2, 2) + m.pow(y1 - y2, 2))


def draw_txt(screen: pg.Surface, font: pg.font.Font, txt: str, color: colors, pos: position, align_x: str, align_y: str) -> pg.Surface:
    # draws text
    label = font.render(str(txt), True, color)
    # sets alignment
    new_pos = list(pos)
    if align_x == "l":
        new_pos[0] = pos[0]
    elif align_x == "m":
        new_pos[0] = pos[0] - (label.get_width() / 2)
    elif align_x == "r":
        new_pos[0] = pos[0] - label.get_width()
    if align_y == "b":
        new_pos[1] = pos[1]
    elif align_y == "m":
        new_pos[1] = pos[1] - (label.get_height() / 2)
    elif align_y == "t":
        new_pos[1] = pos[1] - label.get_height()
    new_pos = tuple(new_pos)
    # draws aligned text
    screen.blit(label, new_pos)
    return label
