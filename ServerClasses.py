from pygame import Rect
from pygame.sprite import Sprite
from random import randint
from math import sin, cos, radians
import sqlite3


cell_size = 100


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
    attributes = ['id', 'health', 'speed', 'attack_range', 'attack_reload_time', 'attack_amount_of_bullets', 'attack_damage']

    def __init__(self, x, y, login, *group):
        super().__init__(*group)
        self.player_name = login
        self.rect = Rect(x, y, cell_size, cell_size)
        self.class_name = self.__class__.__name__.lower()
        con = sqlite3.connect("BrawlStars.db")
        cur = con.cursor()
        for attribute in self.attributes:
            # print(f'self.{attribute} = cur.execute(f"SELECT {attribute} FROM brawlers WHERE name = \'{self.class_name}\'").fetchone()[0]')
            exec(f'self.{attribute} = cur.execute("SELECT {attribute} FROM brawlers WHERE name = \'{self.class_name}\'").fetchone()[0]')
        self.power = cur.execute(f"SELECT power FROM players_brawlers WHERE login = '{self.player_name}' AND brawler_id = {self.id}").fetchone()[0]
        con.close()

    def move(self, type_of_move):
        # type_of_move - число от 0 до 7, обозначает направление как в компасе начиная с севера по часовой
        # то есть 0 - вверх, 1 - вверх и вправо, 2 - вправо и тд
        x, y = 0, 0
        if type_of_move == 0:
            y = -1 * self.speed
        elif type_of_move == 1:
            x = round(self.speed / 2 ** (1 / 2))
            y = -1 * round(self.speed / 2 ** (1 / 2))
        elif type_of_move == 2:
            x = self.speed
        elif type_of_move == 3:
            x = round(self.speed / 2 ** (1 / 2))
            y = round(self.speed / 2 ** (1 / 2))
        elif type_of_move == 4:
            y = self.speed
        elif type_of_move == 5:
            x = -1 * round(self.speed / 2 ** (1 / 2))
            y = round(self.speed / 2 ** (1 / 2))
        elif type_of_move == 6:
            x = -1 * self.speed
        elif type_of_move == 7:
            x = -1 * round(self.speed / 2 ** (1 / 2))
            y = -1 * round(self.speed / 2 ** (1 / 2))
        self.rect.move(x, y)


class Shelly(Brawler):

    def __init__(self, x, y, login, *group):
        super().__init__(x, y, login, *group)


if __name__ == '__main__':
    s = Shelly(1, 2)
    print(s.health, s.speed, s.attack_damage)