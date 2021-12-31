import pygame as pg

pg.init()
COLOR_INACTIVE = pg.Color('lightskyblue3')
COLOR_ACTIVE = pg.Color('dodgerblue2')
FONT = pg.font.SysFont('arial', 18)
size = width, height = 1500, 700
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
                if event.key == pg.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        w = max(self.rect.w, self.txt_surface.get_width() + 10)
        self.rect.w = w

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


def check_data():
    data = get_data()
    if all(data):
        return True
    return False


def main():
    global input_boxes
    text_login = FONT.render("login", 1, COLOR_INACTIVE)
    text_password = FONT.render("password", 1, COLOR_INACTIVE)
    text_error = FONT.render("", 1, (255, 0, 0))
    screen.blit(text_login, (600, 50, 300, 32))
    screen.blit(text_password, (600, 150, 300, 32))
    screen.blit(text_error, (600, 350, 300, 32))
    input_box1 = InputBox(600, 100, 300, 32)
    input_box2 = InputBox(600, 200, 300, 32)
    input_boxes = [input_box1, input_box2]
    continue_button = Button(600, 300, 300, 32, text='Continue')
    done = False
    clock = pg.time.Clock()
    while not done:
        global ev
        ev = pg.event.get()
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

        screen.blit(text_password, (600, 150, 300, 32))
        screen.blit(text_login, (600, 50, 300, 32))
        screen.blit(text_error, (600, 350, 300, 32))
        pg.display.flip()
        if continue_button.is_over(pg.mouse.get_pos()):
            if check_data():
                login, password = get_data()
                done = True
                text_error = FONT.render("", 1, (255, 0, 0))
            else:
                text_error = FONT.render("Check input data", 1, (255, 0, 0))
        clock.tick(30)


if __name__ == '__main__':
    main()
