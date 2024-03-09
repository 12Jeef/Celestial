# crucial functions
import func as f
# pygame and math
import pygame as pg
import math as m


class Player:
    # sets up base variables
    hp = 1000
    hp_o = hp
    hp_ol = []
    hp_u = 0
    dir = 0
    reload = 0
    shield = 0
    energy = 0
    energy_o = energy
    energy_ol = []
    energy_u = 0
    vx = 0
    vy = 0
    score = 0
    score_d = score

    def __init__(self, image: str, surface: pg.Surface, x: f.coord, y: f.coord):
        # loads image
        self.image = f.load_image(image, surface).convert_alpha()
        # saves xy pos
        self.x = x
        self.y = y

    def tick(self, player_controls: tuple[[bool] * 3], mouse_pos: f.position, cam_xy: f.position, game_wh: f.position, intermission: bool, portal: (object, None)) -> int:
        # changes vel x and y by controls
        if m.fabs((int(player_controls[0]) - int(player_controls[1])) * 0.75) > 0:
            self.vx += (int(player_controls[0]) - int(player_controls[1])) * 0.75
        if m.fabs((int(player_controls[2]) - int(player_controls[3])) * 0.75) > 0:
            self.vy += (int(player_controls[2]) - int(player_controls[3])) * 0.75
        if portal is not None:
            # moves towards portal
            speed = 3 * (1 - (f.distance(self.x, self.y, portal.x, portal.y) / 2400))
            if speed < 0.55:
                speed = 0.55
            self.vx += speed * m.sin(m.radians(f.point_towards(self.x, self.y, portal.x, portal.y) + 90))
            self.vy -= speed * m.cos(m.radians(f.point_towards(self.x, self.y, portal.x, portal.y) + 90))
            if f.distance(self.x, self.y, portal.x, portal.y) < 100:
                self.damage(3, portal.x, portal.y)
        # restricts player to world border
        if self.x != 0:
            prop = (self.x / m.fabs(self.x))
            if m.fabs(int(m.fabs(self.x) > game_wh[0]) * (m.fabs(self.x) - game_wh[0]) * prop * 0.2) > 0:
                self.vx -= int(m.fabs(self.x) > game_wh[0]) * (m.fabs(self.x) - game_wh[0]) * prop * 0.2
        if self.y != 0:
            prop = (self.y / m.fabs(self.y))
            if m.fabs(int(m.fabs(self.y) > game_wh[1]) * (m.fabs(self.y) - game_wh[1]) * prop * 0.2) > 0:
                self.vy += int(m.fabs(self.y) > game_wh[1]) * (m.fabs(self.y) - game_wh[1]) * prop * 0.2
        # friction and moves player
        if m.fabs(self.vx) > 0.5:
            self.vx *= 0.85
            self.x += self.vx
        elif m.fabs(self.vx) > 0:
            self.vx = 0
        if m.fabs(self.vy) > 0.5:
            self.vy *= 0.85
            self.y -= self.vy
        elif m.fabs(self.vy) > 0:
            self.vy = 0
        # ticks reload, shield, and energy
        if self.reload > 0:
            self.reload -= 1
        if self.shield > 0:
            self.shield -= 1
        if self.energy < 60:
            self.energy += 1
        # regenerates health
        if self.hp < 75 and intermission:
            self.hp += m.floor(0.5 * (m.pow(75 - self.hp, 2) / m.pow(75, 2)) * 100) / 100
        # used for hp bar effect
        self.hp_ol.append(self.hp)
        if len(self.hp_ol) > 10:
            self.hp_o += (self.hp_ol[0] - self.hp_o)/3
            self.hp_ol = self.hp_ol[1:len(self.hp_ol)]
        # used for energy bar effect
        self.energy_ol.append(self.energy)
        if len(self.energy_ol) > 10:
            self.energy_o += (self.energy_ol[0] - self.energy_o)/3
            self.energy_ol = self.energy_ol[1:len(self.energy_ol)]
        # changes score display
        if self.score_d != self.score:
            self.score_d += m.ceil((self.score - self.score_d)/3)
        # points player towards mouse
        self.dir = f.point_towards(self.x - cam_xy[0], self.y - cam_xy[1], mouse_pos[0], mouse_pos[1])
        # generates shoot value
        shoot = 0
        if player_controls[4] == 1 and self.reload == 0:
            self.shield = 15
            self.reload = 5
            shoot = 1
            self.vx -= 7.5 * m.cos(m.radians(self.dir))
            self.vy -= 7.5 * m.sin(m.radians(self.dir))
            if self.energy == 60:
                self.shield = 30
                self.energy = 0
                self.energy_u = 10
                shoot = 2
                self.vx -= 7.5 * m.cos(m.radians(self.dir))
                self.vy -= 7.5 * m.sin(m.radians(self.dir))
        # ticks hp and energy updating
        if self.hp_u > 0:
            self.hp_u -= 1
        if self.energy_u > 0:
            self.energy_u -= 1
        # returns final shoot value
        return shoot

    def render(self, cam_xy: f.position) -> f.rendering:
        # rotates player based on dir
        image_rot = pg.transform.rotate(self.image, self.dir - 90)
        # offsets image so it's centered
        player_x_ch = -image_rot.get_width() / 2
        player_y_ch = -image_rot.get_height() / 2
        return image_rot, (player_x_ch + self.x - cam_xy[0], player_y_ch + self.y - cam_xy[1])

    def damage(self, hp: f.number, x: f.coord, y: f.coord) -> f.number:
        # damages itself and updates
        hp = m.ceil((hp * (1 - (0.75 * (self.shield / 30)))) * 2) / 2
        self.hp -= hp
        if self.hp < 0:
            self.hp = 0
        self.hp_u = 10
        # bounces off damager
        bounce_dir = f.point_towards(x, y, self.x, self.y)
        self.vx += 7.5 * (1 - (0.5 * (self.shield / 30))) * m.cos(m.radians(bounce_dir))
        self.vy += 7.5 * (1 - (0.5 * (self.shield / 30))) * m.sin(m.radians(bounce_dir))
        return hp


class Shield:
    # sets up base variables
    shield = 0
    dir = 0
    x = 0
    y = 0

    def __init__(self, image: str, surface: pg.Surface):
        # loads image
        self.image = f.load_image(image, surface).convert_alpha()

    def tick(self, player: Player):
        # takes dir, shield, and xy value to player values
        self.dir = player.dir
        if self.shield != player.shield:
            self.shield = player.shield
        if self.x != player.x:
            self.x = player.x
        if self.y != player.y:
            self.y = player.y

    def render(self, cam_xy: f.position) -> f.rendering:
        # rotate image
        image_rot = pg.transform.rotate(self.image, self.dir - 90)
        # applies ghost
        image_rot.set_alpha(255 * self.shield / 30)
        # offsets image so it's centered
        shield_x_ch = -image_rot.get_width() / 2
        shield_y_ch = -image_rot.get_height() / 2
        # moves image backwards slightly
        shield_x = shield_x_ch + self.x + (5 * m.sin(m.radians(self.dir - 90)))
        shield_y = shield_y_ch + self.y + (5 * m.cos(m.radians(self.dir - 90)))
        return image_rot, (shield_x - cam_xy[0], shield_y - cam_xy[1])


class Portal:
    dir = 0

    def __init__(self, image: str, surface: pg.Surface, x: f.coord, y: f.coord):
        # loads image
        self.image = f.load_image(image, surface).convert_alpha()
        # saves xy pos
        self.x = x
        self.y = y

    def tick(self):
        # rotates portal
        self.dir += 10

    def render(self, cam_xy: f.position) -> f.rendering:
        # rotate image
        image_rot = pg.transform.rotate(self.image, self.dir)
        # offsets image so it's centered
        port_x_ch = -image_rot.get_width() / 2
        port_y_ch = -image_rot.get_height() / 2
        return image_rot, (port_x_ch + self.x - cam_xy[0], port_y_ch + self.y - cam_xy[1])
