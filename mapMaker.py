import math

from PIL import Image


def color_(color):
    a = []
    for c in colors:
        a.append(math.sqrt((c[0] - color[0]) ** 2 + (c[1] - color[1]) ** 2 + (c[2] - color[2]) ** 2))
    # if sum(color[:3]) < 350:
    #     return 1
    return a.index(min(a))


blocks = int(1000/16.6)
im = '/Users/alexanderskorokhodov/Downloads/%3F%3F%3F%3F%3F%3F%3F%3F%3F_%3F_%3F%3F%3F%3F%3F%3F%3F%3F.png'
map_ = Image.open(im)
#map_.show()
# map_ = map_.resize((blocks + 2, blocks + 2))
# map_ = map_.crop((1, 1, blocks + 1, blocks + 1))
# map_ = ImageEnhance.Contrast(image=map_).enhance(1.2)
size = 16.6
new_map = Image.new("RGB", (blocks, blocks))
map_ = Image.open(im)
pixels = map_.load()
for i in range(blocks):
    for j in range(blocks):
        lx = int(i * size)
        ur = int(j * size)
        # COLOR = (0, 0, 0)
        # for X in range(25):
        #     for Y in range(10):
        #         COLOR = (COLOR[0] + pixels[lx + X, ur + Y][0], COLOR[1] + pixels[lx + X, ur + Y][1],
        #                  COLOR[2] + pixels[lx + X, ur + Y][2])
        # COLOR = (COLOR[0] // 250, COLOR[1] // 250, COLOR[2] // 250)
        # new_map.putpixel((i, j), COLOR)
        new_map.putpixel((i, j), pixels[lx+size//2, ur+size//6])

new_map.show()
grass = (255, 184, 20)
grass2 = (225, 109, 20)
water = (66, 170, 255)
w2 = (237, 131, 99)
blue = (214, 55, 54)
gr1 = (198, 135, 98)
gr2 = (187, 127, 93)
colors = [grass, w2, blue, gr1, gr2, grass2, water]
pixels = new_map.load()
new_map1 = Image.new("RGB", (blocks, blocks))
res = ''
for j in range(blocks):
    for i in range(blocks):
        id__ = color_(pixels[i, j])
        if id__ in [1]:
            new_map1.putpixel((i, j), (180, 135, 100))
            res += '.'
        elif id__ in [2, 3, 4]:
            new_map1.putpixel((i, j), (92, 59, 0))
            res += '#'
        elif id__ in [0, 5]:
            new_map1.putpixel((i, j), (255, 255, 0))
            res += 'X'
        else:
            new_map1.putpixel((i, j), (66, 170, 255))
            res += '-'
    res += '\n'
new_map1.show()
with open(file='data/maps/RockwallBrawl.txt', mode='w') as file:
    file.write(res)

