import os.path
import sys

import pygame
from pygame.draw import rect


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


def main():
    pygame.init()
    size = width, height = 1500, 700
    screen = pygame.display.set_mode(size)

    # создадим группу, содержащую все спрайты
    all_sprites = pygame.sprite.Group()
    background = pygame.sprite.Sprite()
    background.image = load_image("login1.jpg")
    background.rect = background.image.get_rect(center=(width // 2, height // 2))
    length_of_loading = 100
    loading = rect(screen, "Gray", (100, 600, length_of_loading, 50), width=1, border_radius=25)
    # добавим спрайт в группу
    all_sprites.add(background)
    running = True
    fps = 60
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((0, 0, 255))
        all_sprites.draw(screen)
        length_of_loading += 5
        loading = rect(screen, "black", (100, 600, length_of_loading, 50), width=0, border_radius=25)
        pygame.display.flip()
        clock.tick(fps)
        if length_of_loading >= width - 200:
            running = False
