import os.path
import sys
from json import loads

import pygame as pg
import pygame.transform

from commands import *  # commands


def get_player_info(sock):
    message = sock.recv(len(CMD_PLAYER_INFO_IN_MENU)).decode()
    if message == CMD_PLAYER_INFO_IN_MENU:
        data = sock.recv(32).decode()
        while data[-1] != Delimiter:
            data += sock.recv(32).decode()
        info = loads(data[:-1])
        return info


pg.init()
COLOR_INACTIVE = pg.Color('lightskyblue3')
COLOR_ACTIVE = pg.Color('dodgerblue2')
COLOR_DEFAULT = pg.Color(102, 102, 190)
FONT = pg.font.SysFont('arial', 36)
size = width, height = 1500, 700
clock = pg.time.Clock()
fps = 60
screen = pg.display.set_mode(size)
ev: pg.event


class Button:
    def __init__(self, x, y, w, h, text='', color=COLOR_DEFAULT, r=0):
        self.color = color
        self.og_col = color
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.text = text
        self.radius = r

    def draw(self, win, outline=None):
        # Call this method to draw the button on the screen
        if outline:
            pg.draw.rect(win, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0,
                         border_radius=self.radius)

        pg.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0, border_radius=self.radius)

        if self.text != '':
            font = FONT
            text = font.render(self.text, True, (0, 0, 0))
            win.blit(text, (
                self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def is_over(self, pos):
        # Pos is the mouse position or a tuple of (x,y) coordinates
        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.height:
                self.color = (128, 128, 128)
            else:
                self.color = self.og_col
        else:
            self.color = self.og_col
        global ev
        for event in ev:
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.x < pos[0] < self.x + self.width:
                    if self.y < pos[1] < self.y + self.height:
                        return True


class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif len(self.text) < 12:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        pass

    def draw(self, scr):
        # Blit the text.
        scr.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pg.draw.rect(scr, self.color, self.rect, 2)


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pg.image.load(fullname)
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def server_error_window():
    running = True
    try_button = Button(600, 300, 300, 32, text='Try again', color=COLOR_DEFAULT, r=16)
    all_sprites = pg.sprite.Group()
    background = pg.sprite.Sprite()
    background.image = load_image(f"serverError1.jpg")
    background.rect = background.image.get_rect(center=(width // 2, height // 2))
    all_sprites.add(background)
    text_server_error = FONT.render("Error: Cannot connect to server", True, (255, 0, 0))
    while running:
        global ev
        ev = pg.event.get()
        for event in ev:
            if event.type == pg.QUIT:
                return False
        screen.fill((30, 30, 30))
        all_sprites.draw(screen)
        try_button.draw(screen)
        screen.blit(text_server_error, (625, 400, 300, 32))
        pg.display.flip()
        if try_button.is_over(pg.mouse.get_pos()):
            running = False
        clock.tick(fps)
    return True


def get_user_data():
    return {'nick': 'sanya', 'login': 'sanya', 'password': 'sanya', 'trophies': 666, 'gems': 1000}


def main(sock):
    running = True
    bg_sprites = pg.sprite.Group()
    background = pg.sprite.Sprite()
    background.image = load_image("menu.jpg")
    background.rect = background.image.get_rect(center=(width // 2, height // 2))
    trophy = pg.sprite.Sprite()
    trophy.image = pygame.transform.scale(load_image("trophy.png", (0, 0, 0)), (64, 64))
    trophy.rect = trophy.image.get_rect()
    trophy.rect.x, trophy.rect.y = 350, 20
    fg_sprites = pg.sprite.Group()
    fg_sprites.add(trophy)
    bg_sprites.add(background)
    user_button = Button(20, 20, 300, 64, text=f'username', r=20)
    trophies_button = Button(350, 20, 200, 64, text=f'', r=20)
    money_button = Button(1000, 20, 200, 64, text=f'', r=20)
    try:
        user_data = get_player_info(sock)
        user_button.text = user_data['nickname']
        trophies_button.text = '    ' + str(user_data['all_cups'])
        money_button.text =  str(user_data['money']) + '$'
    except:
        server_error_window()
    while running:
        global ev
        ev = pg.event.get()
        for event in ev:
            if event.type == pg.QUIT:
                return False
        screen.fill((30, 30, 30))
        bg_sprites.draw(screen)
        user_button.draw(screen, outline=pg.Color("BLACK"))
        trophies_button.draw(screen, outline=pg.Color("BLACK"))
        money_button.draw(screen, outline=pg.Color("BLACK"))
        fg_sprites.draw(screen)
        pg.display.flip()
        clock.tick(fps)


if __name__ == '__main__':
    main(None)
