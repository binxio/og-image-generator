import os
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import sys
from .logger import log
import textwrap
 
data_dir = os.path.dirname(__file__)

def _mask(img):
    gradient_magnitude = 0.66
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    width, height = img.size
    gradient = Image.new('L', (width, 1), color=0xFF)
    print(width)
    for x in range(width):
        gradient.putpixel((x, 0), int(255 * (1 - gradient_magnitude * float(x)/width)))
    alpha = gradient.resize(img.size)
    black_img = Image.new('RGBA', (width, height), color=0) # i.e. black
    black_img.putalpha(alpha)
    return Image.alpha_composite(img, black_img)    

       
def _write_title(img, text):
    x, y = (32, 32)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(os.path.join(data_dir, 'fonts', 'Ubuntu-B.ttf'), 64)
    width, height = font.getsize(text)
    lines = textwrap.wrap(text, width=32)
    for line in lines:
        draw.text((x, y), line, font=font, fill=(255,255,255))
        y += height

def _write_subtitle(img, text):
    width, height = img.size
    draw = ImageDraw.Draw(img)
    x, y = (32, int(height * 0.45))
    font = ImageFont.truetype(os.path.join(data_dir, 'fonts', 'Ubuntu-M.ttf'), 36)
    width, height = font.getsize(text)
    lines = textwrap.wrap(text, width=50)
    for line in lines:
        draw.text((x, y), line, font=font, fill=(255,255,255))
        y += height


def _write_author(img, text):
    width, height = img.size
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(os.path.join(data_dir, 'fonts', 'Ubuntu-M.ttf'), 36)
    _, font_height = font.getsize(text)
    lines = textwrap.wrap(text, width=36)
    draw.text((32 + 220 + 16, height - 32 - 16 - font_height), text, font=font, fill=(255,255,255))

def _write_logo(img):
    x, y = img.size
    logo = Image.open(os.path.join(data_dir, 'images', 'binx-logo-white.png'))
    logo = logo.resize((220,65))
    img.paste(logo, (32,  y - 32 - logo.size[1]), logo)


def generate(in_file:str, title:str, subtitle:str, author:str, out_file:str):
    img = Image.open(in_file)
    width, height = img.size
    if height < 630:
        log.error(f'height must at least 630, this image is {width}x{height}')
        exit(1)
    if width < 1200:
        log.error(f'width must at least 1200, this image is {width}x{height}')
        exit(1)

    img = _mask(img)
    _write_logo(img)
    _write_title(img, title)
    _write_subtitle(img, subtitle)
    _write_author(img, author)
    img.save(out_file)
