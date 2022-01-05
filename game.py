from math import cos, sin

import pygame.sprite

from brawlers import *

ev: pygame.event
size = width, height = 1500, 700
tile_images = {
    'wall': 'maps/tiles/wall.png',
    'ground': 'maps/tiles/ground.png',
    'skeleton': 'maps/tiles/skeleton.png',
    'bushes': 'maps/tiles/bushes.png',
    'water': 'maps/tiles/river.png',
    'chest': 'maps/tiles/chest.png'
}
tile_decode = {'X': 'bushes', '.': 'ground', '#': 'wall', 'S': 'skeleton', 'P': 'ground', 'C': 'chest', '-': 'water'}
BRAWLERS = {'shelly': Shelly}
FPS = 50


def terminate():
    pygame.quit()
    sys.exit()


def get_brawler():
    return 'shelly'  # fix


def get_cords():
    return 100, 100  # fix


def load_map(map_name):
    filename = "data/maps/" + map_name + '.txt'
    with open(filename, 'r') as mapFile:
        _map = [i.strip() for i in mapFile]
    return _map


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


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self, top_left_tile: pygame.sprite.Sprite, bottom_right_tile: pygame.sprite.Sprite):
        self.dx = width // 2
        self.dy = height // 2
        self.tlt = top_left_tile
        self.brt = bottom_right_tile

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj, _x, _y):
        obj.rect.x -= _x
        obj.rect.y -= _y

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


class Map(pygame.sprite.Sprite):
    def __init__(self, map_name):
        super().__init__()
        self.field = load_map(map_name)
        self.width = len(self.field[0])
        self.height = len(self.field)
        self.cell_size = 50

    def make_tiles_group(self):
        tiles_group = pygame.sprite.Group()
        for i in range(self.height):
            for j in range(self.width):
                tile = pygame.sprite.Sprite()
                tile.image = pygame.transform.scale(load_image(tile_images[tile_decode[self.field[i][j]]]),
                                                    (self.cell_size, self.cell_size))
                tile.rect = tile.image.get_rect()
                tile.rect.x, tile.rect.y = j * self.cell_size, i * self.cell_size
                tiles_group.add(tile)
                if j == self.width - 1 and i == self.height - 1:
                    bottom_right_tile = tile
                if i == 0 == j:
                    top_left_tile = tile
        return tiles_group, top_left_tile, bottom_right_tile


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, tiles_group, all_sprites, tile_height):
        super().__init__(tiles_group, all_sprites)
        self.image = load_image(tile_images[tile_type])
        self.rect = self.image.get_rect().move(*pos_x, tile_height * pos_y)


def main():
    global ev
    pygame.init()
    x_shoot, y_shoot = width - 150, height - 150
    screen = pygame.display.set_mode(size)
    field = Map('RockWallBrawl')
    tiles_group, top_left_tile, bottom_right_tile = field.make_tiles_group()
    brawler_name = get_brawler()
    cords = get_cords()
    clock = pygame.time.Clock()
    player = BRAWLERS[brawler_name](*cords)
    player_group = pygame.sprite.Group()
    player_group.add(player)
    camera = Camera(top_left_tile, bottom_right_tile)
    running = True
    while running:
        ev = pygame.event.get()
        screen.fill((0, 0, 0))
        for event in ev:
            if event.type == pygame.QUIT:
                terminate()
        mouse_buttons = pygame.mouse.get_pressed()
        tiles_group.draw(screen)
        x, y = pygame.mouse.get_pos()
        _x, _y = player.update(x_shoot, y_shoot, x, y, mouse_buttons, velocity=field.cell_size // 10)
        pygame.draw.line(screen,
                         pygame.Color("RED") if player.is_shoot else pygame.Color("WHITE"),
                         (player.rect.x + 25, player.rect.y + 25),
                         (player.rect.x + cos(player.angle) * 100 + 25, player.rect.y + sin(player.angle) * 100 + 25),
                         width=10)
        if (_x > 0 and player.rect.x + _x >= width // 2 and
            bottom_right_tile.rect.x + bottom_right_tile.rect.width >= width) or (
                _x < 0 and player.rect.x + _x <= width // 2 and top_left_tile.rect.x <= 0):
            for sprite in tiles_group:
                camera.apply(sprite, _x, 0)
        elif 0 <= player.rect.x + _x <= width - player.rect.width:
            player.rect.move_ip(_x, 0)
        if (_y > 0 and player.rect.y + _y >= height // 2 and
            bottom_right_tile.rect.y + bottom_right_tile.rect.height >= height) or (
                _y < 0 and player.rect.y + _y <= height // 2 and top_left_tile.rect.y <= 0):
            for sprite in tiles_group:
                camera.apply(sprite, 0, _y)
        elif 0 <= player.rect.y + _y <= height - player.rect.height:
            player.rect.move_ip(0, _y)
        player_group.draw(screen)
        print(player.rect.x, player.rect.y)
        pygame.draw.circle(screen, pygame.Color("RED"), (x_shoot, y_shoot), 50, width=1)
        pygame.draw.circle(screen, pygame.Color("WHITE"), (player.rect.x + 25, player.rect.y + 25), 30, width=2)
        if 2500 >= (x_shoot - x) ** 2 + (y_shoot - y) ** 2:
            pygame.draw.circle(screen, pygame.Color("RED"), (x, y), 30)
        else:
            pygame.draw.circle(screen, pygame.Color("RED"), (
                x_shoot + cos(player.angle) * 50,
                y_shoot + sin(player.angle) * 50), 30)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
