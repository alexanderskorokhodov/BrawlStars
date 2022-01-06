import os.path
import sys
import time
from json import loads

import pygame as pg

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
pg.display.set_caption('Brawl Stars', 'Brawl Stars')
COLOR_INACTIVE = pg.Color('lightskyblue3')
COLOR_ACTIVE = pg.Color('dodgerblue2')
COLOR_DEFAULT = pg.Color(102, 102, 190)
MAIN_FONT = pg.font.Font('./data/mainFont.ttf', 36)
BRAWLER_FONT = pg.font.Font('./data/mainFont.ttf', 70)
CHOOSE_BRAWLER_FONT = pg.font.Font('./data/mainFont.ttf', 40)
CUPS_FONT = pg.font.Font('./data/mainFont.ttf', 30)
POWER_FONT = pg.font.Font('./data/mainFont.ttf', 40)
size = width, height = 1500, 700
clock = pg.time.Clock()
fps = 60
screen = pg.display.set_mode(size)
ev: pg.event

ranks = []
for row in open('data/ranks.csv', mode='r').readlines()[1:]:
    ranks.append(tuple(map(int, row.strip().split(';'))))


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


class ChooseBrawlerButton:
    def __init__(self, x, y, w, h, data, brawler_name='el_primo', color=COLOR_DEFAULT, r=0,
                 text_color=pg.Color("Black"),
                 bold=False, sound='data/tones/menu_click_08.mp3'):
        self.color = color
        self.og_col = color
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.text = brawler_name
        self.radius = r
        self.textColor = text_color
        self.bold = bold
        self.sound = pg.mixer.Sound(sound)
        self.img = load_image(f'brawlers/inChoose/{brawler_name.lower()}.png')
        self.rank = max(list((filter(lambda s: s[1] <= data['brawlers'][brawler_name][0], ranks))),
                        key=lambda a: a[0])[0]
        self.cups = data['brawlers'][brawler_name][0]

    def draw(self, win, outline=None):
        # Call this method to draw the button on the screen
        fg = pg.sprite.Group()
        brawler_group = pg.sprite.Group()
        rank_img = pg.sprite.Sprite()
        rank_img.image = pg.transform.scale(load_image(f"ranks/Rank_{self.rank}.png"), (60, 68))
        rank_img.rect = rank_img.image.get_rect()
        rank_img.rect.x, rank_img.rect.y = self.x - 10, self.y - 15
        if outline:
            pg.draw.rect(win, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 3,
                         border_radius=self.radius)
        pg.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0, border_radius=self.radius)
        pg.draw.rect(win, self.color, (self.x, self.y, self.width, 32), 0, border_top_left_radius=self.radius,
                     border_top_right_radius=self.radius)
        brawler = pg.sprite.Sprite()
        brawler.image = pg.transform.scale(self.img, (self.height - 16, int((self.height - 16) / 6 * 5)))
        brawler.rect = brawler.image.get_rect()
        brawler.rect.x, brawler.rect.y = self.x, self.y + 32
        pg.draw.rect(win, (86, 3, 25), (self.x, self.y, self.width, 32), 0)
        brawler_group.add(brawler)
        fg.add(rank_img)
        brawler_group.draw(win)
        pg.draw.rect(win, 'BLACK', (self.x, self.y + 32, self.width, int((self.height - 16) / 6 * 5)), 4)
        fg.draw(win)
        if self.text != '':
            draw_outline(self.x, self.y + (self.height / 2) + 50, self.text.upper().replace('_', ' '), win,
                         CHOOSE_BRAWLER_FONT)
        draw_outline(self.x + self.width // 2, self.y - 3, str(self.cups), win, CUPS_FONT)

    def is_over(self, pos):
        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.height:
                self.color = (255, 245, 238)
            else:
                self.color = self.og_col
        else:
            self.color = self.og_col
        global ev
        for event in ev:
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.x < pos[0] < self.x + self.width:
                        if self.y < pos[1] < self.y + self.height:
                            self.sound.play()
                            return self.text


class Button:
    def __init__(self, x, y, w, h, text='', color=COLOR_DEFAULT, r=0, text_color=pg.Color("Black"), bold=False,
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
        self.sound = pg.mixer.Sound(sound)

    def draw(self, win, outline=None):
        # Call this method to draw the button on the screen
        if outline:
            pg.draw.rect(win, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 3,
                         border_radius=self.radius)
        pg.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0, border_radius=self.radius)

        if self.text != '':
            font = MAIN_FONT
            text = font.render(self.text, self.bold, self.textColor)
            win.blit(text, (
                self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def is_over(self, pos):
        # Pos is the mouse position or a tuple of (x,y) coordinates
        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.height:
                self.color = (255, 245, 238)
            else:
                self.color = self.og_col
        else:
            self.color = self.og_col
        global ev
        for event in ev:
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.x < pos[0] < self.x + self.width:
                    if self.y < pos[1] < self.y + self.height:
                        self.sound.play()
                        return True


class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = MAIN_FONT.render(text, True, self.color)
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
                self.txt_surface = MAIN_FONT.render(self.text, True, self.color)

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
    try_button = Button(600, 300, 300, 64, text='Try again', color=COLOR_DEFAULT, r=16)
    all_sprites = pg.sprite.Group()
    background = pg.sprite.Sprite()
    background.image = load_image(f"serverError1.jpg")
    background.rect = background.image.get_rect(center=(width // 2, height // 2))
    all_sprites.add(background)
    text_server_error = MAIN_FONT.render("Error: Cannot connect to server", True, (255, 0, 0))
    while running:
        global ev
        ev = pg.event.get()
        for event in ev:
            if event.type == pg.QUIT:
                quit()
        screen.fill((30, 30, 30))
        all_sprites.draw(screen)
        try_button.draw(screen)
        screen.blit(text_server_error, (500, 400, 300, 32))
        if try_button.is_over(pg.mouse.get_pos()):
            running = False
        pg.display.flip()
        clock.tick(fps)
    return True


def brawler_menu(user_data, chosen_brawler):
    running = True
    brawlers_stats = user_data['brawlers']
    brawlers = list(brawlers_stats.keys())
    current_id = brawlers.index(chosen_brawler)
    bg_sprites = pg.sprite.Group()
    background = pg.sprite.Sprite()
    background.image = load_image("menu.jpg")
    background.rect = background.image.get_rect(center=(width // 2, height // 2))
    back_button = Button(20, 20, 300, 64, text=f'< BACK', r=20)
    bg_sprites.add(background)
    brawler_name = BRAWLER_FONT.render(f'{brawlers[current_id]}'.title(), True, pg.Color("BLACK"))
    power_text = POWER_FONT.render(
        f'Power {brawlers_stats[brawlers[current_id]][1]} ({brawlers_stats[brawlers[current_id]][2]}/100)', True,
        pg.Color("BLACK"))
    cups_button = Button(150, 630, 430, 50, text='Cups:', r=20)
    select_button = Button(1000, 630, 400, 50, text='Select', r=20, sound='data/tones/select_brawler_01.mp3')
    brawler = pg.sprite.Sprite()
    brawler.image = pg.transform.scale(load_image(f"brawlers/inMenu/{brawlers[current_id]}.png"), (400, 400))
    brawler.rect = brawler.image.get_rect()
    brawler.rect.x, brawler.rect.y = 175, 100
    fg = pg.sprite.Group()
    fg.add(brawler)
    while running:
        global ev
        ev = pg.event.get()
        for event in ev:
            if event.type == pg.QUIT:
                quit()
        screen.fill((30, 30, 30))
        bg_sprites.draw(screen)
        brawler_name = BRAWLER_FONT.render(f'{brawlers[current_id]}'.upper(), True, pg.Color("BLACK"))
        power_text = POWER_FONT.render(
            f'Power {brawlers_stats[brawlers[current_id]][1]} ({brawlers_stats[brawlers[current_id]][2]}/100)', True,
            pg.Color("BLACK"))
        cups_button.text = 'Cups: ' + str(brawlers_stats[brawlers[current_id]][0])
        screen.blit(brawler_name, (1000, 100, 300, 64))
        bg_sprites.draw(screen)
        back_button.draw(screen, outline=pg.Color("BLACK"))
        cups_button.draw(screen, outline=pg.Color("BLACK"))
        screen.blit(power_text, (1000, 200, 300, 64))
        select_button.draw(screen, outline=pg.Color("BLACK"))
        brawler.image = pg.transform.scale(load_image(f"brawlers/inMenu/{brawlers[current_id].lower()}.png"),
                                           (400, 400))
        brawler.rect = brawler.image.get_rect()
        brawler.rect.x, brawler.rect.y = 175, 100
        fg.draw(screen)
        if back_button.is_over(pg.mouse.get_pos()):
            return None
        if select_button.is_over(pg.mouse.get_pos()):
            return brawlers[current_id]
        current_id = current_id % len(brawlers)
        pg.display.flip()
        clock.tick(fps)
    return None


def brawlers_menu(user_data):
    global ev
    running = True
    all_b = []
    for i, br in enumerate(user_data['brawlers']):
        br = ChooseBrawlerButton(250 + i % 3 * 350, 80 + 325 * (i // 3), 300, 300, user_data, brawler_name=br)
        all_b.append(br)
        if i == len(user_data['brawlers']) - 1:
            down_border = br
        if i == 0:
            up_border = br
    bg_sprites = pg.sprite.Group()
    background = pg.sprite.Sprite()
    background.image = load_image("menu.jpg")
    background.rect = background.image.get_rect(center=(width // 2, height // 2))
    back_button = Button(20, 20, 150, 64, text=f'< BACK', r=20)
    bg_sprites.add(background)
    while running:
        ev = pg.event.get()
        for event in ev:
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN or event.type == pg.MOUSEBUTTONUP:
                if event.button == 5:
                    if down_border.y - 10 + down_border.height >= height - 50:
                        for b in all_b:
                            b.y -= 10
                if event.button == 4:
                    if up_border.y + 10 <= 80:
                        for b in all_b:
                            b.y += 10
        screen.fill((30, 30, 30))
        back_button.draw(screen, outline=pg.Color("BLACK"))
        for b in all_b:
            b.draw(screen, outline='BLACK')
        pg.display.flip()
        if back_button.is_over(pg.mouse.get_pos()):
            return None
        for b in all_b:
            if b.is_over(pg.mouse.get_pos()):
                res = brawler_menu(user_data, b.text)
                if res:
                    return res
        clock.tick(fps)
    return None


def play():
    pass


def main(sock):
    running = True
    bg_sprites = pg.sprite.Group()
    background = pg.sprite.Sprite()
    background.image = load_image("menu.jpg")
    background.rect = background.image.get_rect(center=(width // 2, height // 2))
    fg_sprites = pg.sprite.Group()
    trophy = pg.sprite.Sprite()
    trophy.image = pg.transform.scale(load_image("trophy.png"), (64, 64))
    trophy.rect = trophy.image.get_rect()
    trophy.rect.x, trophy.rect.y = 350, 20
    fg_sprites.add(trophy)
    coin = pg.sprite.Sprite()
    coin.image = pg.transform.scale(load_image("coin.png"), (64, 64))
    coin.rect = coin.image.get_rect()
    coin.rect.x, coin.rect.y = 1000, 20
    fg_sprites.add(coin)
    bg_sprites.add(background)
    user_button = Button(20, 20, 300, 64, text=f'username', r=20, bold=True)
    trophies_button = Button(350, 20, 200, 64, text=f'', r=20, bold=True)
    money_button = Button(1000, 20, 200, 64, text=f'', r=20, text_color=pg.Color("WHITE"), color=pg.Color("Black"),
                          bold=True)
    brawlers_menu_button = Button(20, 250, 200, 64, text='BRAWLERS', r=20, color=pg.Color("Yellow"))
    user_data = get_player_info(sock)
    user_button.text = user_data['nickname']
    trophies_button.text = '    ' + str(user_data['all_cups'])
    money_button.text = '      ' + str(user_data['money'])
    current_brawler = list(user_data['brawlers'].keys())[0]
    brawler = pg.sprite.Sprite()
    brawler.image = pg.transform.scale(load_image(f"brawlers/inMenu/{current_brawler.lower()}.png"), (450, 450))
    brawler.rect = brawler.image.get_rect(center=(width // 2, height // 2))
    fg_sprites.add(brawler)
    event_button = Button(500, 580, 500, 100, text='SHOWDOWN', r=20, color=pg.Color("yellow"), bold=True)
    event_img = pg.sprite.Sprite()
    event_img.image = pg.transform.scale(load_image("showdown.png"), (100, 100))
    event_img.rect = event_img.image.get_rect()
    event_img.rect.x, event_img.rect.y = 500, 580
    fg_sprites.add(event_img)
    play_button = Button(1050, 580, 400, 100, text='PLAY', r=20, color=pg.Color("Yellow"), bold=True)
    pg.mixer.music.load('data/tones/main-menu-2.mp3')
    pg.mixer.music.play(-1)
    while running:
        brawler.image = pg.transform.scale(load_image(f"brawlers/inMenu/{current_brawler.lower()}.png"), (450, 450))
        brawler.rect = brawler.image.get_rect(center=(width // 2, height // 2))
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
        play_button.draw(screen, outline=pg.Color('BLACK'))
        brawlers_menu_button.draw(screen, outline=pg.Color("Black"))
        event_button.draw(screen, outline=pg.Color("Black"))
        fg_sprites.draw(screen)
        pg.display.flip()
        if brawlers_menu_button.is_over(pg.mouse.get_pos()):
            chosen_brawler = brawlers_menu(user_data)
            if chosen_brawler:
                current_brawler = chosen_brawler
        if play_button.is_over(pg.mouse.get_pos()):
            play()
        clock.tick(fps)


if __name__ == '__main__':
    main(None)
