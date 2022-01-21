from json import loads
from math import cos, sin, degrees

from brawlers import *
from commands import *


class CrossHair:

    def __init__(self, screen, attack_length, attack_width, player_size):
        self.screen = screen
        self.x_shoot, self.y_shoot = width - 150, height - 150
        self.attack_length = attack_length
        self.attack_width = attack_width
        self.cell_size = player_size
        self.controller_size = 50

    def draw(self, x, y, player, sock):
        player.update_angle(self.x_shoot, self.y_shoot, x, y)  # update angle

        pygame.draw.circle(self.screen, pygame.Color("WHITE"), (player.rect.centerx, player.rect.centery),
                           self.cell_size, width=2)  # player outline

        # draw attack
        if pygame.mouse.get_pressed()[0]:
            send_attack(sock, round(degrees(player.angle)))
            pygame.draw.line(self.screen, "RED", (player.rect.centerx, player.rect.centery), (
                player.rect.centerx + cos(player.angle) * self.attack_length,
                player.rect.centery + sin(player.angle) * self.attack_length), width=self.attack_width)
        else:
            pygame.draw.line(self.screen, "WHITE", (player.rect.centerx, player.rect.centery), (
                player.rect.centerx + cos(player.angle) * self.attack_length,
                player.rect.centery + sin(player.angle) * self.attack_length), width=self.attack_width)

        # draw controller
        pygame.draw.circle(self.screen, "RED", (self.x_shoot, self.y_shoot),
                           self.controller_size, width=1)
        if self.controller_size ** 2 >= (self.x_shoot - x) ** 2 + (self.y_shoot - y) ** 2:
            pygame.draw.circle(self.screen, "RED", (x, y), 30)
        else:
            pygame.draw.circle(self.screen, "RED",
                               (self.x_shoot + cos(player.angle) * self.controller_size,
                                self.y_shoot + sin(player.angle) * self.controller_size), 30)


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
            try:
                message = self.socket.recv(64).decode()
                if message:
                    self.extra_text += message
                    while Delimiter not in self.extra_text:
                        self.extra_text += self.socket.recv(64).decode()
                    command = self.extra_text.split(Delimiter)[0]
                    self.extra_text = self.extra_text.split(Delimiter)[1:]
                    for i in range(len(self.extra_text)):
                        if i != len(self.extra_text) - 1:
                            self.commands.append(self.extra_text[i])
                    if len(self.extra_text):
                        self.extra_text = self.extra_text[-1]
                    return command
                else:
                    return ''
            except BlockingIOError:
                return ''
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

    def get_brawlers_start_info(self):
        message = self.get_message()
        if message.startswith(CMD_GAME_players_brawlers_info):
            info = loads(message[len(CMD_GAME_players_brawlers_info):])
            return info
        else:
            raise Exception(f'другая команда в очереди, напиши Сане ({message})')

    def get_brawlers_changes(self):
        message = self.get_message()
        if not message:
            return ''
        if message.startswith(CMD_GAME_changes):
            info = loads(message[len(CMD_GAME_changes):])
            return info
        else:
            print(message)
            raise Exception(f'другая команда в очереди, напиши Сане ({message})')


class Map(pygame.sprite.Sprite):
    def __init__(self, map_name):
        super().__init__()
        self.field = load_map(map_name)
        self.width = len(self.field[0])
        self.height = len(self.field)
        self.cell_size = cell_size

    def draw_tiles(self, x_shift, y_shift, screen):
        tiles_group = pygame.sprite.Group()
        for i in range(self.height):
            for j in range(self.width):
                tile = pygame.sprite.Sprite()
                tile.image = pygame.transform.scale(tile_images[tile_decode[self.field[i][j]]],
                                                    (self.cell_size, self.cell_size))
                tile.rect = tile.image.get_rect()
                tile.rect.x, tile.rect.y = j * self.cell_size - x_shift, i * self.cell_size - y_shift
                tiles_group.add(tile)
        tiles_group.draw(screen)

    def destroy_tile(self, x, y):
        self.field[x][y] = '.'


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


def load_map(map_name):
    filename = "data/maps/" + map_name
    with open(filename, 'r') as mapFile:
        _map = [i.strip() for i in mapFile]
    return _map


def terminate():
    return True  # fix


def send_attack(sock, angle):
    sock.sendall((CMD_GAME_attack + str(angle) + Delimiter).encode())


def send_move(sock):
    x = 0
    y = 0
    if pygame.key.get_pressed()[pygame.K_d]:
        x += 1
    if pygame.key.get_pressed()[pygame.K_a]:
        x -= 1
    if pygame.key.get_pressed()[pygame.K_w]:
        y -= 1
    if pygame.key.get_pressed()[pygame.K_s]:
        y += 1
    if x == 0 and y == 0:
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
FPS = 60


def main(sock, extra_message, login):
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(size)
    running = True

    # get data
    msc = MessageCatcherSender(sock, extra_message)
    field = Map(msc.get_map_name())
    all_players_data = msc.get_brawlers_start_info()
    msc.setblocking(False)

    print(all_players_data)

    player = BRAWLERS[all_players_data[login][0]](*all_players_data[login][1], all_players_data[login][2])

    # shift objects
    player.rect.x, player.rect.y = all_players_data[login][1]
    x_shift = max(min(player.rect.x - width // 2, field.width * field.cell_size - width), 0)
    y_shift = max(min(player.rect.y - height // 2, field.height * field.cell_size - height), 0)
    player.rect.x -= x_shift
    player.rect.y -= y_shift

    player_group = pygame.sprite.Group()
    player_group.add(player)
    brawlers_from_nick = {}
    brawlers_from_nick[login] = player
    for nick in all_players_data:
        if nick != login:
            enemy = BRAWLERS[all_players_data[nick][0]](*all_players_data[nick][1], all_players_data[nick][2])
            enemy.rect.x -= x_shift
            enemy.rect.y -= y_shift
            player_group.add(enemy)
            brawlers_from_nick[nick] = enemy
    hud = CrossHair(screen, attack_length=100, attack_width=30, player_size=cell_size)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return terminate()

        screen.fill((0, 0, 0))

        # send shift
        send_move(sock)

        # get changes
        changes = msc.get_brawlers_changes()
        remake_shift = False
        if changes:
            print(changes)
            if login in changes:
                if 'move' in changes[login]:
                    remake_shift = True
            for nick in changes.keys():
                for to_change in changes[nick].keys():
                    if to_change == 'move':
                        brawlers_from_nick[nick].move(changes[nick][to_change])

        # shift remaking
        if remake_shift:
            new_x_shift = max(min(player.rect.x + x_shift - width // 2, field.width * field.cell_size - width), 0)
            new_y_shift = max(min(player.rect.y + y_shift - height // 2, field.height * field.cell_size - height), 0)
            if new_x_shift != x_shift or new_y_shift != y_shift:
                print(new_x_shift, x_shift)
                for nick in brawlers_from_nick.keys():
                    brawlers_from_nick[nick].rect.x -= new_x_shift - x_shift
                    brawlers_from_nick[nick].rect.y -= new_y_shift - y_shift
                x_shift = new_x_shift
                y_shift = new_y_shift

        # draw objects
        field.draw_tiles(x_shift=x_shift, y_shift=y_shift, screen=screen)
        player_group.draw(screen)

        # draw controller and send attack if pressed
        hud.draw(*pygame.mouse.get_pos(), player, sock)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
