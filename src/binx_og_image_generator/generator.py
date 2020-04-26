import os
import click
from collections import namedtuple
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import sys
from .logger import log
import textwrap

data_dir = os.path.dirname(__file__)

Blog = namedtuple("Blog", "title subtitle author")


def _mask(img, gradient_magnitude:float):
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    width, height = img.size
    gradient = Image.new("L", (width, 1), color=0xFF)
    for x in range(width):
        gradient.putpixel(
            (x, 0), int(255 * (1 - gradient_magnitude * float(x) / width))
        )
    alpha = gradient.resize(img.size)
    black_img = Image.new("RGBA", (width, height), color=0)  # i.e. black
    black_img.putalpha(alpha)
    return Image.alpha_composite(img, black_img)


def _write_title(img, text):
    x, y = (32, 32)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(os.path.join(data_dir, "fonts", "Ubuntu-B.ttf"), 64)
    width, height = font.getsize(text)
    lines = textwrap.wrap(text, width=32)
    for line in lines:
        draw.text((x, y), line, font=font, fill=(255, 255, 255))
        y += height


def _write_subtitle(img, text):
    width, height = img.size
    draw = ImageDraw.Draw(img)
    x, y = (32, int(height * 0.45))
    font = ImageFont.truetype(os.path.join(data_dir, "fonts", "Ubuntu-M.ttf"), 36)
    width, height = font.getsize(text)
    lines = textwrap.wrap(text, width=50)
    for line in lines:
        draw.text((x, y), line, font=font, fill=(255, 255, 255))
        y += height


def _write_author(img, text):
    width, height = img.size
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(os.path.join(data_dir, "fonts", "Ubuntu-M.ttf"), 36)
    _, font_height = font.getsize(text)
    lines = textwrap.wrap(text, width=36)
    draw.text(
        (32 + 220 + 16, height - 32 - 16 - font_height),
        text,
        font=font,
        fill=(255, 255, 255),
    )


def _write_logo(img):
    x, y = img.size
    logo = Image.open(os.path.join(data_dir, "images", "binx-logo-white.png"))
    logo = logo.resize((220, 65))
    img.paste(logo, (32, y - 32 - logo.size[1]), logo)


def generate(
    blog: Blog,
    in_file: str,
    out_file: str,
    resize: bool = False,
    overwrite: bool = False,
    gradient_magnitude: float = 0.9,
):
    img = Image.open(in_file)
    width, height = img.size
    if height < 630:
        log.error(f"height must at least 630, this image is {width}x{height}")
        exit(1)
    if width < 1200:
        log.error(f"width must at least 1200, this image is {width}x{height}")
        exit(1)

    if resize:
        log.info(
            "resizing %dx%d to 1200x630, ratio match %d%%",
            width,
            height,
            int((width / height) / (1200 / 630) * 100),
        )
        img = img.resize((1200, 630))

    img = _mask(img, gradient_magnitude)
    log.info("add logo")
    _write_logo(img)
    log.info("add title")
    _write_title(img, blog.title)
    log.info("add subtitle")
    _write_subtitle(img, blog.subtitle)
    log.info("add author")
    _write_author(img, blog.author)
    if not out_file:
        out_file = os.path.join(
            os.path.dirname(in_file), "og-" + os.path.basename(in_file)
        )

    if os.path.exists(out_file) and not overwrite:
        log.error("%s already exists, and no --overwrite was specified", out_file)
        return

    if img.mode != "RGB" and (out_file.endswith(".jpg") or out_file.endswith(".jpeg")):
        img = img.convert("RGB")

    img.save(out_file)
    log.info("og image saved to %s", out_file)


@click.command(help="generate an og image for blog")
@click.option("--title", required=True, help="of the blog")
@click.option("--subtitle", required=True, help="of the blog")
@click.option("--author", required=True, help="of the blog")
@click.option("--gradient-magnitude", "-g", type=float, default=0.9, help="of the mask")
@click.option(
    "--output",
    required=False,
    help="filename of the image, default prefix og- to filename",
)
@click.option(
    "--overwrite/--no-overwrite", required=False, default=False, help="output file"
)
@click.option(
    "--resize/--no-resize", is_flag=True, default=True, help="to 1200x630 pixels"
)
@click.argument("image", type=click.Path(dir_okay=False, exists=True), nargs=1)
def main(title, subtitle, author, output, image, resize, overwrite, gradient_magnitude):
    overwrite = overwrite or output
    blog = Blog(title, subtitle, author)
    generate(
        blog,
        in_file=image,
        out_file=output,
        resize=resize,
        overwrite=overwrite,
        gradient_magnitude=gradient_magnitude,
    )
