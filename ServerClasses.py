from pygame import Rect
from pygame.sprite import Sprite
from random import randint
from math import sin, cos, radians
import sqlite3

cell_size = 50


class Block(Sprite):
    # parent class of all blocks
    def __init__(self, x, y, *group):
        super().__init__(*group)
        self.breakable_by_bullet = False
        self.breakable_by_ult = False
        self.player_collision = False
        self.bullet_collision = False
        self.rect = Rect(x, y, cell_size, cell_size)


class Wall(Block):
    # just a wall
    def __init__(self, x, y, *group):
        super().__init__(x, y, *group)
        self.breakable_by_bullet = False
        self.breakable_by_ult = True
        self.player_collision = True
        self.bullet_collision = True


class Bush(Block):
    # куст
    def __init__(self, x, y, *group):
        super().__init__(x, y, *group)
        self.breakable_by_bullet = False
        self.breakable_by_ult = True
        self.player_collision = False
        self.bullet_collision = False


class Skeletons(Block):
    # just skeletons
    def __init__(self, x, y, *group):
        super().__init__(x, y, *group)
        self.breakable_by_bullet = True
        self.breakable_by_ult = True
        self.player_collision = True
        self.bullet_collision = True


class Chest(Block):
    # сундук с банкой
    def __init__(self, x, y, power_crystal_group, *group):
        super().__init__(x, y, *group)
        self.breakable_by_bullet = True
        self.breakable_by_ult = True
        self.player_collision = False
        self.bullet_collision = False
        self.health = 6000
        self.power_crystal_group = power_crystal_group

    def get_damage(self, damage):
        self.health = max(0, self.health - damage)
        if self.health == 0:
            self.spawn_crystal(self.power_crystal_group)

    def spawn_crystal(self, group):
        range_len = randint(0, cell_size)
        angle = radians(randint(0, 359))
        x = round(range_len * cos(angle))
        y = round(range_len * sin(angle))
        PowerCrystal(x, y, group)


class PowerCrystal(Sprite):
    # crystal that power up brawler
    def __init__(self, x, y, *group):
        super().__init__(*group)
        self.size = cell_size
        self.rect = Rect(x - self.size // 2, y - self.size // 2, self.size, self.size)


class Brawler(Sprite):
    # parent class of all brawlers
    attributes = ['id', 'health', 'speed', 'attack_range', 'attack_reload_time',
                  'attack_amount_of_bullets', 'attack_damage', 'attack_speed']

    def __init__(self, x, y, login, bullet_group, *group):
        super().__init__(*group)
        self.bullet_group = bullet_group
        self.player_name = login
        self.rect = Rect(x, y, cell_size, cell_size)
        self.class_name = self.__class__.__name__.lower()
        con = sqlite3.connect("BrawlStars.db")
        cur = con.cursor()
        for attribute in self.attributes:
            # print(f'self.{attribute} = cur.execute(f"SELECT {attribute} FROM brawlers WHERE name = \'{self.class_name}\'").fetchone()[0]')
            exec(
                f'self.{attribute} = cur.execute("SELECT {attribute} FROM brawlers WHERE name = \'{self.class_name}\'").fetchone()[0]')
        self.power = cur.execute(
            f"SELECT power FROM players_brawlers WHERE login = '{self.player_name}' AND brawler_id = {self.id}").fetchone()[
            0]
        self.health += (self.power - 1) * self.health // 20
        self.attack_damage += (self.power - 1) * self.attack_damage // 20
        con.close()

    def from_type_of_move_to_cords(self, type_of_move, tickrate):
        # type_of_move - число от 0 до 7, обозначает направление как в компасе начиная с севера по часовой
        # то есть 0 - вверх, 1 - вверх и вправо, 2 - вправо и тд
        x, y = 0, 0
        if type_of_move == 0:
            y = -1 * self.speed / tickrate
        elif type_of_move == 1:
            x = self.speed / tickrate / 2 ** (1 / 2)
            y = -1 * self.speed / tickrate / 2 ** (1 / 2)
        elif type_of_move == 2:
            x = self.speed / tickrate
        elif type_of_move == 3:
            x = self.speed / tickrate / 2 ** (1 / 2)
            y = self.speed / tickrate / 2 ** (1 / 2)
        elif type_of_move == 4:
            y = self.speed / tickrate
        elif type_of_move == 5:
            x = -1 * self.speed / tickrate / 2 ** (1 / 2)
            y = self.speed / tickrate / 2 ** (1 / 2)
        elif type_of_move == 6:
            x = -1 * self.speed / tickrate
        elif type_of_move == 7:
            x = -1 * self.speed / tickrate / 2 ** (1 / 2)
            y = -1 * self.speed / tickrate / 2 ** (1 / 2)
        return round(x), round(y)

    def move(self, x, y):
        self.rect.x += x
        self.rect.y += y


class Shelly(Brawler):

    def __init__(self, x, y, login, *group, bullet_group=None):
        super().__init__(x, y, login, bullet_group, *group)

    def attack(self, angle, tickrate):
        for i in range(-2, 3,):
            Bullet(self.rect.centerx, self.rect.centery, cell_size // 4, angle + i * 5, self.attack_speed,
                   self.attack_range, self.attack_damage, tickrate, self.bullet_group)


class Colt(Brawler):

    def __init__(self, x, y, login, *group, bullet_group=None):
        super().__init__(x, y, login, bullet_group, *group)

    def attack(self, angle, tickrate):
        Bullet(self.rect.centerx, self.rect.centery, cell_size // 4, angle, self.attack_speed,
               self.attack_range, self.attack_damage, tickrate, self.bullet_group)


class Bull(Brawler):

    def __init__(self, x, y, login, *group, bullet_group=None):
        super().__init__(x, y, login, bullet_group, *group)


class Bullet(Sprite):
    # parent class of all bullets
    def __init__(self, x, y, radius, angle, bullet_speed, max_range, damage, tickrate, *group):
        super().__init__(*group)
        self.rect = Rect(x, y, radius * 2, radius * 2)
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


if __name__ == '__main__':
    s = Shelly(1, 2)
    print(s.health, s.speed, s.attack_damage)
