from json import loads
from math import cos, sin, degrees, radians

from brawlers import *
from commands import *

FIND_FONT = pygame.font.Font('./data/mainFont.ttf', 50)
COLOR_DEFAULT = pygame.Color(102, 102, 190)
MAIN_FONT = pygame.font.Font('./data/mainFont.ttf', 36)
ev = None

bs = {'Shelly': 1, 'Colt': 2, 'Bull': 2}


class Button:
    def __init__(self, x, y, w, h, text='', color=COLOR_DEFAULT, r=0,
                 text_color=pygame.Color("Black"), bold=False,
                 sound='data/tones/menu_click_08.mp3'):
        self.color = color
        self.og_col = color
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.text = text
        self.radius = r
        self.textColor = text_color
        self.bold = bold
        self.sound = pygame.mixer.Sound(sound)

    def draw(self, win, outline=None):
        # Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline,
                             (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 3,
                             border_radius=self.radius)
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0,
                         border_radius=self.radius)

        if self.text != '':
            font = MAIN_FONT
            text = font.render(self.text, self.bold, self.textColor)
            win.blit(text, (
                self.x + (self.width / 2 - text.get_width() / 2),
                self.y + (self.height / 2 - text.get_height() / 2)))

    def is_over(self, pos):
        # Pos is the mouse position or a tuple of (x,y) coordinates
        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.height:
                self.color = (255, 245, 238)
            else:
                self.color = self.og_col
        else:
            self.color = self.og_col
        for event in ev:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.x < pos[0] < self.x + self.width:
                    if self.y < pos[1] < self.y + self.height:
                        self.sound.play()
                        return True


def draw_outline(x, y, string, win, font):
    def draw_text(x_, y_, s, col, window, bold=True):
        text = font.render(s, bold, col)
        window.blit(text, (x_, y_))

    r = 4
    draw_text(x - 1, y - r + 2, string, 'black', win)
    draw_text(x + 1, y - r + 2, string, 'black', win)
    draw_text(x + 1, y + r, string, 'black', win)
    draw_text(x - 1, y + r, string, 'black', win)
    draw_text(x, y, string, 'white', win)


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

        pygame.draw.circle(self.screen, pygame.Color("WHITE"),
                           (player.rect.centerx, player.rect.centery),
                           self.cell_size // 3 * 2, width=2)  # player outline

        # draw attack
        if pygame.mouse.get_pressed()[0]:
            # send_attack(sock, round(degrees(player.angle)))
            pygame.draw.line(self.screen, "RED", (player.rect.centerx, player.rect.centery), (
                player.rect.centerx + cos(player.angle) * self.attack_length,
                player.rect.centery + sin(player.angle) * self.attack_length),
                             width=self.attack_width)
        else:
            pygame.draw.line(self.screen, "WHITE", (player.rect.centerx, player.rect.centery), (
                player.rect.centerx + cos(player.angle) * self.attack_length,
                player.rect.centery + sin(player.angle) * self.attack_length),
                             width=self.attack_width)

        # draw controller
        pygame.draw.circle(self.screen, "RED", (self.x_shoot, self.y_shoot),
                           self.controller_size, width=1)
        if self.controller_size ** 2 >= (self.x_shoot - x) ** 2 + (self.y_shoot - y) ** 2:
            pygame.draw.circle(self.screen, "RED", (x, y), 30)
        else:
            pygame.draw.circle(self.screen, "RED",
                               (self.x_shoot + cos(player.angle) * self.controller_size,
                                self.y_shoot + sin(player.angle) * self.controller_size), 30)

    def shoot(self, x, y, player, sock):
        player.update_angle(self.x_shoot, self.y_shoot, x, y)  # update angle
        send_attack(sock, round(degrees(player.angle)))


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

    def get_end_game(self):
        message = self.get_message()
        if not message:
            return ''
        if message.startswith(CMD_GAME_game_ends):
            place = int(message[len(CMD_GAME_game_ends):])
            return place
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
FPS = 30


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

    player = BRAWLERS[all_players_data[login][0]](*all_players_data[login][1],
                                                  all_players_data[login][2])

    # shift objects
    player.rect.x, player.rect.y = all_players_data[login][1]
    x_shift = max(min(player.rect.x - width // 2, field.width * field.cell_size - width), 0)
    y_shift = max(min(player.rect.y - height // 2, field.height * field.cell_size - height), 0)
    player.rect.x -= x_shift
    player.rect.y -= y_shift

    bullet_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    player_group.add(player)

    brawlers_from_nick = {}
    brawlers_from_nick[login] = player
    for nick in all_players_data:
        if nick != login:
            enemy = BRAWLERS[all_players_data[nick][0]](*all_players_data[nick][1],
                                                        all_players_data[nick][2])
            enemy.rect.x -= x_shift
            enemy.rect.y -= y_shift
            player_group.add(enemy)
            brawlers_from_nick[nick] = enemy
    hud = CrossHair(screen, attack_length=100, attack_width=30, player_size=cell_size)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, sock, None, screen
            elif event.type == pygame.MOUSEBUTTONUP:
                hud.shoot(*pygame.mouse.get_pos(), player, sock)

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
                    elif to_change == 'attack':
                        print(1)
                        brawlers_from_nick[nick].attack(changes[nick][to_change], bullet_group)
                    elif to_change == 'died':
                        if nick == login:
                            running = False
                            break

        # shift remaking
        if remake_shift:
            new_x_shift = max(
                min(player.rect.x + x_shift - width // 2, field.width * field.cell_size - width), 0)
            new_y_shift = max(
                min(player.rect.y + y_shift - height // 2, field.height * field.cell_size - height),
                0)
            if new_x_shift != x_shift or new_y_shift != y_shift:
                print(new_x_shift, x_shift)
                for nick in brawlers_from_nick.keys():
                    brawlers_from_nick[nick].rect.x -= new_x_shift - x_shift
                    brawlers_from_nick[nick].rect.y -= new_y_shift - y_shift
                x_shift = new_x_shift
                y_shift = new_y_shift

        # draw objects
        field.draw_tiles(x_shift=x_shift, y_shift=y_shift, screen=screen)
        # draw controller and send attack if pressed
        hud.draw(*pygame.mouse.get_pos(), player, sock)
        bullet_group.update()
        bullet_group.draw(screen)
        player_group.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    msc.setblocking(True)
    place = msc.get_end_game()
    return True, sock, all_players_data[login][0], screen, place


def search_window(chosen_brawler, sock, screen):
    chosen_brawler_id = bs[chosen_brawler.title()]
    sock.sendall((CMD_FIND_MATCH + '0' + str(chosen_brawler_id // 10) + str(
        chosen_brawler_id % 10) + Delimiter).encode())
    running = True
    bg = pygame.sprite.Group()
    fg = pygame.sprite.Group()
    img = pygame.sprite.Sprite()
    img.image = load_image("load_in_game.png")
    img.rect = img.image.get_rect()
    img.rect.x, img.rect.y = 650, 250
    background = pygame.sprite.Sprite()
    background.image = load_image("menu.jpg")
    background.rect = background.image.get_rect(center=(width // 2, height // 2))
    bg.add(background)
    fg.add(img)
    radius = (180, 130)
    xd = width // 2
    yd = height // 2
    angle = 0
    _fps = 60
    clock = pygame.time.Clock()
    players = ''
    message = ''
    sock.setblocking(False)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if players and players.split('/')[0] == players.split('/')[1]:
            if message:
                return True, message
            return True, ''
        try:
            message += sock.recv(16).decode()
        except BlockingIOError:
            pass
        if Delimiter in message:
            players = message.split(Delimiter)[0]
            message = Delimiter.join(message.split(Delimiter)[1:])
            players = players[len(CMD_PLAYERS_IN_ROOM):]

        screen.fill((30, 30, 30))
        bg.draw(screen)
        angle -= 2
        points = [(xd + cos(radians(angle + i * 30)) * (radius[i % 2] + 16),
                   yd - sin(radians(angle + i * 30)) * (radius[i % 2] + 16)) for i in range(12)]
        pygame.draw.polygon(screen, color='black', points=points)
        points = [(xd + cos(radians(angle + i * 30)) * radius[i % 2],
                   yd - sin(radians(angle + i * 30)) * radius[i % 2])
                  for i in range(12)]
        pygame.draw.polygon(screen, color=(251, 196, 8), points=points)
        fg.draw(screen)
        draw_outline(470, 20, "SEARCHING FOR PLAYERS", screen, FIND_FONT)
        draw_outline(520, 90, f"PLAYERS FOUND {players}", screen, FIND_FONT)
        pygame.display.flip()
        clock.tick(_fps)
    return False, ''


def end(sock, brawler_name, place, screen):
    running = True
    global ev
    clock = pygame.time.Clock()
    bg_sprites = pygame.sprite.Group()
    background = pygame.sprite.Sprite()
    background.image = load_image("menu.jpg")
    background.rect = background.image.get_rect(center=(width // 2, height // 2))
    back_button = Button(20, 630, 300, 64, text=f'menu', r=20)
    bg_sprites.add(background)
    fps = 30
    select_button = Button(1080, 630, 400, 64, text='play again', r=20,
                           sound='data/tones/select_brawler_01.mp3')
    brawler = pygame.sprite.Sprite()
    brawler.image = pygame.transform.scale(
        load_image(f"brawlers/inMenu/{brawler_name.lower()}.png"), (450, 500))
    brawler.rect = brawler.image.get_rect()
    brawler.rect.x, brawler.rect.y = 500, 100
    fg = pygame.sprite.Group()
    extra_message = ''
    fg.add(brawler)
    while running:
        ev = pygame.event.get()
        for event in ev:
            if event.type == pygame.QUIT:
                quit()
        screen.fill((30, 30, 30))
        bg_sprites.draw(screen)
        back_button.draw(screen, outline=pygame.Color("BLACK"))
        select_button.draw(screen, outline=pygame.Color("BLACK"))
        fg.draw(screen)
        if back_button.is_over(pygame.mouse.get_pos()):
            res = False
            running = False
        if select_button.is_over(pygame.mouse.get_pos()):
            res = True
            running = False
        pygame.display.flip()
        clock.tick(fps)
    if res:
        res, extra_message = search_window(brawler_name, sock, screen)
    return res, sock, extra_message


if __name__ == '__main__':
    size = (1500, 700)
    screen = pygame.display.set_mode(size)
    end('', 'Shelly', screen=screen)
