import os
import sys
from math import pi, acos, sqrt, cos, sin, radians

import pygame

cell_size = 50


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


class Brawler(pygame.sprite.Sprite):
    def __init__(self, x_, y_, name, health, level):
        super().__init__()
        self.image = pygame.transform.scale(load_image(f"brawlers/inGame/{name}.png"),
                                            (cell_size, cell_size))
        self.rect = self.image.get_rect()
        self.name = name
        self.rect.x, self.rect.y = x_, y_
        self.angle = 0
        self.is_shoot = False
        self.is_super = False
        self.max_health = health + (level - 1) * (health // 20)
        self.current_health = self.max_health

    def move(self, cords):
        self.rect.x += cords[0]
        self.rect.y += cords[1]
        print(self.rect.center)

    def update_angle(self, x_shoot, y_shoot, x, y):
        hip = sqrt((x_shoot - x) ** 2 + (y_shoot - y) ** 2)
        if hip:
            _cos = (x - x_shoot) / hip
            _sin = (y - y_shoot) / hip
            self.angle = acos(_cos) if _sin > 0 else 2 * pi - acos(_cos)
        else:
            self.angle = 0


class Shelly(Brawler):
    def __init__(self, x, y, level):
        super().__init__(x, y, 'Shelly', 3600, level)


class Colt(Brawler):
    def __init__(self, x, y, level):
        super().__init__(x, y, 'Colt', 2800, level)

    def attack(self, angle, bullet_group, tickrate=30):
        Bullet(self.rect.centerx, self.rect.centery, cell_size // 4, angle, 500,
               250, 400, tickrate, bullet_group)


class Bull(Brawler):
    def __init__(self, x, y, level):
        super().__init__(x, y, 'Bull', 5000, level)


class Bullet(pygame.sprite.Sprite):
    # parent class of all bullets
    def __init__(self, x, y, radius, angle, bullet_speed, max_range, damage, tickrate, *group):
        super().__init__(*group)
        self.image = load_image(f"brawlers/inGame/ColtAttack.png")
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.radius = radius
        self.angle = angle
        self.speed = bullet_speed / tickrate
        self.x_step = self.speed * cos(radians(self.angle))
        self.y_step = self.speed * sin(radians(self.angle))
        self.max_range = max_range
        self.damage = damage
        self.current_range = 0

    def update(self, *args, **kwargs) -> None:
        self.rect.x += self.x_step
        self.rect.y += self.y_step
        self.current_range += (self.x_step ** 2 + self.y_step ** 2) ** (1 / 2)
        if self.current_range >= self.max_range:
            self.kill()
