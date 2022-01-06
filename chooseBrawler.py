import os
import sys

import pygame as pg

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


data = {'nickname': 'Alex', 'money': 151587, 'all_cups': 0,
        'brawlers': {'shelly': [0, 1, 0], 'nita': [1250, 2, 50],
                     'colt': [0, 0, 0], 'bull': [0, 10, 60],
                     'jessie': [0, 2, 0], 'brock': [0, 0, 0],
                     'dynamike': [0, 0, 0], 'bo': [50, 0, 0],
                     'tick': [0, 0, 0], '8-bit': [500, 0, 0],
                     'emz': [0, 0, 0], 'stu': [0, 0, 0],
                     'el_primo': [600, 0, 0], 'barley': [0, 0, 0],
                     'poco': [750, 0, 0], 'rosa': [0, 0, 0],
                     'rico': [0, 0, 0]}}


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




running = True
all_b = []
for i, br in enumerate(data['brawlers']):
    br = ChooseBrawlerButton(10 + i % 4 * 350, 15 + 350 * (i // 4), 300, 300, brawler_name=br)
    all_b.append(br)
    if i == len(data['brawlers']) - 1:
        down_border = br
    if i == 0:
        up_border = br
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
                if up_border.y + 10 <= 50:
                    for b in all_b:
                        b.y += 10
    screen.fill((30, 30, 30))
    for b in all_b:
        b.draw(screen, outline='BLACK')
    pg.display.flip()
    for b in all_b:
        if b.is_over(pg.mouse.get_pos()):
            brawler_menu(b.text)
    clock.tick(fps)
