from math import cos, sin

import pygame.sprite

from brawlers import *
from commands import *
from json import loads


class MessageCatcherSender:

    def __init__(self, sock, extra_message):
        self.socket = sock
        self.commands = []
        self.extra_text = extra_message
        self.setblocking(True)

    def setblocking(self, value):
        self.socket.setblocking(value)

    def send_message(self, message: str):
        self.socket.sendall(message.encode())

    def get_message(self):
        if len(self.commands) == 0:
            while Delimiter not in self.extra_text:
                self.extra_text += self.socket.recv(64).decode()
            print(self.extra_text)
            command = self.extra_text.split(Delimiter)[0]
            self.extra_text = self.extra_text.split(Delimiter)[1:]
            for i in range(len(self.extra_text)):
                if i != len(self.extra_text) - 1:
                    self.commands.append(self.extra_text[i])
            if len(self.extra_text):
                self.extra_text = self.extra_text[-1]
            return command
        else:
            command = self.commands[0]
            self.commands.pop(0)
            return command


    def get_map_name(self):
        message = self.get_message()
        if message.startswith(CMD_GAME_map):
            return message[len(CMD_GAME_map):]
        else:
            raise Exception(f'другая команда в очереди, напиши Сане ({message})')

    def get_brawlers(self):
        message = self.get_message()
        if message.startswith(CMD_GAME_players_brawlers_info):
            info = loads(message[len(CMD_GAME_players_brawlers_info):])
            return info
        else:
            raise Exception(f'другая команда в очереди, напиши Сане ({message})')


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


ev: pygame.event
size = width, height = 1500, 700
tile_images = {
    'wall': load_image('maps/tiles/wall.png'),
    'ground': load_image('maps/tiles/ground.png'),
    'skeleton': load_image('maps/tiles/skeleton.png'),
    'bushes': load_image('maps/tiles/bushes.png'),
    'water': load_image('maps/tiles/river.png'),
    'chest': load_image('maps/tiles/chest.png')
}
tile_decode = {'X': 'bushes',
               '.': 'ground',
               '#': 'wall',
               'S': 'skeleton',
               'P': 'ground',
               'C': 'chest',
               '-': 'water'}
BRAWLERS = {'shelly': Shelly, 'colt': Colt, 'bull': Bull}
FPS = 50


def terminate():
    return True  # fix


def get_map():
    return 'map_name'  # fix


def get_brawler():
    return 'shelly'  # fix


def get_cords():
    return 100, 100  # fix


def send_attack(sock, angle):
    sock.sendall((CMD_GAME_attack + str(angle) + Delimiter).encode())


def send_move(sock, x, y):
    if x and y:
        return
    if x == 0:
        if y == 1:
            type_of_move = 4
        elif y == -1:
            type_of_move = 0
    elif y == 0:
        if x == 1:
            type_of_move = 2
        elif x == -1:
            type_of_move = 6
    else:
        if x == 1 and y == 1:
            type_of_move = 3
        elif x == 1 and y == -1:
            type_of_move = 1
        elif x == -1 and y == 1:
            type_of_move = 5
        elif x == -1 and y == -1:
            type_of_move = 7
    sock.sendall((CMD_GAME_move + str(type_of_move) + Delimiter).encode())


def load_map(map_name):
    filename = "data/maps/" + map_name + '.txt'
    with open(filename, 'r') as mapFile:
        _map = [i.strip() for i in mapFile]
    return _map


class Camera:

    def __init__(self, top_left_tile: pygame.sprite.Sprite, bottom_right_tile: pygame.sprite.Sprite):
        self.dx = width // 2
        self.dy = height // 2
        self.tlt = top_left_tile
        self.brt = bottom_right_tile

    def apply(self, obj, _x, _y):
        obj.rect.x -= _x
        obj.rect.y -= _y

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

    def destroy_tile(self, x, y):
        self.field[x][y] = '.'


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, tiles_group, all_sprites, tile_height):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(*pos_x, tile_height * pos_y)


def main(sock, extra_message):

    s = MessageCatcherSender(sock, extra_message)
    print(s.get_map_name())
    print(s.get_brawlers())

    global ev
    pygame.init()
    x_shoot, y_shoot = width - 150, height - 150
    screen = pygame.display.set_mode(size)
    field = Map(get_map())
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
        for event in ev:
            if event.type == pygame.QUIT:
                return terminate()
        screen.fill((0, 0, 0))
        mouse_buttons = pygame.mouse.get_pressed()
        x, y = pygame.mouse.get_pos()
        # get shift x, y
        _x, _y = player.update(x_shoot, y_shoot, x, y, mouse_buttons)
        # send shift
        _x, _y = send_move(sock, _x, _y)
        # camera and player pos
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
        # draw objects
        tiles_group.draw(screen)
        player_group.draw(screen)
        # draw controller
        if player.is_shoot:
            send_attack(sock, player.angle)
            pygame.draw.line(screen, pygame.Color("RED"), (player.rect.x + 25, player.rect.y + 25),
                             (player.rect.x + cos(player.angle) * 100 + 25,
                              player.rect.y + sin(player.angle) * 100 + 25),
                             width=10)
        else:
            pygame.draw.line(screen, pygame.Color("WHITE"), (player.rect.x + 25, player.rect.y + 25),
                             (player.rect.x + cos(player.angle) * 100 + 25,
                              player.rect.y + sin(player.angle) * 100 + 25), width=10)
        pygame.draw.circle(screen, pygame.Color("RED"), (x_shoot, y_shoot), 50, width=1)
        pygame.draw.circle(screen, pygame.Color("WHITE"), (player.rect.x + 25, player.rect.y + 25), 30, width=2)
        if 2500 >= (x_shoot - x) ** 2 + (y_shoot - y) ** 2:
            pygame.draw.circle(screen, pygame.Color("RED"), (x, y), 30)
        else:
            pygame.draw.circle(screen, pygame.Color("RED"),
                               (x_shoot + cos(player.angle) * 50, y_shoot + sin(player.angle) * 50), 30)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
