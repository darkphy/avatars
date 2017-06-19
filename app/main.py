from PIL import Image, ImageFont, ImageDraw
from random import randint
import argparse
import math


def split_by_n(seq, n):
    seq = str(seq)
    while seq:
        yield int(seq[:n])
        seq = seq[n:]


def get_block_color(uuid, bl, i, j):
    colorlist = [
        (206, 18, 91),
        (45, 14, 55),
        (51, 177, 139),
        (237, 86, 75),
        (241, 241, 241),
        (222, 160, 29)
        ]

    # index = randint(0, len(colorlist)-1)
    index = int(uuid/(bl + (i*2) - j)) % len(colorlist)
    r, g, b = colorlist[index]
    alpha = bl % 255
    return (r, g, b, alpha)


def create_blocks(uuid, blocks=9, split_value=3):
    # make a list of len=blocks using num from uuid
    power = int((blocks*split_value)/2) - len(str(uuid))
    if(power > 0):
        uuid = int(str(int(math.pow(10, power))) + str(uuid))
    ul = list(split_by_n(uuid, split_value))
    ul_rev = [int(math.pow(10, split_value)) - x for x in ul[::-1]]
    ul = ul + ul_rev
    ul = ul[:blocks]
    return ul


def create_layer(uuid, draw, rows=3, columns=3, ImgWidth=512, ImgHeight=512,
                 paddingX=0, paddingY=0):

    # padding
    ImgWidth -= paddingX
    ImgHeight -= paddingY

    width = ImgWidth / rows
    height = ImgHeight / columns
    rx0, ry0, rx1, ry1 = x0, y0, x1, y1 = (paddingX, paddingY, width, height)

    bl = create_blocks(uuid, rows*columns)
    for i in range(0, rows):
        for j in range(0, columns):
            draw.rectangle([(x0, y0), (x1, y1)],
                           get_block_color(uuid, bl[(i*columns)+j], i, j),
                           outline=None)
            if(x0+width < ImgWidth):
                x0 += width
            else:
                x0 = rx0
            if(x1+width <= ImgWidth):
                x1 += width
            else:
                x1 = rx1
        if(y0+height < ImgHeight):
            y0 += height
        else:
            y0 = ry0
        if(y1+height <= ImgHeight):
            y1 += height
        else:
            y1 = ry1

    return draw


def images_loop(uuid, layers=2, width=1000, height=1000, text="",
                fontTTF="Pillow/Tests/fonts/FreeMono.ttf",
                fontSize=40):
    image_final = None
    images = []
    white = (255, 255, 255, 0)
    for i in range(0, layers):
        images.append(Image.new("RGBA", (width, height), white))
    fff = images[0]
    for i in range(0, layers):
        draw = ImageDraw.Draw(images[i], 'RGBA')
        draw = create_layer(uuid, draw, ImgWidth=width, ImgHeight=height)
        rotatedeg = ((uuid/(i+1)) % 360) * (1 if (i % 2 == 0) else -1)
        images[i] = images[i].rotate(rotatedeg, resample=Image.BICUBIC)
        if image_final is not None:
            image_final = Image.composite(images[i], image_final, images[i])
        else:
            image_final = images[i]
    image_final = Image.composite(image_final, fff, image_final)
    if len(text) > 0:
        txtImage = Image.new('RGBA', image_final.size, (255, 255, 255, 0))
        tdraw = ImageDraw.Draw(txtImage)
        fnt = ImageFont.truetype(fontTTF, fontSize)
        tw, th = tdraw.textsize(text, font=fnt)
        hfix = (30/100*th)  # unusual height fix
        tdraw.text(((width-tw)/2, (height-th-hfix)/2), text, font=fnt,
                   fill=(185, 241, 241, 128))
        image_final = Image.alpha_composite(image_final, txtImage)

    return image_final


parser = argparse.ArgumentParser(description='Create Unique Identicons Image')
parser.add_argument('-i', '--id', type=int, help='A Unique id',
                    required=True)
parser.add_argument('-o', '--out', help='Output filename',
                    required=True)
parser.add_argument('-l', '--layers', type=int,
                    help='Specify the number of layers of image')
parser.add_argument('-w', '--width', type=int, help='Width of Image')
parser.add_argument('-he', '--height', type=int, help='Height of Image')
parser.add_argument('-t', '--text', help='Text to Print at center')
parser.add_argument('-s', '--fsize', type=int, help='Font Size of the Text')
parser.add_argument('-fttf', '--fontTTF',
                    help='Font ttf location')
args = vars(parser.parse_args())

height = width = 1000
layers = 2
uuid = args['id']
text = ""
fontSize = 200
fontTTF = "Pillow/Tests/fonts/FreeMono.ttf"

if args['layers']:
    layers = args['layers']
if args['height']:
    height = args['height']
if args['width']:
    width = args['width']
if args['text']:
    text = args['text']
if args['fsize']:
    fontSize = args['fsize']
if args['fontTTF']:
    fontTTF = args['fontTTF']

filename = "my_drawing.jpg"

save_image = images_loop(uuid, layers, width, height,
                         text=text, fontSize=fontSize, fontTTF=fontTTF)
save_image.save(filename)
