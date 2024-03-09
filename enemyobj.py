# crucial functions
import func as f
from playerobj import Player, Portal
# pygame and math
import pygame as pg
import math as m
# random enemy generation
from random import randint


class Enemy:
    # sets up base variables
    vx = 0
    vy = 0
    dir = 0
    hp_l = [20, 25, 35, 15, 2.5, 150, 25, 50]
    speed_l = [0.75, 1.25, 1.5, 0.75, 1.5, 0.625, 0.75, 1.5]
    size_l = [30, 45, 55, 40, 15, 125, 75, 35]
    points_l = [200, 250, 500, 300, 50, 500, 400, 250]
    rot_l = [1, 1, 2, 3, 1, 4, 3, 25]
    reload = 0
    reload_t = 0
    spawn = 30
    delete = 0
    data = None

    def __init__(self, surface: pg.Surface, x: f.coord, y: f.coord, enemy_type: int):
        # loads image based on type
        self.image = f.load_image("enemy_" + str(enemy_type) + ".svg", surface).convert_alpha()
        # saves xy pos and dir
        self.x = x
        self.y = y
        # gets enemy type
        self.type = enemy_type
        # sets hp, speed, size, and rot based on lists
        self.hp = self.hp_l[enemy_type - 1]
        self.speed = self.speed_l[enemy_type - 1]
        self.size = self.size_l[enemy_type - 1]
        self.rot = self.rot_l[enemy_type - 1]
        # sets random dir
        self.dir = randint(0, 360)
        self.m_dir = self.dir

    def tick(self, player: Player, asteroids: list, enemies: list, portal: (Portal, None)) -> (tuple[list, list], int):
        if self.delete == 0:
            if self.spawn == 0:
                # changes velocity to point towards player
                self.vx += self.speed * m.cos(m.radians(self.m_dir))
                self.vy += self.speed * m.sin(m.radians(self.m_dir))
            if portal is not None:
                # moves towards portal
                speed = 3 * (1 - (f.distance(self.x, self.y, portal.x, portal.y) / 2400))
                if speed < 0.55:
                    speed = 0.55
                self.vx += speed * m.sin(m.radians(f.point_towards(self.x, self.y, portal.x, portal.y) + 90))
                self.vy -= speed * m.cos(m.radians(f.point_towards(self.x, self.y, portal.x, portal.y) + 90))
                if f.distance(self.x, self.y, portal.x, portal.y) < 100:
                    self.damage(3, portal.x, portal.y)
            # friction
            if m.fabs(self.vx) > 0.5:
                self.vx *= 0.85
            elif m.fabs(self.vx) > 0:
                self.vx = 0
            if m.fabs(self.vy) > 0.5:
                self.vy *= 0.85
            elif m.fabs(self.vy) > 0:
                self.vy = 0
            # points towards player, bounces off other enemies
            if self.spawn > 0:
                self.spawn -= 1
            else:
                if not self.type == 8:
                    self.dir = f.point_towards(self.x, self.y, player.x, player.y)
                    for enemy in enemies:
                        if self.x != enemy.x and self.y != enemy.y:
                            dist = f.distance(self.x, self.y, enemy.x, enemy.y)
                            if dist < self.size + enemy.size:
                                self.speed *= 0.1
                                self.damage(0, enemy.x, enemy.y)
                                self.speed /= 0.1
            # changes xy pos by vel xy
            if m.fabs(self.vx) > 0:
                self.x += self.vx
            if m.fabs(self.vy) > 0:
                self.y -= self.vy
            # rotates move dir to match dir
            d = -(m.fmod(m.fmod(self.dir, 360) - m.fmod(self.m_dir, 360), 360) - 180)
            self.m_dir += ((180 - m.fabs(d)) * d / m.fabs(d)) / self.rot
            # creates list of damage objects
            damages_this = list()
            if f.distance(self.x, self.y, player.x, player.y) < self.size + 30:
                self.damage(1, player.x, player.y)
                damages_this.append(player)
            for asteroid in asteroids:
                if f.distance(self.x, self.y, asteroid.x, asteroid.y) < asteroid.size_l[asteroid.size - 1] + self.size:
                    damage = asteroid.damage(1, self.x, self.y, 2)
                    self.damage(damage, asteroid.x, asteroid.y)
                    damages_this.append(asteroid)
            # conditional creation
            allowed = True
            if self.type == 4:
                if len(enemies) > 25:
                    allowed = False
            if self.type == 7:
                if len(enemies) > 10:
                    allowed = False
            if self.type == 8:
                if self.data is None:
                    total_chains = 0
                    for enemy in enemies:
                        if enemy.type == 8:
                            if enemy.x != self.x and enemy.y != self.y:
                                total_chains += 1
                    self.data = total_chains
                else:
                    if self.data > 0:
                        if self.rot != 2:
                            self.rot = 2
                        follower = False
                        for enemy in enemies:
                            if enemy.type == 8:
                                if enemy.x != self.x and enemy.y != self.y:
                                    if enemy.data == self.data - 1:
                                        follower = True
                                        self.dir = f.point_towards(self.x, self.y, enemy.x, enemy.y)
                                        if f.distance(self.x, self.y, enemy.x, enemy.y) > self.size * 0.5:
                                            prop = (f.distance(self.x, self.y, enemy.x, enemy.y) - (self.size * 0.5)) / 50
                                            if prop > 3:
                                                self.speed = self.speed_l[self.type - 1] * 3
                                            else:
                                                self.speed = self.speed_l[self.type - 1] * prop
                                        else:
                                            self.speed = self.speed_l[self.type - 1]
                        if not follower:
                            self.speed = self.speed_l[self.type - 1]
                            self.data -= 1
                    else:
                        if self.rot != self.rot_l[self.type - 1]:
                            self.rot = self.rot_l[self.type - 1]
                        self.dir = f.point_towards(self.x, self.y, player.x, player.y)
            # shoots
            if self.reload == 0:
                projectiles = list()
                if self.spawn == 0 and allowed:
                    self.reload_t += 1
                    # enemy type 1
                    if self.type == 1:
                        if self.reload_t == 1:
                            projectiles.append((2, 0, 0))
                            self.reload = 40
                        if self.reload_t in [2, 3, 4]:
                            projectiles.append((1, 0, 0))
                            self.reload = 25
                        if self.reload_t == 4:
                            self.reload_t = 0
                    # enemy type 2
                    elif self.type == 2:
                        if self.reload_t == 1:
                            projectiles.append((1, -60, 0))
                            self.reload = 20
                        if self.reload_t == 2:
                            projectiles.append((1, 60, 0))
                            self.reload = 20
                        if self.reload_t == 2:
                            self.reload_t = 0
                    # enemy type 3
                    elif self.type == 3:
                        if self.reload_t in [1, 3, 5]:
                            projectiles.append((1, -85, -25))
                            self.reload = 5
                        if self.reload_t in [2, 4, 6]:
                            projectiles.append((1, 85, -25))
                            self.reload = 5
                        if self.reload_t == 7:
                            projectiles.append((2, 0, 75))
                            self.reload = 25
                        if self.reload_t == 7:
                            self.reload_t = 0
                    # enemy type 4
                    elif self.type == 4:
                        if self.reload_t == 1:
                            projectiles.append((0, 0, 0))
                            self.reload = 60
                        if self.reload_t == 1:
                            self.reload_t = 0
                    # enemy type 5
                    elif self.type == 5:
                        if self.reload_t == 1:
                            projectiles.append((1, 0, 0))
                            self.reload = 30
                        if self.reload_t == 1:
                            self.reload_t = 0
                    # enemy type 6
                    elif self.type == 6:
                        if self.reload_t == 1:
                            projectiles.append((2, 0, 140))
                            self.reload = 30
                        if self.reload_t == 1:
                            self.reload_t = 0
                    # enemy type 7
                    elif self.type == 7:
                        if self.reload_t == 1:
                            projectiles.append((0, 0, 0))
                            self.reload = 120
                        if self.reload_t == 1:
                            self.reload_t = 0
                    # enemy type 8
                    elif self.type == 8:
                        if self.data == 0:
                            if self.reload_t == 1:
                                projectiles.append((2, -45, 20))
                                self.reload = 15
                            if self.reload_t == 2:
                                projectiles.append((2, 45, 20))
                                self.reload = 15
                        elif m.fmod(self.data, 5) == 0:
                            if self.reload_t == 1:
                                if len(enemies) < 35:
                                    projectiles.append((0, 0, 0))
                                self.reload = 120
                        else:
                            if self.reload_t == 1:
                                projectiles.append((1, -45, 20))
                                self.reload = 30
                            if self.reload_t == 2:
                                projectiles.append((1, 45, 20))
                                self.reload = 30
                        if self.reload_t == 2:
                            self.reload_t = 0
                    # recoil
                    if self.type != 8:
                        for projectile in projectiles:
                            self.vx -= 7.5 * self.speed * m.cos(m.radians(self.dir))
                            self.vy -= 7.5 * self.speed * m.sin(m.radians(self.dir))
                            if projectile[0] == 2:
                                self.vx -= 7.5 * self.speed * m.cos(m.radians(self.dir))
                                self.vy -= 7.5 * self.speed * m.sin(m.radians(self.dir))
                return damages_this, projectiles
            else:
                self.reload -= 1
                return damages_this, []
        else:
            # death animation
            self.delete += 1
            if self.delete > 3:
                return 1
            return 0

    def render(self, cam_xy: f.position) -> f.rendering:
        if self.delete > 0:
            # death animation
            del_p = (self.delete - 1) / 2
            image_rot = pg.Surface((self.size * 4, self.size * 4)).convert_alpha()
            color = (255, int(255 * (1 - del_p)), int(255 * (1 - del_p)))
            pg.draw.circle(image_rot, color, (self.size * 2, self.size * 2), self.size * 1.5 * (0.5 + (0.5 * del_p)))
            pg.draw.circle(image_rot, (255, 255, 255), (self.size * 2, self.size * 2), self.size * 1.5 * 0.5 * (0.5 + (0.5 * del_p)))
        else:
            # rotates enemy based on dir
            image_rot = pg.transform.rotate(self.image, self.m_dir - 90)
        # offsets image so it's centered
        enemy_ch_x = -image_rot.get_width() / 2
        enemy_ch_y = -image_rot.get_height() / 2
        return image_rot, (enemy_ch_x + self.x - cam_xy[0], enemy_ch_y + self.y - cam_xy[1])

    def damage(self, hp: f.number, x: f.coord, y: f.coord):
        # damages itself
        self.hp -= m.ceil(hp * 2) / 2
        if self.hp < 0:
            self.hp = 0
            self.delete = 1
        # bounces off damager
        bounce_dir = f.point_towards(x, y, self.x, self.y)
        self.vx += 3.75 * m.cos(m.radians(bounce_dir))
        self.vy += 3.75 * m.sin(m.radians(bounce_dir))


class Wave:
    from collections.abc import Sequence

    def __init__(self, enemy_gen: Sequence[tuple[int, int, tuple[int, int]]]):
        # saves enemy generation
        self.enemy_gen = enemy_gen

    def gen_queue(self):
        # creates wave_queue list
        wave_queue = list()
        for i in range(len(self.enemy_gen)):
            # is possible to generate
            if randint(1, self.enemy_gen[i][1]) == 1:
                # generate a random number of enemies
                for e in range(randint(self.enemy_gen[i][2][0], self.enemy_gen[i][2][1])):
                    wave_queue.append(self.enemy_gen[i][0])
        return wave_queue
