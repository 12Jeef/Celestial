# crucial functions
import func as f
# name collecting
import os
# pygame and math
import pygame as pg
import math as m
# imports objects
from playerobj import Player, Shield, Portal
from movingobj import Asteroid, Projectile, Damage
from enemyobj import Enemy, Wave
from menuobj import Button, Slider
# copying vars
from copy import copy
# random asteroid and enemy generation
from random import randint
# fps checking
from time import time
# line printing


def get_controls(pressed, click_pause) -> tuple:
    # creates list of 5 controls: right, left, up, down, shoot
    controls = [0] * 5
    if pressed[pg.K_RIGHT] or pressed[pg.K_d]:
        controls[0] = 1
    if pressed[pg.K_LEFT] or pressed[pg.K_a]:
        controls[1] = 1
    if pressed[pg.K_UP] or pressed[pg.K_w]:
        controls[2] = 1
    if pressed[pg.K_DOWN] or pressed[pg.K_s]:
        controls[3] = 1
    if pressed[pg.K_SPACE]:
        controls[4] = 1
    # detect mouse down
    if pg.mouse.get_pressed(3)[0]:
        if click_pause == 0:
            controls[4] = 1
    # returns tuple instead
    return tuple(controls)


def draw_bar(surface: pg.Surface, symbol: pg.Surface, bar_wh: f.position, bar_pos: f.position, bar_val: f.position, bar_c: f.colors, bar_u: int):
    # creates tuple of two bar len values
    bar_v = (bar_val[0]/bar_val[2], bar_val[1]/bar_val[2])
    bar_val = bar_v
    # creates bar update, which is used for pulse and stretch effect
    bar_u_v = 1 - (bar_u / 10)
    # creates color of symbols, used for adding "brightness" to symbol
    new_col = pg.Color((255-((255-bar_c[0])*bar_u_v), 255-((255-bar_c[1])*bar_u_v), 255-((255-bar_c[2])*bar_u_v)))
    new_symbol = copy(symbol)
    # replaces all pixels with set color
    for x in range(new_symbol.get_width()):
        for y in range(new_symbol.get_height()):
            new_col.a = new_symbol.get_at((x, y))[3]
            new_symbol.set_at((x, y), new_col)
    bar_list = list()
    # white and black tuple - used to shorten code
    white = (255, 255, 255)
    black = (0, 10, 40)
    # bar slant amount
    bar_shift = 10
    # creates background
    bar = pg.Surface((bar_wh[0] + bar_shift, bar_wh[1])).convert_alpha()
    bar_val_q = bar_wh[0]
    pg.draw.polygon(bar, black, [(bar_shift, 0), (bar_shift + bar_val_q, 0), (bar_val_q, bar_wh[1]), (0, bar_wh[1])])
    bar.set_alpha(128)
    bar_list.append(bar)
    # creates white delayed surface
    bar = pg.Surface((bar_wh[0] + bar_shift, bar_wh[1])).convert_alpha()
    bar_val_q = bar_wh[0] * bar_val[1]
    pg.draw.polygon(bar, white, [(bar_shift, 0), (bar_shift + bar_val_q, 0), (bar_val_q, bar_wh[1]), (0, bar_wh[1])])
    bar_list.append(bar)
    # creates colored surface
    bar = pg.Surface((bar_wh[0] + bar_shift, bar_wh[1])).convert_alpha()
    bar_val_q = bar_wh[0] * bar_val[0]
    pg.draw.polygon(bar, bar_c, [(bar_shift, 0), (bar_shift + bar_val_q, 0), (bar_val_q, bar_wh[1]), (0, bar_wh[1])])
    bar_list.append(bar)
    # creates ring
    bar = pg.Surface((bar_wh[0] + bar_shift, bar_wh[1])).convert_alpha()
    bar_val_q = bar_wh[0]
    w = 1.5
    pg.draw.polygon(
        bar, bar_c,
        [(bar_shift + w, 0), (bar_shift + bar_val_q - w, 0), (bar_val_q - w, bar_wh[1] - w), (w, bar_wh[1] - w)],
        int(2 * w)
    )
    bar_list.append(bar)
    # draws bars on screen
    for bar in bar_list:
        blit(surface, bar, bar_pos)
    # gets symbol position and change it by pulse effect
    symbol_xy = (bar_pos[0] - (bar_wh[1] * (0.75 + (bar_u_v / 4))), bar_pos[1] - (bar_wh[1] * (0.5 * (1 - bar_u_v))))
    # gets symbol width and height based on pulse effect
    symbol_wh = (int(bar_wh[1] * (1 - (0.5 * (1 - bar_u_v)))), int(bar_wh[1] * (1 + (0.5 * (1 - bar_u_v)))))
    # draws symbol
    blit(surface, pg.transform.scale(new_symbol, symbol_wh), symbol_xy)


def draw_glow(image: pg.Surface, surface: pg.Surface, amount: f.number, screen_wh: f.position):
    if amount > 0:
        # creates copy of image and applies alpha
        shield_glow_alpha = copy(image)
        shield_glow_alpha.set_alpha(int(63.75 * amount))
        # enlargement amount
        scale_amount = 0.5
        # fit to screen
        scale_d = (int(screen_wh[0] * (1 + scale_amount)), int(screen_wh[1] * (1 + scale_amount)))
        scale_shield = pg.transform.scale(shield_glow_alpha, scale_d)
        # draw shield
        blit(surface, scale_shield, (-(screen_wh[0] * scale_amount) / 2, -(screen_wh[1] * scale_amount) / 2))


def ch_cam_xy(cam_xy: f.position, x: f.coord, y: f.coord) -> f.position:
    # changes cam_xy by specified amount
    return cam_xy[0] + x, cam_xy[1] + y


def shake(cam_shk: f.position, strength: f.number) -> f.position:
    # shakes camera
    return (cam_shk[0] + randint(-strength, strength)) * -0.75, (cam_shk[1] + randint(-strength, strength)) * -0.75


def blit(screen: pg.Surface, image: pg.Surface, pos: f.position):
    if pos[0] > screen.get_width():
        return
    if pos[1] > screen.get_height():
        return
    if pos[0] + image.get_width() < 0:
        return
    if pos[1] + image.get_height() < 0:
        return
    screen.blit(image, pos)


def minimap_pos(pos: f.position, game_wh: f.position, minimap: pg.Surface) -> f.position:
    # returns position of object on minimap
    pos = (
        minimap.get_width() * (0.5 + 0.5 * pos[0] / game_wh[0]) - 5,
        minimap.get_height() * (0.5 + 0.5 * pos[1] / game_wh[1]) - 5
    )
    return pos


def blur_surface(surface: pg.Surface, blur: int) -> pg.Surface:
    wh = (surface.get_width(), surface.get_height())
    percent = 1 - (0.9 * (blur / 100))
    wh_blur = (int(wh[0] * percent), int(wh[1] * percent))
    blur_surf = copy(surface)
    blur_surf = pg.transform.smoothscale(blur_surf, wh_blur)
    blur_surf = pg.transform.smoothscale(blur_surf, wh)
    return blur_surf


def main():
    # init
    pg.mixer.pre_init(44100, -16, 1, 512)
    pg.init()

    # creates screen
    info = pg.display.Info()
    screen_wh = (int(1 * (info.current_w - 0)), int(1 * (info.current_h - 111)))
    screen = pg.display.set_mode(screen_wh)
    # game width and height
    game_wh = (1200, 1200)
    # game mode and scrolling
    mode = 0
    mode_nxt = 1
    mode_menu = False
    mode_menu_m = 0
    transition = 10
    click_pause = 0
    scroll_x = 0
    scroll_y = 0
    scroll_vx = 0
    scroll_vy = 0
    # limits pygame events
    pg.event.set_allowed([pg.QUIT, pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP])

    # creates leaderboard
    try:
        log = open("leaderboard.log", "r")
    except FileNotFoundError:
        log = open("leaderboard.log", "x")
    log.close()
    leaderboard = list()
    leaderboard_dis = pg.Surface((0, 0))
    leaderboard_row = pg.Surface((0, 0))

    # sets up game name
    game_name = os.path.split(f.main_dir)[1]
    game_title = pg.Surface((600, 300)).convert_alpha()
    for i in range(10):
        i_prop = i / 10
        col = 170 + ((255 - 170) * i_prop)
        f.draw_txt(game_title, f.game_fonts_large[2], game_name, (col, col, col), (300, 150 + (5 * (1 - i_prop))), "m", "m")
    f.draw_txt(game_title, f.game_fonts[1], "Shooter Game", (191.25, 191.25, 191.25), (300, 225), "m", "m")

    # sets up cameras: final, player, and shake
    cam_xy = (0, 0)
    cam_xy_p = cam_xy
    cam_shk = (0, 0)
    # creates player and shield objects
    player = Player("player.svg", screen, cam_xy_p[0], cam_xy_p[1])
    shield = Shield("shield.svg", screen)
    # creates asteroids, projectiles, damages, and enemies
    asteroids = list()
    asteroid_t = 60
    projectiles = list()
    damages = list()
    enemies = list()
    enemies_t = 60
    wave_queue = list()
    wave_t = 60 * 15
    # creates portal
    portal = None
    # creates sound list
    sounds = list()
    volume = 1

    # sets window name and app icon
    pg.display.set_caption(game_name + " - Shooter Game")
    icon = pg.Surface((110, 110)).convert_alpha()
    pg.draw.circle(icon, (0, 10, 40), (55, 55), 50)
    player_icon = f.load_image("player.svg", icon)
    player_icon_avd = (player_icon.get_width() + player_icon.get_height()) / 2
    player_icon_d = (int(75 * player_icon.get_width() / player_icon_avd), int(75 * player_icon.get_height() / player_icon_avd))
    player_icon = pg.transform.scale(player_icon, player_icon_d)
    player_icon = pg.transform.rotate(player_icon, -45)
    icon.blit(player_icon, ((110 - player_icon.get_width()) / 2, (110 - player_icon.get_height()) / 2))
    pg.display.set_icon(icon)

    # menu objects
    menu_obj = [
        [
            Button(0, 50, 300, 50, "PLAY", 1, (255, 255, 255), "play_game")
        ],
        [
            Button(0, -37.5, 300, 50, "RESUME", 1, (255, 255, 255), "mode_menu"),
            Slider(0, 37.5, 300, 50, "VOLUME", 1, (255, 255, 255), 100, 100, "volume_slider")
        ],
        [
            Button(0, 200, 300, 50, "HOME", 1, (255, 255, 255), "return_home")
        ]
    ]

    # creates wave list
    waves = [
        # 1
        Wave([(1, 2, (1, 1)), (2, 1, (1, 2))]),
        Wave([(1, 2, (1, 2)), (2, 1, (1, 2))]),
        Wave([(1, 1, (1, 2)), (2, 1, (2, 3))]),
        Wave([(1, 1, (2, 3)), (2, 1, (3, 5))]),
        # 5
        Wave([(1, 1, (1, 2)), (4, 1, (1, 1))]),
        Wave([(1, 1, (2, 3)), (2, 1, (3, 5)), (4, 3, (1, 1))]),
        Wave([(1, 1, (2, 3)), (2, 1, (3, 5)), (4, 3, (1, 2))]),
        Wave([(1, 1, (2, 3)), (2, 1, (2, 3)), (4, 2, (1, 1))]),
        Wave([(1, 1, (2, 3)), (2, 1, (2, 3)), (4, 2, (1, 2))]),
        # 10
        Wave([(1, 1, (1, 2)), (3, 1, (1, 1))]),
        Wave([(1, 1, (2, 3)), (2, 1, (2, 3)), (4, 4, (1, 1)), (5, 10, (1, 1))]),
        Wave([(1, 1, (2, 3)), (2, 1, (2, 3)), (4, 4, (1, 2)), (5, 8, (1, 1))]),
        Wave([(1, 1, (2, 3)), (2, 1, (2, 3)), (4, 3, (1, 1)), (5, 6, (1, 1))]),
        Wave([(1, 1, (2, 3)), (2, 1, (2, 3)), (4, 3, (1, 2)), (5, 4, (1, 1))]),
        # 15
        Wave([(1, 1, (3, 5)), (6, 1, (1, 2))]),
        Wave([(1, 1, (5, 8))]),
        Wave([(2, 1, (5, 8))]),
        Wave([(4, 1, (2, 3))]),
        Wave([(5, 1, (35, 45))]),
        # 20
        Wave([(4, 1, (2, 3)), (6, 1, (1, 3))]),
        Wave([(1, 1, (3, 5)), (6, 1, (1, 2))]),
        Wave([(1, 1, (2, 3)), (6, 1, (1, 3))]),
        Wave([(1, 1, (1, 2)), (6, 1, (2, 3))]),
        Wave([(1, 1, (1, 1)), (6, 1, (2, 4))]),
        # 25
        Wave([(7, 1, (1, 1))]),
        Wave([]),
        Wave([]),
        Wave([]),
        Wave([]),
        # 30
        Wave([(8, 1, (25, 25))])
    ]
    wave_count = 30
    wave_count -= 1
    intermission = False
    game_over = False

    # loads shield and border glow
    """ disabled to increase fps
    shield_glow = load_image("shield_glow.svg", real_screen)
    border_glow = load_image("border_glow.svg", real_screen)
    """

    # creates minimap and minimap symbols
    minimap = pg.Surface((500, 500)).convert_alpha()
    symb_size = 15
    mini_enemy = pg.Surface((symb_size, symb_size)).convert_alpha()
    pg.draw.circle(mini_enemy, (255, 0, 0), (symb_size / 2.5, symb_size / 2.5), symb_size / 2)
    mini_neutral = pg.Surface((symb_size, symb_size)).convert_alpha()
    pg.draw.circle(mini_neutral, (255, 255, 255), (symb_size / 2, symb_size / 2), symb_size / 2)
    mini_friend = pg.Surface((symb_size, symb_size)).convert_alpha()
    pg.draw.circle(mini_friend, (0, 255, 0), (symb_size / 2, symb_size / 2), symb_size / 2)

    # sets fps
    fps = 60
    fps_av = fps
    fps_clock = pg.time.Clock()
    tick = 0

    # creates and draws background
    bg = pg.Surface(screen_wh).convert_alpha()
    bg.fill((0, 10, 40))
    blit(screen, bg, (0, 0))

    # creates dark transition
    dark = pg.Surface(screen_wh).convert_alpha()
    dark.fill((0, 0, 0))

    # draws border
    border_x_1 = pg.Surface((screen_wh[0] + 50, 50)).convert_alpha()
    pg.draw.line(border_x_1, (255, 0, 0), (25, 25), (border_x_1.get_width() - 25, 25), 25)
    pg.draw.circle(border_x_1, (255, 0, 0), (25, 25), 13)
    pg.draw.circle(border_x_1, (255, 0, 0), (border_x_1.get_width() - 25, 25), 13)
    border_x_1.set_alpha(128)
    border_x_2 = pg.Surface((screen_wh[0] + 50, 50)).convert_alpha()
    pg.draw.line(border_x_2, (255, 255, 255), (25, 25), (border_x_1.get_width() - 25, 25), 13)
    pg.draw.circle(border_x_2, (255, 255, 255), (25, 25), 7)
    pg.draw.circle(border_x_2, (255, 255, 255), (border_x_1.get_width() - 25, 25), 7)
    border_x = [border_x_1, border_x_2]
    border_y_1 = pg.Surface((50, screen_wh[1] + 50)).convert_alpha()
    pg.draw.line(border_y_1, (255, 0, 0), (25, 25), (25, border_y_1.get_height() - 25), 25)
    pg.draw.circle(border_y_1, (255, 0, 0), (25, 25), 13)
    pg.draw.circle(border_y_1, (255, 0, 0), (25, border_y_1.get_height() - 25), 13)
    border_y_1.set_alpha(128)
    border_y_2 = pg.Surface((50, screen_wh[1] + 50)).convert_alpha()
    pg.draw.line(border_y_2, (255, 255, 255), (25, 25), (25, border_y_2.get_height() - 25), 13)
    pg.draw.circle(border_y_2, (255, 255, 255), (25, 25), 7)
    pg.draw.circle(border_y_2, (255, 255, 255), (25, border_y_1.get_height() - 25), 7)
    border_y = [border_y_1, border_y_2]

    # draws heart symbol
    hp_symbol = pg.Surface((100, 100)).convert_alpha()
    pg.draw.polygon(hp_symbol, (0, 0, 0), [(20, 40), (80, 40), (50, 90)])
    hp_symbol_p = pg.Surface((30, 30)).convert_alpha()
    pg.draw.ellipse(hp_symbol_p, (0, 0, 0), pg.Rect((0, 0), (30, 60)))
    blit(hp_symbol, hp_symbol_p, (20, 10))
    blit(hp_symbol, hp_symbol_p, (50, 10))
    # draws energy symbol
    e_symbol = pg.Surface((100, 100)).convert_alpha()
    pg.draw.polygon(e_symbol, (0, 0, 0), [(60, 0), (20, 60), (50, 60), (40, 100), (80, 40), (50, 40), (60, 0)])

    # creates star symbols
    stars_s = list()
    for i in range(3):
        stars_s.append(pg.Surface((50, 50)).convert_alpha())
    glow = 85
    for i in range(len(stars_s)):
        percent = (len(stars_s) - i) / len(stars_s)
        pg.draw.circle(
            stars_s[i],
            (0 + int(glow * percent), 10 + int(glow * percent), 40 + int(glow * percent)),
            (stars_s[i].get_width() / 2, stars_s[i].get_height() / 2),
            percent * 5
        )
    # creates star list
    stars_d = (25, 50, 100, 200, 500, 1000)
    stars = list()
    for i1 in range(len(stars_s)):
        para = 0.25 + (0.5 * (1 - ((len(stars_s) - (i1 + 1)) / 2)))
        for i2 in range(stars_d[len(stars_s) - (i1 + 1)]):
            rand_xy = (
                randint(0, int(screen_wh[0] / para)) - (screen_wh[0] / (2 * para)),
                randint(0, int(screen_wh[1] / para)) - (screen_wh[1] / (2 * para))
            )
            stars.append((len(stars_s) - i1, rand_xy))

    while 1:
        # fps checker
        c_time = round(time() * 1000)
        tick += 1

        # quitting and scrolling
        for e in pg.event.get():
            if e.type == pg.QUIT:
                return
            elif e.type == pg.MOUSEWHEEL and mode != 2:
                scroll_vx += e.x
                scroll_vy += e.y

        # changes transition
        if transition < 20:
            if transition == 10:
                if mode_nxt != mode:
                    mode = mode_nxt
                    # resets game
                    if mode == 1:
                        # sets up cameras: final, player, and shake
                        cam_xy = (0, 0)
                        cam_xy_p = cam_xy
                        cam_shk = (0, 0)
                        # creates player and shield objects
                        player = Player("player.svg", screen, cam_xy_p[0], cam_xy_p[1])
                        shield = Shield("shield.svg", screen)
                        # creates asteroids, projectiles, damages, and enemies
                        asteroids = list()
                        asteroid_t = 60
                        projectiles = list()
                        damages = list()
                        enemies = list()
                        enemies_t = 60
                        wave_queue = list()
                        wave_t = 60 * 15
                        # creates portal
                        portal = None
                    elif mode == 2:
                        game_over = False
                    elif mode == 3:
                        # organizes leaderboard
                        log = open("leaderboard.log", "r").read()
                        leaderboard = list(log.split("\n"))
                        leaderboard = leaderboard[0:len(leaderboard) - 1]
                        for i in range(len(leaderboard)):
                            leaderboard[i] = leaderboard[i].split("//")
                        leaderboard_org = list()
                        for i1 in range(len(leaderboard)):
                            if len(leaderboard_org) > 0:
                                inserted = False
                                for i2 in range(len(leaderboard_org)):
                                    if int(leaderboard[i1][0]) < int(leaderboard_org[i2][0]) and not inserted:
                                        leaderboard_org.insert(i2, leaderboard[i1])
                                        inserted = True
                                if not inserted:
                                    leaderboard_org.append(leaderboard[i1])
                            else:
                                leaderboard_org.append(leaderboard[i1])
                        leaderboard_org.sort(reverse=True)
                        # adds to leaderboard
                        log = open("leaderboard.log", "a")
                        log_line = [player.score, 0]
                        for i in range(len(log_line)):
                            log_line[i] = str(log_line[i])
                        log_line_final = ""
                        for phrase in log_line:
                            log_line_final += phrase + "//"
                        # log.write(log_line_final + "\n")
                        log.close()
                        leaderboard_this = log_line
                        # renders leaderboard
                        leaderboard_wh = (400, 50)
                        leaderboard_dis = pg.Surface((leaderboard_wh[0], leaderboard_wh[1] * (len(leaderboard_org) + 1))).convert_alpha()
                        y = 0
                        offset = False
                        this = len(leaderboard_org)
                        for log in leaderboard_org:
                            if int(log[0]) < int(leaderboard_this[0]):
                                if not offset:
                                    offset = True
                                    this = y
                            log_surf = pg.Surface(leaderboard_wh).convert_alpha()
                            f.draw_txt(log_surf, f.game_fonts[1], log[0], (255, 255, 255), leaderboard_wh, "r", "t")
                            f.draw_txt(log_surf, f.game_fonts[1], log[1], (255, 255, 255), (leaderboard_wh[0] - 100, leaderboard_wh[1]), "r", "t")
                            f.draw_txt(log_surf, f.game_fonts[1], str(y + 1 + int(offset)), (255, 255, 255), (0, leaderboard_wh[1]), "l", "t")
                            blit(leaderboard_dis, log_surf, (0, y * leaderboard_wh[1]))
                            y += 1
                        log_surf = pg.Surface(leaderboard_wh).convert_alpha()
                        f.draw_txt(log_surf, f.game_fonts[1], leaderboard_this[0], (0, 255, 0), leaderboard_wh, "r", "t")
                        f.draw_txt(log_surf, f.game_fonts[1], leaderboard_this[1], (0, 255, 0), (leaderboard_wh[0] - 100, leaderboard_wh[1]), "r", "t")
                        num = f.draw_txt(log_surf, f.game_fonts[1], str(this + 1), (0, 255, 0), (0, leaderboard_wh[1]), "l", "t")
                        f.draw_txt(log_surf, f.game_fonts[1], "YOU", (0, 255, 0), (num.get_width() + 15, leaderboard_wh[1]), "l", "t")
                        blit(leaderboard_dis, log_surf, (0, y * leaderboard_wh[1]))
                        # creates leaderboard row
                        leaderboard_row = pg.Surface(leaderboard_wh).convert_alpha()
                        f.draw_txt(leaderboard_row, f.game_fonts[1], "score", (255, 255, 255), leaderboard_wh, "r", "t")
                        f.draw_txt(leaderboard_row, f.game_fonts[1], "wave", (255, 255, 255), (leaderboard_wh[0] - 100, leaderboard_wh[1]), "r", "t")
                        f.draw_txt(leaderboard_row, f.game_fonts[1], "place", (255, 255, 255), (0, leaderboard_wh[1]), "l", "t")
                        # resets scrolling
                        scroll_x = 0
                        scroll_y = 0

            transition += 1
        else:
            if mode_nxt != mode:
                transition = 0
        if click_pause > 0:
            click_pause -= 1
        dark_fade = copy(dark)
        dark_fade.set_alpha(int(255 * (1 - (m.fabs(transition - 10) / 10))))

        # draws background
        blit(screen, bg, (0, 0))

        # changes final camera by screen_wh offset
        cam_xy = (cam_xy[0] - (screen_wh[0]/2), cam_xy[1] - (screen_wh[1]/2))

        if not (mode == 2 and not mode_menu):
            # ticks buttons and sliders
            for obj in menu_obj[mode - 1]:
                if type(obj) == Button:
                    obj.tick((pg.mouse.get_pos()[0] - (screen_wh[0] / 2), pg.mouse.get_pos()[1] - (screen_wh[1] / 2)), pg.mouse.get_pressed(3)[0])
                    if obj.clicked:
                        click_pause = 5
                        if obj.job == "play_game":
                            mode_nxt = 2
                        if obj.job == "return_home":
                            mode_nxt = 1
                        if obj.job == "mode_menu":
                            mode_menu = not mode_menu
                if type(obj) == Slider:
                    obj.tick((pg.mouse.get_pos()[0] - (screen_wh[0] / 2), pg.mouse.get_pos()[1] - (screen_wh[1] / 2)), pg.mouse.get_pressed(3)[0])
                    if obj.clicked:
                        click_pause = 5
                        if obj.job == "volume_slider":
                            volume = obj.value / obj.value_max

        if mode == 2:
            # sets mode menu
            if pg.key.get_pressed()[pg.K_ESCAPE]:
                if mode_menu_m == 0:
                    mode_menu_m = 1
                    mode_menu = not mode_menu
            else:
                if mode_menu_m == 1:
                    mode_menu_m = 0
            if not mode_menu:
                # creates asteroids
                asteroid_t -= 1 * int(asteroid_t > 0)
                if asteroid_t == 0 and len(asteroids) < 25:
                    success = False
                    while not success:
                        # generates random direction, size, and time until next asteroid
                        asteroid_d = randint(0, 360)
                        if randint(0, 2) == 0:
                            asteroid_s = 3
                        elif randint(0, 2) == 0:
                            asteroid_s = 2
                        else:
                            asteroid_s = 1
                        asteroid_t = randint(m.floor(2 * 60), m.floor(5 * 60))
                        # shortens time based on size
                        if asteroid_s == 1:
                            asteroid_t *= 1
                        elif asteroid_s == 2:
                            asteroid_t *= 0.5
                        elif asteroid_s == 3:
                            asteroid_t *= 0.25
                        asteroid_t = m.floor(asteroid_t)
                        # gets radius of screen
                        screen_dist = 0.75 * f.distance(0, 0, screen_wh[0], screen_wh[1])
                        # generates asteroid xy pos based on radius
                        asteroid_xy = (
                            player.x + (screen_dist * m.cos(m.radians(asteroid_d))),
                            player.y - (screen_dist * m.sin(m.radians(asteroid_d)))
                        )
                        if m.fabs(asteroid_xy[0]) < game_wh[0] and m.fabs(asteroid_xy[1]) < game_wh[1]:
                            success = True
                            # creates asteroid
                            asteroids.append(Asteroid(screen, asteroid_xy[0], asteroid_xy[1], asteroid_s, 90 - asteroid_d))

                # wave creation
                intermission = False
                if len(enemies) == 0:
                    if wave_t == 0:
                        if len(waves) > wave_count:
                            wave_queue = waves[wave_count].gen_queue()
                            wave_count += 1
                        else:
                            wave_queue = list()
                            portal = Portal("portal.svg", screen, 0, 0)
                    else:
                        intermission = True
                        wave_t -= 1
                        if len(waves) < wave_count + 1 and not game_over:
                            game_over = True
                # generates enemy if queue has enemies
                if len(wave_queue) > 0:
                    wave_t = int(60 * 7.5)
                    enemies_t -= 1 * int(enemies_t > 0)
                    if enemies_t == 0 and len(enemies) < 25:
                        # randomly generates enemy direction and deletes from wave queue
                        enemies_t = 30
                        enemy_t = wave_queue[0]
                        wave_queue = wave_queue[1:len(wave_queue)]
                        success = False
                        while not success:
                            # generates random direction
                            enemy_d = randint(0, 360)
                            # gets radius of screen
                            screen_dist = 0.75 * f.distance(0, 0, screen_wh[0], screen_wh[1])
                            # generates enemy xy pos based on radius
                            enemy_xy = (
                                player.x + (screen_dist * m.cos(m.radians(enemy_d))),
                                player.y - (screen_dist * m.sin(m.radians(enemy_d)))
                            )
                            if m.fabs(enemy_xy[0]) < game_wh[0] and m.fabs(enemy_xy[1]) < game_wh[1]:
                                success = True
                                # creates enemy
                                enemies.append(Enemy(screen, enemy_xy[0], enemy_xy[1], enemy_t))

        # ticks objects
        # ticks sounds and sets volume and deletes
        if len(sounds) > 0:
            new_sounds = []
            for sound in sounds:
                sound.tick(player)
                sound.set_volume(volume)
                if sound.playing:
                    new_sounds.append(sound)
            # updates list
            sounds = new_sounds
        if mode == 2 and not mode_menu:
            # ticks player and shoots
            result = player.tick(get_controls(pg.key.get_pressed(), click_pause), pg.mouse.get_pos(), cam_xy, game_wh, intermission, portal)
            if result > 0:
                projectiles.append(Projectile(screen, player.x, player.y, 0, 0, (1, result), player.dir))
                sounds.append(f.Sound("shoot_1.wav", player.x, player.y, 0.5))
                if result == 2:
                    cam_shk = shake(cam_shk, 10)
                    sounds.append(f.Sound("shoot_2.wav", player.x, player.y, 0.5))
                    sounds.append(f.Sound("explode_1.wav", player.x, player.y, 0.25))
            if player.hp == 0:
                if game_over:
                    mode_nxt = 4
                else:
                    mode_nxt = 3
            # ticks shield
            shield.tick(player)
            # ticks asteroid
            if len(asteroids) > 0:
                new_asteroids = list()
                for asteroid in asteroids:
                    result = asteroid.tick(player, asteroids, game_wh, portal)
                    if result is None:
                        # asteroid alive
                        new_asteroids.append(asteroid)
                    else:
                        if type(result) in (float, int):
                            # damage player
                            damage = player.damage(result, asteroid.x, asteroid.y)
                            stay_time = [12, 9, 6][[2, 1, 0.5].index(result)]
                            damages.append(Damage(player.x, player.y, damage, stay_time))
                            damages.append(Damage(asteroid.x, asteroid.y, 1, 9))
                            cam_shk = shake(cam_shk, 25)
                            new_asteroids.append(asteroid)
                        elif type(result) is tuple:
                            # asteroid destroyed
                            if result[0] > 0:
                                sounds.append(f.Sound("explode_2.wav", asteroid.x, asteroid.y, 1))
                                if asteroid.size == 1:
                                    sounds.append(f.Sound("explode_1.wav", asteroid.x, asteroid.y, 1))
                                if asteroid.dmg_team == 1:
                                    player.score += result[0]
                            new_asteroids.extend(result[1])
                # updates list
                asteroids = new_asteroids
            # ticks projectiles
            if len(projectiles) > 0:
                new_projectiles = list()
                for projectile in projectiles:
                    result = projectile.tick(player, asteroids, enemies, game_wh, portal)
                    if result == 1:
                        # projectile destroyed
                        stay_time = [9, 12][[1, 3].index(projectile.damage)]
                        damages.append(Damage(projectile.x, projectile.y, projectile.damage, stay_time))
                    if result == 0:
                        # projectile alive
                        new_projectiles.append(projectile)
                # updates list
                projectiles = new_projectiles
            # ticks enemies
            if len(enemies) > 0:
                new_enemies = list()
                for enemy in enemies:
                    result = enemy.tick(player, asteroids, enemies, portal)
                    if type(result) == int:
                        if result == 0:
                            new_enemies.append(enemy)
                        else:
                            player.score += enemy.points_l[enemy.type - 1]
                    else:
                        for damager in result[0]:
                            if type(damager) == Asteroid:
                                stay_time = [12, 9, 6][[2, 1, 0.5].index(damager.dmg_l[damager.size - 1])]
                                damages.append(Damage(enemy.x, enemy.y, damager.dmg_l[damager.size - 1], stay_time))
                                damages.append(Damage(damager.x, damager.y, 1, 9))
                            elif type(damager) == Player:
                                damages.append(Damage(enemy.x, enemy.y, 1, 9))
                                damages.append(Damage(damager.x, damager.y, player.damage(1, damager.x, damager.y), 9))
                        for projectile in result[1]:
                            if projectile[0] > 0:
                                projectiles.append(Projectile(screen, enemy.x, enemy.y, projectile[1], projectile[2], (2, projectile[0]), enemy.m_dir))
                                sounds.append(f.Sound("shoot_1.wav", enemy.x, enemy.y, 0.5))
                                if projectile[0] == 2:
                                    sounds.append(f.Sound("shoot_2.wav", enemy.x, enemy.y, 0.5))
                                    sounds.append(f.Sound("explode_1.wav", enemy.x, enemy.y, 0.25))
                            else:
                                if enemy.type == 4:
                                    drone = Enemy(screen, enemy.x, enemy.y, 5)
                                    drone.vx += 15 * m.cos(m.radians(enemy.m_dir))
                                    drone.vy += 15 * m.sin(m.radians(enemy.m_dir))
                                    drone.spawn = 0
                                    new_enemies.append(drone)
                                    sounds.append(f.Sound("explode_1.wav", enemy.x, enemy.y, 0.25))
                                if enemy.type == 7:
                                    drone = Enemy(screen, enemy.x, enemy.y, 4)
                                    drone.vx += 15 * m.cos(m.radians(enemy.m_dir))
                                    drone.vy += 15 * m.sin(m.radians(enemy.m_dir))
                                    drone.spawn = 0
                                    new_enemies.append(drone)
                                    sounds.append(f.Sound("explode_1.wav", enemy.x, enemy.y, 0.25))
                                if enemy.type == 8:
                                    offset_dir = 90
                                    for i in range(2):
                                        drone = Enemy(screen, enemy.x, enemy.y, 5)
                                        drone.vx += 30 * m.cos(m.radians(enemy.m_dir + offset_dir))
                                        drone.vy += 30 * m.sin(m.radians(enemy.m_dir + offset_dir))
                                        drone.spawn = 0
                                        new_enemies.append(drone)
                                        offset_dir *= -1
                                    sounds.append(f.Sound("explode_1.wav", enemy.x, enemy.y, 0.25))
                        new_enemies.append(enemy)
                enemies = new_enemies
            # ticks portal
            if portal is not None:
                portal.tick()
            # ticks damages
            if len(damages) > 0:
                new_damages = list()
                for damage in damages:
                    if damage.time == 0:
                        sounds.append(f.Sound("hit.wav", damage.x, damage.y, 0.5 + (0.5 * (damage.damage / 3))))
                    result = damage.tick()
                    if result == 0:
                        # delete damage
                        new_damages.append(damage)
                # updates list
                damages = new_damages
        # tick stars
        for i in range(len(stars)):
            para = 0.25 + (0.5 * (1 - ((stars[i][0] - 1) / 2)))
            new_star = [stars[i][0], list(stars[i][1])]
            # move star onto screen upon off-screen
            while new_star[1][0] - (cam_xy[0] * para) > screen_wh[0] + stars_s[0].get_width():
                new_star[1][0] -= (screen_wh[0] + stars_s[0].get_width()) / para
            while new_star[1][0] - (cam_xy[0] * para) < -stars_s[0].get_width():
                new_star[1][0] += (screen_wh[0] + stars_s[0].get_width()) / para
            while new_star[1][1] - (cam_xy[1] * para) > screen_wh[1] + stars_s[0].get_width():
                new_star[1][1] -= (screen_wh[1] + stars_s[0].get_width()) / para
            while new_star[1][1] - (cam_xy[1] * para) < -stars_s[0].get_width():
                new_star[1][1] += (screen_wh[1] + stars_s[0].get_width()) / para
            stars[i] = (new_star[0], tuple(new_star[1]))
        # draws objects
        # creates minimap
        minimap.fill((0, 5, 20))
        # renders stars
        for star in stars:
            para = 0.25 + (0.5 * (1 - ((star[0] - 1) / 2)))
            blit(screen, stars_s[star[0] - 1], (star[1][0] - (cam_xy[0] * para), star[1][1] - (cam_xy[1] * para)))
        if mode == 2 or mode == 3:
            # renders portal
            if portal is not None:
                blit(screen, portal.render((0, 0))[0], portal.render(cam_xy)[1])
                blit(minimap, mini_neutral, minimap_pos((portal.x, portal.y), game_wh, minimap))
            # renders projectiles
            if len(projectiles) > 0:
                for projectile in projectiles:
                    blit(screen, projectile.render((0, 0))[0], projectile.render(cam_xy)[1])
            # renders asteroids
            if len(asteroids) > 0:
                for asteroid in asteroids:
                    blit(screen, asteroid.render((0, 0))[0], asteroid.render(cam_xy)[1])
                    blit(minimap, mini_neutral, minimap_pos((asteroid.x, asteroid.y), game_wh, minimap))
            # renders player
            if mode == 2:
                blit(screen, player.render((0, 0))[0], player.render(cam_xy)[1])
                blit(minimap, mini_friend, minimap_pos((player.x, player.y), game_wh, minimap))
                # renders shield
                blit(screen, shield.render((0, 0))[0], shield.render(cam_xy)[1])
            # renders enemies
            if len(enemies) > 0:
                for enemy in enemies:
                    blit(screen, enemy.render((0, 0))[0], enemy.render(cam_xy)[1])
                    blit(minimap, mini_enemy, minimap_pos((enemy.x, enemy.y), game_wh, minimap))
            # renders damage
            if len(damages) > 0:
                for damage in damages:
                    blit(screen, damage.render((0, 0))[0], damage.render(cam_xy)[1])
        # renders border
        for i in range(2):
            new_cam_xy = (cam_xy[0] + (screen_wh[0] / 2), cam_xy[1] + (screen_wh[1] / 2))
            x = new_cam_xy[0]
            if m.fabs(x) > game_wh[0] - (screen_wh[0] / 2):
                sign = x / m.fabs(x)
                x = sign * (game_wh[0] - (screen_wh[0] / 2))
            y = new_cam_xy[1]
            if m.fabs(y) > game_wh[1] - (screen_wh[1] / 2):
                sign = y / m.fabs(y)
                y = sign * (game_wh[1] - (screen_wh[1] / 2))
            x -= border_x[i].get_width() / 2
            y -= border_y[i].get_height() / 2
            blit(screen, border_x[i], (x - cam_xy[0], game_wh[1] - cam_xy[1] - (border_x[i].get_height() / 2)))
            blit(screen, border_y[i], (game_wh[0] - cam_xy[0] - (border_y[i].get_width() / 2), y - cam_xy[1]))
            blit(screen, border_x[i], (x - cam_xy[0], -game_wh[1] - cam_xy[1] - (border_x[i].get_height() / 2)))
            blit(screen, border_y[i], (-game_wh[0] - cam_xy[0] - (border_y[i].get_width() / 2), y - cam_xy[1]))

        if mode == 1:
            # camera scrolls to mouse
            cam_xy_p = (0.25 * (pg.mouse.get_pos()[0] - (screen_wh[0] / 2)), 0.25 * (pg.mouse.get_pos()[1] - (screen_wh[1] / 2)))
        elif (mode == 2 or mode == 3) and not mode_menu:
            # camera scrolls to player
            cam_xy_p = ch_cam_xy(cam_xy_p, m.floor((player.x - cam_xy_p[0]) / 3), m.floor((player.y - cam_xy_p[1]) / 3))
        # ticks camera shake
        cam_shk = shake(cam_shk, 0)
        # applies player camera and shake camera to final camera
        cam_xy = (cam_xy_p[0] + cam_shk[0], cam_xy_p[1] + cam_shk[1])

        # draws shield glow
        """ disabled to increase fps
        draw_glow(shield_glow, screen, player.shield / 30, screen_wh)
        """

        # draws border glow
        """ disabled to increase fps
        glow = list()
        for i in range(2):
            glow.append(0)
            if m.fabs(cam_xy[i]) > game_wh[i] - 600:
                glow[i] = (m.fabs(cam_xy[i]) - (game_wh[i] - 600)) / 600
        if glow[0] > glow[1]:
            glow = glow[0]
        elif glow[1] > glow[0]:
            glow = glow[1]
        else:
            glow = (glow[0] + glow[1]) / 2
        draw_glow(border_glow, screen, glow, screen_wh)
        """

        if mode == 1:
            # darken background
            menu_fade = copy(dark)
            menu_fade.set_alpha(64)
            blit(screen, menu_fade, (0, 0))
            # draws title
            blit(screen, game_title, ((screen_wh[0] - game_title.get_width()) / 2, (screen_wh[1] - game_title.get_height()) / 2 - 100))
        elif mode == 2:
            # draws hp and energy bars
            draw_bar(screen, hp_symbol, (200, 30), (45, 25), (player.hp, player.hp_o, 100), (0, 255, 0), player.hp_u)
            draw_bar(screen, e_symbol, (100, 20), (45, 65), (player.energy, player.energy_o, 60), (0, 255, 255), player.energy_u)
            # draws score
            f.draw_txt(screen, f.game_fonts[1], player.score_d, (255, 255, 255), (screen_wh[0] - 25, 25), "r", "b")
            # draws wave
            if not game_over:
                if intermission:
                    f.draw_txt(screen, f.game_fonts[2], "NEXT: WAVE " + str(wave_count + 1), (255, 255, 255), (screen_wh[0] - 25, 55), "r", "b")
                else:
                    f.draw_txt(screen, f.game_fonts[2], "WAVE " + str(wave_count), (255, 255, 255), (screen_wh[0] - 25, 55), "r", "b")

            # draws minimap
            pg.draw.rect(minimap, (255, 255, 255), pg.Rect((0, 0), (minimap.get_width() - 3, minimap.get_height() - 3)), 3)
            pos = (screen_wh[0] - 125, screen_wh[1] - 125)
            blit(screen, pg.transform.scale(minimap, (100, 100)), pos)

            # draws fps
            f.draw_txt(screen, f.game_fonts[2], str(m.floor(fps_av * 10) / 10), (255, 255, 255), (screen_wh[0] - 25, screen_wh[1] - 150), "r", "b")

            if mode_menu:
                # darkens background
                menu_fade = copy(dark)
                menu_fade.set_alpha(128)
                blit(screen, menu_fade, (0, 0))
        elif mode == 3:
            # darken background
            menu_fade = copy(dark)
            menu_fade.set_alpha(128)
            blit(screen, menu_fade, (0, 0))

            # draws leaderboard
            height = (leaderboard_dis.get_height() / (len(leaderboard) + 1))
            new_leaderboard_dis = pg.Surface((leaderboard_dis.get_width(), 300)).convert_alpha()
            if leaderboard_dis.get_height() > 300:
                pos = [0, scroll_y]
                if scroll_y > 0:
                    pos[1] = 0
                elif scroll_y < -leaderboard_dis.get_width() - height:
                    pos[1] = -leaderboard_dis.get_width() - height
                scroll_y = pos[1]
                pos = tuple(pos)
            else:
                pos = (0, 300 - leaderboard_dis.get_height())
            blit(new_leaderboard_dis, leaderboard_dis, pos)
            pos = ((screen_wh[0] - new_leaderboard_dis.get_width()) / 2, (screen_wh[1] / 2) - new_leaderboard_dis.get_height())
            blit(screen, new_leaderboard_dis, (pos[0], pos[1] + 100))
            pos = ((screen_wh[0] - new_leaderboard_dis.get_width()) / 2, (screen_wh[1] / 2) - new_leaderboard_dis.get_height() - height)
            blit(screen, leaderboard_row, (pos[0], pos[1] + 100))

        if not (mode == 2 and not mode_menu):
            # draws menu objects
            for obj in menu_obj[mode - 1]:
                blit(screen, obj.render()[0], (obj.render()[1][0] + (screen_wh[0] / 2), obj.render()[1][1] + (screen_wh[1] / 2)))

        if mode != 2:
            # scrolls
            if m.fabs(scroll_vx) > 1:
                scroll_vx *= 0.85
                scroll_x += scroll_vx
            elif m.fabs(scroll_vx) > 0:
                scroll_vx = 0
            if m.fabs(scroll_vy) > 1:
                scroll_vy *= 0.85
                scroll_y += scroll_vy
            elif m.fabs(scroll_vy) > 0:
                scroll_vy = 0

        # draws transition
        if 20 > transition > 0:
            blit(screen, dark_fade, (0, 0))

        # update
        pg.display.flip()
        fps_clock.tick(fps)

        # fps checker
        c_time_2 = round(time() * 1000)
        fps_check = 1 / ((c_time_2 - c_time) / 1000)
        fps_av = (fps_av + fps_check) / 2


# triggers game function
main()
