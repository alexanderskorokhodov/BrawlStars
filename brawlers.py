import os
import sys
from math import pi, acos, sqrt

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
        self.image = pygame.transform.scale(load_image(f"brawlers/inGame/{name}.png"), (cell_size, cell_size))
        self.rect = self.image.get_rect()
        self.name = name
        self.rect.x, self.rect.y = x_, y_
        self.angle = 0
        self.is_shoot = False
        self.is_super = False
        self.max_health = health + (level - 1) * (health // 20)
        self.current_health = self.max_health

    def update(self, x_shoot: int, y_shoot: int, x: int, y: int, mouse_buttons: list) -> tuple:
        self.update_angle(x_shoot, y_shoot, x, y)
        _x = 0
        _y = 0
        if pygame.key.get_pressed()[pygame.K_d]:
            _x += 1
        if pygame.key.get_pressed()[pygame.K_a]:
            _x -= 1
        if pygame.key.get_pressed()[pygame.K_w]:
            _y -= 1
        if pygame.key.get_pressed()[pygame.K_s]:
            _y += 1
        if mouse_buttons[0]:
            self.is_shoot = True
        else:
            self.is_shoot = False
        return _x, _y

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


class Bull(Brawler):
    def __init__(self, x, y, level):
        super().__init__(x, y, 'Bull', 5000, level)
