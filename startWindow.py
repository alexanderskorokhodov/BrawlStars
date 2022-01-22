import json
import os.path
import random
import socket
import sys

import pygame as pg
from pygame.draw import rect

from commands import *  # commands


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


pg.init()
pg.display.set_caption('Brawl Stars', 'Brawl Stars')
pg.display.set_icon(load_image('icon.png'))
COLOR_INACTIVE = pg.Color('lightskyblue3')
COLOR_ACTIVE = pg.Color('dodgerblue2')
FONT = pg.font.SysFont('arial', 18)
size = width, height = 1500, 700
clock = pg.time.Clock()
fps = 60
screen = pg.display.set_mode(size)
ev: pg.event
input_boxes: list


class Button:
    def __init__(self, x, y, w, h, text='', color=COLOR_ACTIVE, r=0):
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

        pg.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0,
                     border_radius=self.radius)

        if self.text != '':
            font = FONT
            text = font.render(self.text, True, (0, 0, 0))
            win.blit(text, (
                self.x + (self.width / 2 - text.get_width() / 2),
                self.y + (self.height / 2 - text.get_height() / 2)))

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
                if event.key == pg.K_RETURN:
                    return True
                if event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif len(self.text) < 12:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)
        return False

    def update(self):
        pass

    def draw(self, scr):
        # Blit the text.
        scr.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pg.draw.rect(scr, self.color, self.rect, 2)


def get_data():
    data = []
    for i in input_boxes:
        data.append(i.text)
    return data


def write_credentials(login, password):
    credentials = {'login': login, 'password': password}
    with open(file='data/credentials.json', mode='w') as file:
        json.dump(credentials, file)


def check_reg_data():
    data = get_data()
    if not 12 >= len(data[0]) > 0:
        return False, 'Length of login must be between 1 and 12'
    if not 12 >= len(data[1]) > 0:
        return False, 'Length of password must be between 1 and 12'
    if not 12 >= len(data[2]) > 0:
        return False, 'Length of nickname must be between 1 and 12'
    return True, ''


def check_log_data():
    data = get_data()[:-1]
    if not 12 >= len(data[0]) > 0:
        return False, 'Length of login must be between 1 and 12'
    if not 12 >= len(data[1]) > 0:
        return False, 'Length of password must be between 1 and 12'
    return True, ''


def start():
    sock = False
    all_sprites = pg.sprite.Group()
    background = pg.sprite.Sprite()
    screens = os.listdir('./data/loginScreens')
    background.image = pg.transform.scale(load_image(f"loginScreens/{random.choice(screens)}"),
                                          (width, height))
    background.rect = background.image.get_rect(center=(width // 2, height // 2))
    length_of_loading = 100
    rect(screen, "Gray", (100, 600, length_of_loading, 50), width=1, border_radius=25)
    all_sprites.add(background)
    running = True
    velocity = 10
    pg.mixer.music.load('data/tones/now-loading.mp3')
    pg.mixer.music.play()
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        screen.fill((0, 0, 255))
        all_sprites.draw(screen)
        length_of_loading += velocity
        rect(screen, "black", (100, 600, length_of_loading, 50), width=0, border_radius=25)
        pg.display.flip()
        clock.tick(fps)
        if length_of_loading >= width - 200:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            with open('ip.txt') as f:
                ip = f.read()
            if ip:
                server_address = (ip, 10000)
            else:
                server_address = (socket.gethostbyname(socket.gethostname()), 10000)
            print('Подключено к {} порт {}'.format(*server_address))
            sock.connect(server_address)
            running = False
    pg.mixer.music.stop()
    return sock


def server_error_window():
    running = True
    try_button = Button(600, 300, 300, 32, text='Try again', r=16)
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


def login_reg_window(sock):
    global input_boxes

    text_reg = FONT.render("Registration", True, COLOR_INACTIVE)
    text_login = FONT.render("Login:", True, COLOR_INACTIVE)
    text_password = FONT.render("Password:", True, COLOR_INACTIVE)
    text_nick = FONT.render("Nick:", True, COLOR_INACTIVE)

    text_error = FONT.render("", True, (255, 0, 0))
    input_box1 = InputBox(600, 150, 300, 32)
    input_box1.active = True
    input_box1.color = COLOR_ACTIVE
    input_box2 = InputBox(600, 250, 300, 32)
    input_box3 = InputBox(600, 350, 300, 32)
    input_boxes = [input_box1, input_box2, input_box3]
    continue_button = Button(600, 450, 300, 32, text='Continue', r=16)
    reg_button = Button(600, 550, 300, 32, text='Registration', r=16)
    back_button = Button(600, 550, 300, 32, text='Back', r=16)
    done = False

    window = 'LOG'

    while not done:
        global ev
        ev = pg.event.get()
        a = False
        if window == 'LOG':
            for event in ev:
                if event.type == pg.QUIT:
                    done = True
                a = False
                for box in input_boxes[:-1]:
                    b = box.handle_event(event)
                    if b and input_boxes.index(box) == 0:
                        input_boxes[0].active = False
                        input_boxes[1].active = True
                        input_boxes[0].color = COLOR_INACTIVE
                        input_boxes[1].color = COLOR_ACTIVE
                        break
                    elif b and input_boxes.index(box) == 1:
                        a = True
            for box in input_boxes[:-1]:
                box.update()

            screen.fill((30, 30, 30))
            for box in input_boxes[:-1]:
                box.draw(screen)
            continue_button.draw(screen)
            reg_button.draw(screen)
            screen.blit(text_password, (600, 200, 300, 32))
            screen.blit(text_login, (600, 100, 300, 32))
            screen.blit(text_error, (600, 500, 300, 32))

            pg.display.flip()

            if continue_button.is_over(pg.mouse.get_pos()) or a:
                check, mes = check_log_data()
                if check:
                    login, password = get_data()[:-1]
                    text_error = FONT.render("", True, (255, 0, 0))
                    sock.sendall((CMD_TO_LOG_IN + login + Delimiter + password).encode())
                    message = sock.recv(
                        max(len(CMD_RIGHT_PASSWORD), len(CMD_WRONG_PASSWORD))).decode()
                    if message == CMD_RIGHT_PASSWORD:
                        done = True
                        return True, login, password
                    else:
                        a = False
                        text_error = FONT.render('Invalid login or password', True, (255, 0, 0))
                else:
                    text_error = FONT.render(mes, True, (255, 0, 0))
            if reg_button.is_over(pg.mouse.get_pos()):
                window = 'REG'
                text_error = FONT.render("", True, (255, 0, 0))
                input_box1.active = True
                input_box1.color = COLOR_ACTIVE
        else:
            for event in ev:
                if event.type == pg.QUIT:
                    done = True
                a = False
                for box in input_boxes:
                    b = box.handle_event(event)
                    if b and input_boxes.index(box) == 0:
                        input_boxes[0].active = False
                        input_boxes[1].active = True
                        input_boxes[0].color = COLOR_INACTIVE
                        input_boxes[1].color = COLOR_ACTIVE
                        break
                    elif b and input_boxes.index(box) == 1:
                        input_boxes[1].active = False
                        input_boxes[2].active = True
                        input_boxes[1].color = COLOR_INACTIVE
                        input_boxes[2].color = COLOR_ACTIVE
                        break
                    elif b and input_boxes.index(box) == 2:
                        a = True

            for box in input_boxes:
                box.update()

            screen.fill((30, 30, 30))
            for box in input_boxes:
                box.draw(screen)

            continue_button.draw(screen)
            back_button.draw(screen)
            screen.blit(text_password, (600, 200, 300, 32))
            screen.blit(text_login, (600, 100, 300, 32))
            screen.blit(text_error, (600, 500, 300, 32))
            screen.blit(text_reg, (600, 50, 300, 32))
            screen.blit(text_nick, (600, 300, 300, 32))

            pg.display.flip()

            if continue_button.is_over(pg.mouse.get_pos()) or a:
                check, mes = check_reg_data()
                if check:
                    login, password, nick = get_data()
                    text_error = FONT.render("", True, (255, 0, 0))
                    sock.sendall((
                                         CMD_TO_REGISTRATION + login + Delimiter + password + Delimiter + nick).encode())
                    message = sock.recv(
                        max(len(CMD_SUCCESSFUL_REGISTRATION), len(CMD_FAIL_REGISTRATION))).decode()
                    if message == CMD_SUCCESSFUL_REGISTRATION:
                        done = True
                        return True, login, password
                    else:
                        text_error = FONT.render('This login already exists', True, (255, 0, 0))
                else:
                    text_error = FONT.render(mes, True, (255, 0, 0))
                    a = False
            if back_button.is_over(pg.mouse.get_pos()):
                window = 'LOG'
                text_error = FONT.render("", True, (255, 0, 0))
                input_box1.active = True
                input_box1.color = COLOR_ACTIVE
        clock.tick(fps)


def main():
    # start screen
    while 1:
        try:
            sock = start()
            if sock:
                break
            else:
                raise
        except:
            print('Не удалось подключиться к серверу')
            if not server_error_window():
                quit()
    # login screen
    if os.path.exists('data/credentials.json'):
        with open(file='data/credentials.json', mode='r') as file:
            credentials = json.load(file)
        login, password = credentials['login'], credentials['password']
        sock.sendall((CMD_TO_LOG_IN + login + Delimiter + password).encode())
        message = sock.recv(max(len(CMD_RIGHT_PASSWORD), len(CMD_WRONG_PASSWORD))).decode()
        if message == CMD_RIGHT_PASSWORD:
            return True, sock, login, password
    res, login, password = login_reg_window(sock)
    if res:
        write_credentials(login, password)
        return True, sock, login, password
    return False, None


if __name__ == '__main__':
    main()
