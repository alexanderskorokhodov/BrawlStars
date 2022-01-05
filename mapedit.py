import pygame
from pygame.draw import rect


class Board:
    # создание поля
    def __init__(self, width, height, b):
        self.width = width
        self.height = height
        self.board = b
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
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j] == 1:
                    rect(screen, 'green', [self.left + j * self.cell_size + 1, self.top + i * self.cell_size + 1,
                                           self.cell_size - 2, self.cell_size - 2])
                elif self.board[i][j] == 2:
                    rect(screen, (188, 152, 126),
                         [self.left + j * self.cell_size + 1, self.top + i * self.cell_size + 1,
                          self.cell_size - 2, self.cell_size - 2])
                elif self.board[i][j] == 3:
                    rect(screen, 'brown', [self.left + j * self.cell_size + 1, self.top + i * self.cell_size + 1,
                                           self.cell_size - 2, self.cell_size - 2])
                elif self.board[i][j] == 4:
                    rect(screen, (255, 0, 0),
                         [self.left + j * self.cell_size + 1, self.top + i * self.cell_size + 1,
                          self.cell_size - 2, self.cell_size - 2])
                elif self.board[i][j] == 5:
                    rect(screen, 'white', [self.left + j * self.cell_size + 1, self.top + i * self.cell_size + 1,
                                           self.cell_size - 2, self.cell_size - 2])
                elif self.board[i][j] == 6:
                    rect(screen, 'purple', [self.left + j * self.cell_size + 1, self.top + i * self.cell_size + 1,
                                            self.cell_size - 2, self.cell_size - 2])
                elif self.board[i][j] == 7:
                    rect(screen, 'blue', [self.left + j * self.cell_size + 1, self.top + i * self.cell_size + 1,
                                         self.cell_size - 2, self.cell_size - 2])
                rect(screen, 'white', [self.left + j * self.cell_size, self.top + i * self.cell_size,
                                       self.cell_size, self.cell_size], width=1)

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
        self.board[cell[1]][cell[0]] = (self.board[cell[1]][cell[0]] + 1) % 8


n = {1: 'X', 2: '.', 3: '#', 4: 'S', 5: 'P', 6: 'C', 7: '-'}
m = {'X': 1, '.': 2, '#': 3, 'S': 4, 'P': 5, 'C': 6, '-': 7}
map_ = open("data/maps/DriedUpRiver.txt", 'r').readlines()
map_ = list(map(lambda x: list(map(lambda y: m[y], list(x.rstrip()))), map_))
print(map_)
board = Board(len(map_), len(map_), map_)
board.set_view(0, 0, 15)
running = True
fps = 24
size = width, height = 1000, 1000
clock = pygame.time.Clock()
screen = pygame.display.set_mode(size)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            text = board.board
        if event.type == pygame.MOUSEBUTTONDOWN:
            board.get_click(event.pos)
    screen.fill((0, 0, 0))
    board.render(screen)
    pygame.display.flip()
    clock.tick(fps)
res = ''
for i in range(len(map_)):
    for j in range(len(map_)):
        res += n[map_[i][j]]
    res += '\n'
with open(file='data/maps/DriedUpRiver.txt', mode='w') as file:
    file.write(res)
