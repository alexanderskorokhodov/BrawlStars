import os.path
import socket
import sys

import pygame as pg
from pygame.draw import rect

from commands import *  # commands

pg.init()
COLOR_INACTIVE = pg.Color('lightskyblue3')
COLOR_ACTIVE = pg.Color('dodgerblue2')
FONT = pg.font.SysFont('arial', 18)
size = width, height = 1500, 700
fps = 60
screen = pg.display.set_mode(size)
ev: pg.event
input_boxes: list


class Button:
    def __init__(self, x, y, w, h, text='', color=COLOR_ACTIVE):
        self.color = color
        self.og_col = color
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.text = text

    def draw(self, win, outline=None):
        # Call this method to draw the button on the screen
        if outline:
            pg.draw.rect(win, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)

        pg.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)

        if self.text != '':
            font = FONT
            text = font.render(self.text, 1, (0, 0, 0))
            win.blit(text, (
                self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def is_over(self, pos):
        global STATE
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


def get_data():
    data = []
    for i in input_boxes:
        data.append(i.text)
    return data


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


def main():

    # screensaver
    all_sprites = pg.sprite.Group()
    background = pg.sprite.Sprite()
    background.image = load_image("login1.jpg")
    background.rect = background.image.get_rect(center=(width // 2, height // 2))
    length_of_loading = 100
    loading = rect(screen, "Gray", (100, 600, length_of_loading, 50), width=1, border_radius=25)
    # добавим спрайт в группу
    all_sprites.add(background)
    running = True
    clock = pg.time.Clock()
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        screen.fill((0, 0, 255))
        all_sprites.draw(screen)
        length_of_loading += 10
        loading = rect(screen, "black", (100, 600, length_of_loading, 50), width=0, border_radius=25)
        pg.display.flip()
        clock.tick(fps)
        if length_of_loading == 200:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if length_of_loading == 300:
            server_address = (socket.gethostbyname(socket.gethostname()), 10000)
        if length_of_loading == 400:
            print('Подключено к {} порт {}'.format(*server_address))
        if length_of_loading == 500:
            sock.connect(server_address)
        if length_of_loading >= width - 200:
            running = False

    # login
    global input_boxes

    text_reg = FONT.render("Registration", 1, COLOR_INACTIVE)
    text_login = FONT.render("Login:", 1, COLOR_INACTIVE)
    text_password = FONT.render("Password:", 1, COLOR_INACTIVE)
    text_nick = FONT.render("Nick:", 1, COLOR_INACTIVE)

    text_error = FONT.render("", 1, (255, 0, 0))
    input_box1 = InputBox(600, 150, 300, 32)
    input_box2 = InputBox(600, 250, 300, 32)
    input_box3 = InputBox(600, 350, 300, 32)
    input_boxes = [input_box1, input_box2, input_box3]
    continue_button = Button(600, 450, 300, 32, text='Continue')
    reg_button = Button(600, 550, 300, 32, text='Registration')
    back_button = Button(600, 550, 300, 32, text='Back')
    done = False

    window = 'LOG'

    while not done:
        global ev
        ev = pg.event.get()
        if window == 'LOG':
            for event in ev:
                if event.type == pg.QUIT:
                    done = True
                for box in input_boxes:
                    box.handle_event(event)

            for box in input_boxes:
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

            if continue_button.is_over(pg.mouse.get_pos()):
                check, mes = check_log_data()
                if check:
                    login, password = get_data()[:-1]
                    text_error = FONT.render("", 1, (255, 0, 0))
                    sock.sendall((CMD_TO_LOG_IN + login + Delimiter + password).encode())
                    message = sock.recv(max(len(CMD_RIGHT_PASSWORD), len(CMD_WRONG_PASSWORD))).decode()
                    if message == CMD_RIGHT_PASSWORD:
                        done = True
                    else:
                        text_error = FONT.render('Server Error', 1, (255, 0, 0))
                else:
                    text_error = FONT.render(mes, 1, (255, 0, 0))
            if reg_button.is_over(pg.mouse.get_pos()):
                window = 'REG'
                text_error = FONT.render("", 1, (255, 0, 0))
        else:
            for event in ev:
                if event.type == pg.QUIT:
                    done = True
                for box in input_boxes:
                    box.handle_event(event)

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

            if continue_button.is_over(pg.mouse.get_pos()):
                check, mes = check_reg_data()
                if check:
                    login, password, nick = get_data()
                    text_error = FONT.render("", 1, (255, 0, 0))
                    sock.sendall((CMD_TO_REGISTRATION + login + Delimiter + password + Delimiter + nick).encode())
                    message = sock.recv(max(len(CMD_SUCCESSFUL_REGISTRATION), len(CMD_FAIL_REGISTRATION))).decode()
                    if message == CMD_SUCCESSFUL_REGISTRATION:
                        done = True
                    else:
                        text_error = FONT.render('Server Error', 1, (255, 0, 0))
                else:
                    text_error = FONT.render(mes, 1, (255, 0, 0))
            if back_button.is_over(pg.mouse.get_pos()):
                window = 'LOG'
                text_error = FONT.render("", 1, (255, 0, 0))
        clock.tick(fps)


if __name__ == '__main__':
    main()
