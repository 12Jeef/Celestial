# crucial functions
import func as f
from playerobj import Player, Portal
# pygame and math
import pygame as pg
import math as m
# random asteroid generation
from random import randint


class Asteroid:
    # sets up base variables
    hp_l = [10, 5, 1]
    speed_l = [1, 2.5, 5]
    spin_l = [0.5, 1, 2]
    size_l = [87.5, 50, 25]
    dmg_l = [2, 1, 0.5]
    dmg_team = 0
    points_l = [100, 50, 10]
    dir = 0
    vx = 0
    vy = 0
    damaged = False
    id = ""
    spawn = 30

    def __init__(self, surface: pg.Surface, x: f.coord, y: f.coord, size: int, m_dir: f.number):
        # loads image based on type
        self.image = f.load_image("asteroid_" + str(size) + ".svg", surface).convert_alpha()
        # saves surface for next creation
        self.surface = surface
        # saves xy pos and size
        self.x = x
        self.y = y
        self.size = size
        # sets hp and speed based on lists
        self.hp = self.hp_l[size - 1]
        self.speed = self.speed_l[size - 1]
        # sets a move direction and a random display direction
        self.m_dir = m_dir + 90
        self.dir = randint(0, 360)
        # randomly generates vel xy
        move = 2 * randint(0, 10) / 10
        self.vx = move * self.speed * m.cos(m.radians(self.m_dir))
        self.vy = move * self.speed * m.sin(m.radians(self.m_dir))

    def tick(self, player: Player, asteroids: list, game_wh: f.position, portal: Portal) -> (tuple[int, list], float, int):
        if self.damaged:
            self.damaged = False
        # rotates asteroid by spin speed
        self.dir += self.spin_l[self.size - 1]
        # changes xy pos by move dir and vel xy
        self.x += self.speed * m.cos(m.radians(self.m_dir)) + self.vx
        self.y += self.speed * m.sin(m.radians(self.m_dir)) - self.vy
        if portal is not None:
            # moves towards portal
            speed = 3 * (1 - (f.distance(self.x, self.y, portal.x, portal.y) / 2400))
            if speed < 0.55:
                speed = 0.55
            self.vx += speed * m.sin(m.radians(f.point_towards(self.x, self.y, portal.x, portal.y) + 90))
            self.vy -= speed * m.cos(m.radians(f.point_towards(self.x, self.y, portal.x, portal.y) + 90))
            if f.distance(self.x, self.y, portal.x, portal.y) < 100:
                self.damage(3, portal.x, portal.y, 0)
        # friction
        if m.fabs(self.vx) > 1:
            self.vx *= 0.85
        elif m.fabs(self.vx) > 0:
            self.vx = 0
        if m.fabs(self.vy) > 1:
            self.vy *= 0.85
        elif m.fabs(self.vy) > 0:
            self.vy = 0
        # asteroid too far from player - delete for efficiency
        screen_dist = 1.5 * f.distance(0, 0, self.surface.get_width(), self.surface.get_height())
        if f.distance(self.x, self.y, player.x, player.y) > screen_dist:
            return 0, []
        # asteroid outside border
        game_wh = (game_wh[0] + (2 * self.size_l[self.size - 1]), game_wh[1] + (2 * self.size_l[self.size - 1]))
        if m.fabs(self.x) > game_wh[0] or m.fabs(self.y) > game_wh[1]:
            return 0, []
        # bounces off other asteroids
        if self.spawn > 0:
            self.spawn -= 1
        else:
            """ disabled to increase fps
            for asteroid in asteroids:
                if self.x != asteroid.x and self.y != asteroid.y:
                    dist = distance(self.x, self.y, asteroid.x, asteroid.y)
                    if dist < self.size_l[self.size - 1] + self.size_l[asteroid.size - 1]:
                        self.speed *= 0.1
                        self.damage(0, asteroid.x, asteroid.y)
                        self.speed /= 0.1
            """
        # if asteroid is dead
        if not self.hp > 0:
            # if asteroid is larger than smallest size
            if self.size != 3:
                # creates broken asteroids and adds to list
                create = list()
                for i in range((3 * (1 + int(self.size == 2))) - randint(0, 2)):
                    create.append(Asteroid(self.surface, self.x, self.y, self.size + 1, self.m_dir + randint(0, 360)))
                if self.size == 1:
                    for i in range(6 - randint(0, 2)):
                        create.append(Asteroid(self.surface, self.x, self.y, self.size + 2, self.m_dir + randint(0, 360)))
                return self.points_l[self.size - 1], create
            # asteroid is smallest size, deletes
            return self.points_l[self.size - 1], []
        if f.distance(self.x, self.y, player.x, player.y) < self.size_l[self.size - 1] + 30:
            # damage
            return self.damage(1, player.x, player.y, 1)

    def render(self, cam_xy: f.position) -> f.rendering:
        # rotates asteroid based on dir
        image_rot = pg.transform.rotate(self.image, self.dir - 90)
        # offsets image so it's centered
        aster_ch_x = -image_rot.get_width() / 2
        aster_ch_y = -image_rot.get_height() / 2
        # flash if damaged
        if self.damaged:
            pg.draw.circle(image_rot, (255, 255, 255), (-aster_ch_x, -aster_ch_y), self.size_l[self.size - 1])
        return image_rot, (aster_ch_x + self.x - cam_xy[0], aster_ch_y + self.y - cam_xy[1])

    def damage(self, hp: f.number, x: f.coord, y: f.coord, team: int) -> f.number:
        # damages itself
        self.hp -= m.ceil(hp * 2) / 2
        if self.hp < 0:
            self.hp = 0
        if hp > 0:
            self.damaged = True
        self.dmg_team = team
        # bounces off damager
        bounce_dir = f.point_towards(x, y, self.x, self.y)
        self.vx += 7.5 * self.speed * m.cos(m.radians(bounce_dir))
        self.vy += 7.5 * self.speed * m.sin(m.radians(bounce_dir))
        return self.dmg_l[self.size - 1]


class Projectile:
    # sets up base variables
    speed = 15
    delete = 0
    damage = 0

    def __init__(self, surface: pg.Surface, x: f.coord, y: f.coord, x_add: f.number, y_add: f.number, proj_t: tuple[int, int], proj_dir: f.number):
        # loads image based on type
        self.image = f.load_image("proj_" + str(proj_t[0]) + "_" + str(proj_t[1]) + ".svg", surface).convert_alpha()
        # saves surface for later deletion
        self.surface = surface
        # saves xy pos and dir
        self.x = x
        self.y = y
        self.dir = proj_dir
        # shifts xy pos based on dir and x_add and y_add
        self.x += x_add * m.sin(m.radians(self.dir))
        self.y += x_add * m.cos(m.radians(self.dir))
        self.x += y_add * m.sin(m.radians(self.dir + 90))
        self.y += y_add * m.cos(m.radians(self.dir + 90))
        # gets projectile team and type
        self.team = proj_t[0]
        self.type = proj_t[1]
        # pre-rotates image to increase efficiency
        self.image_rot = pg.transform.rotate(self.image, self.dir - 90)
        # sets projectile damage based on type
        self.damage = [1, 3][self.type - 1]

    def tick(self, player: Player, asteroids: list, enemies: list, game_wh: f.position, portal: (Portal, None)) -> int:
        # changes xy pos by dir
        if self.delete == 0:
            self.x += self.speed * m.sin(m.radians(self.dir + 90))
            self.y += self.speed * m.cos(m.radians(self.dir + 90))
            if portal is not None:
                # moves towards portal
                d = -(m.fmod(m.fmod(f.point_towards(self.x, self.y, portal.x, portal.y), 360) - m.fmod(self.dir, 360), 360) - 180)
                self.dir += ((180 - m.fabs(d)) * d / m.fabs(d)) / 3
                self.image_rot = pg.transform.rotate(self.image, self.dir - 90)
                if f.distance(self.x, self.y, portal.x, portal.y) < 100:
                    return 2
            # projectile too far from player - delete for efficiency
            screen_dist = 1.25 * f.distance(0, 0, self.surface.get_width(), self.surface.get_height())
            if f.distance(self.x, self.y, player.x, player.y) > screen_dist:
                return 1
            # projectile outside border
            game_wh = (game_wh[0] + self.image_rot.get_width(), game_wh[1] + self.image_rot.get_height())
            if m.fabs(self.x) > game_wh[0] or m.fabs(self.y) > game_wh[1]:
                return 2
            # collide with asteroids if not in death animation
            for asteroid in asteroids:
                if f.distance(self.x, self.y, asteroid.x, asteroid.y) < asteroid.size_l[asteroid.size - 1] + 10:
                    asteroid.damage(self.damage, self.x, self.y, self.team)
                    self.delete = 1
            # if is player bullet collide with enemies
            if self.team == 1:
                for enemy in enemies:
                    if enemy.delete == 0:
                        if f.distance(self.x, self.y, enemy.x, enemy.y) < 30 + enemy.size:
                            enemy.damage(self.damage, self.x, self.y)
                            self.delete = 1
            # if is enemy bullet collide with player
            elif self.team == 2:
                if f.distance(self.x, self.y, player.x, player.y) < 30 + 10:
                    player.damage(self.damage, self.x, self.y)
                    self.delete = 1
        else:
            # death animation
            self.delete += 1
            if self.delete > 3:
                return 1
        return 0

    def render(self, cam_xy: f.position) -> f.rendering:
        if self.delete > 1:
            # death animation
            del_p = (self.delete - 1) / 2
            image_rot = pg.Surface((100, 100)).convert_alpha()
            color_idx = (0, 0, 0)
            size = [25, 50][self.type - 1]
            if self.team == 1:
                color_idx = (1, 0, 0)
            elif self.team == 2:
                color_idx = (0, 1, 1)
            color = [255, 255, 255]
            for i in range(len(color_idx)):
                if color_idx[i] == 1:
                    color[i] = int(255 * (1 - del_p))
            pg.draw.circle(image_rot, color, (50, 50), size * (0.5 + (0.5 * del_p)))
            if self.damage > 2:
                pg.draw.circle(image_rot, (255, 255, 255), (50, 50), size * 0.5 * (0.5 + (0.5 * del_p)))
        else:
            # loads rotated image
            image_rot = self.image_rot
        # offsets image so it's centered
        proj_ch_x = -image_rot.get_width() / 2
        proj_ch_y = -image_rot.get_height() / 2
        return image_rot, (proj_ch_x + self.x - cam_xy[0], proj_ch_y + self.y - cam_xy[1])


class Damage:
    # sets up base variables
    time = 0

    def __init__(self, x: f.coord, y: f.coord, damage: f.number, stay_time: int):
        # saves xy pos and size
        self.x = x
        self.y = y
        # saves stay time to decide when to delete
        self.stay_time = stay_time
        # sets damage
        if int(damage) == damage:
            self.damage = int(damage)
        else:
            self.damage = damage
        # creates image
        self.text = pg.Surface((100, 100)).convert_alpha()
        f.draw_txt(self.text, f.game_fonts[1], "-" + str(self.damage), (255, 0, 0), (50, 50), "m", "m")

    def tick(self):
        # moves up
        self.y -= 1
        # increases time
        self.time += 1
        # decides to delete
        if self.time > self.stay_time:
            return 1
        return 0

    def render(self, cam_xy: f.position) -> f.rendering:
        # creates text
        text = self.text
        # fades away 6 frames before delete
        if self.time > self.stay_time - 3:
            text.set_alpha(int(255 * (1 - ((self.time - (self.stay_time - 3)) / 3))))
        # offsets image so it's centered
        text_ch_x = -text.get_width() / 2
        text_ch_y = -text.get_height() / 2
        return text, (text_ch_x + self.x - cam_xy[0], text_ch_y + self.y - cam_xy[1])
