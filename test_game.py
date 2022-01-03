import os
import sys
from math import pi, cos, sin, acos, sqrt

import pygame
from pygame.draw import line

ev: pygame.event


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left = 10
        self.top = 10
        self.cell_size = 30

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        for i in range(self.height + 1):
            line(screen, pygame.Color((45, 39, 20)), start_pos=(self.left, self.top + i * self.cell_size),
                 end_pos=(self.left + self.width * self.cell_size, self.top + i * self.cell_size), width=4)
        for i in range(self.width + 1):
            line(screen, pygame.Color((45, 39, 20)), start_pos=(self.left + i * self.cell_size, self.top),
                 end_pos=(self.left + i * self.cell_size, self.top + self.height * self.cell_size), width=4)

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell:
            self.on_click(cell)

    def get_cell(self, mouse_pos):
        x, y = mouse_pos
        cell_x = (x - self.left) // self.cell_size
        cell_y = (y - self.top) // self.cell_size
        if cell_x >= self.width or cell_x < 0 or cell_y >= self.height or cell_y < 0:
            return
        return cell_x, cell_y

    def on_click(self, cell):
        print(cell)


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


class Brawler(pygame.sprite.Sprite):
    def __init__(self, x_=0, y_=0, name='Shelly'):
        super().__init__()
        self.image = pygame.transform.scale(load_image(f"brawlers/gaming{name}.png"), (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x_, y_
        self.angle = 0
        self.is_shoot = False

    def update(self):
        self.update_angle()
        global ev
        super().update()
        _x = 0
        _y = 0
        if pygame.key.get_pressed()[pygame.K_d]:
            _x += 5
        if pygame.key.get_pressed()[pygame.K_a]:
            _x -= 5
        if pygame.key.get_pressed()[pygame.K_w]:
            _y -= 5
        if pygame.key.get_pressed()[pygame.K_s]:
            _y += 5
        if mouse_buttons[0]:
            self.is_shoot = True
        else:
            self.is_shoot = False
        self.rect.move_ip(_x, _y)

    def update_angle(self):
        hip = sqrt((x_shoot - x) ** 2 + (y_shoot - y) ** 2)
        if hip:
            _cos = (x - x_shoot) / hip
            _sin = (y - y_shoot) / hip
            self.angle = acos(_cos) if _sin > 0 else 2 * pi - acos(_cos)
        else:
            self.angle = 0


class Ball(pygame.sprite.Sprite):
    acc = 2

    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(load_image("ball.png"), (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = width // 2, height // 2
        self.withPlayer = None
        self.angle = 0
        self.velocity = 20

    def update(self):
        players = pygame.sprite.spritecollide(self, brawlers, False)
        if not self.withPlayer and players:
            self.velocity = 20
            self.withPlayer = players[0]
        else:
            self.withPlayer = None
            # ball_x, ball_y, degree, color = self.rect.x, self.rect.y, angle, self.velocity
            # if ball_x + cos(degree) * velocity < 10:
            #     degree = 180 - degree
            # if ball_x + cos(degree) * velocity > width - 10:
            #     degree = 180 - degree
            # if ball_y - sin(degree) * velocity < 10:
            #     degree = - degree
            # if ball_y - sin(degree) * velocity > height - 10:
            #     degree = - degree
            # ball_y, ball_x = ball_y - sin(radians(degree)) * velocity, ball_x + cos(radians(degree)) * velocity
            # balls[i] = [ball_x, ball_y, degree, color]

    # def shoot(self):
    #     hip = sqrt((x_shoot - x) ** 2 + (y_shoot - y) ** 2)
    #     if not hip:
    #         _cos = (x_shoot - x) / hip
    #         _sin = (y_shoot - y) / hip
    #         self.angle = acos(_cos) if _sin > 0 else 2 * pi - acos(_cos)
    #     else:
    #         self.angle = 0


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, board):
        super().__init__()


board = Board(20, 20)
board.set_view(0, 0, 50)
running = True
fps = 20
size = width, height = 1000, 1000
x_shoot, y_shoot = 800, 800
clock = pygame.time.Clock()
screen = pygame.display.set_mode(size)
brawlers = pygame.sprite.Group()
player = Brawler()
brawlers.add(player)
ball = Ball()
items = pygame.sprite.Group()
items.add(ball)
while running:
    ev = pygame.event.get()
    for event in ev:
        if event.type == pygame.QUIT:
            running = False
    mouse_buttons = pygame.mouse.get_pressed()
    x, y = pygame.mouse.get_pos()
    screen.fill((76, 70, 50))
    board.render(screen)
    brawlers.update()
    pygame.draw.line(screen,
                     pygame.Color("RED") if player.is_shoot else pygame.Color("WHITE"),
                     (player.rect.x + 25, player.rect.y + 25),
                     (player.rect.x + cos(player.angle) * 100 + 25, player.rect.y + sin(player.angle) * 100 + 25),
                     width=10)
    pygame.draw.circle(screen, pygame.Color("RED"), (x_shoot, y_shoot), 50, width=1)
    pygame.draw.circle(screen, pygame.Color("WHITE"), (player.rect.x + 25, player.rect.y + 25), 30, width=2)
    if 2500 >= (x_shoot - x) ** 2 + (y_shoot - y) ** 2:
        pygame.draw.circle(screen, pygame.Color("RED"), (x, y), 30)
    else:
        pygame.draw.circle(screen, pygame.Color("RED"), (
            x_shoot + cos(player.angle) * 50,
            y_shoot + sin(player.angle) * 50), 30)
    brawlers.draw(screen)
    items.draw(screen)
    pygame.display.flip()
    clock.tick(fps)
