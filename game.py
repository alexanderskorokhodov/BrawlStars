import pygame
from pygame.draw import line

ev: pygame.event

tiles = {
    'wall': 'data/maps/tiles/wall.png',
    'ground': 'data/maps/tiles/ground.png',
    'skeleton': 'data/maps/tiles/sceleton.png',
    'bushes': 'data/maps/tiles/bushes.png',
    'water': 'data/maps/tiles/river.png',
    'chest': 'data/maps/tiles/chest.png'
}


def load_map(map_name):
    filename = "data/maps/" + map_name + '.txt'
    with open(filename, 'r') as mapFile:
        _map = [i.strip() for i in mapFile]
    return _map


class Map:
    def __init__(self, map_name):
        self.field = load_map(map_name)
        self.width = len(self.field[0])
        self.height = len(self.field)
        self.cell_size = 17

    def set_view(self, cell_size):
        self.cell_size = cell_size

    def render(self, screen):
        for i in range(self.height + 1):
            line(screen, pygame.Color((45, 39, 20)), start_pos=(0, i * self.cell_size),
                 end_pos=(self.width * self.cell_size, i * self.cell_size), width=4)
        for i in range(self.width + 1):
            line(screen, pygame.Color((45, 39, 20)), start_pos=(i * self.cell_size, 0),
                 end_pos=(i * self.cell_size, self.height * self.cell_size), width=4)
