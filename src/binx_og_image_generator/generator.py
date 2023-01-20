import os
import click
from collections import namedtuple
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw, ImageColor
import sys
from .logger import log
import textwrap

data_dir = os.path.dirname(__file__)

Blog = namedtuple("Blog", "title subtitle author")


class Generator:
    def __init__(self, brand: str):
        self.medium_font = (
            "Ubuntu-M.ttf" if brand == "binx.io" else "proximanova-medium.ttf"
        )
        self.bold_font = "Ubuntu-B.ttf" if brand == "binx.io" else "proximanova-bold.ttf"
        self.logo = Image.open(
            os.path.join(
                data_dir,
                "images",
                "binx-logo-white.png" if brand == "binx.io" else "xebia-logo-purple.png",
            )
        )
        self.brand = brand

    def _mask(self, img, gradient_magnitude: float):
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

    def _write_title(self, img, text):
        x, y = (32, 32)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(os.path.join(data_dir, "fonts", self.bold_font), 64)
        width, height = font.getsize(text)
        lines = textwrap.wrap(text, width=32)
        for line in lines:
            draw.text((x, y), line, font=font, fill=(255, 255, 255))
            y += height

    def _write_subtitle(self, img, text):
        width, height = img.size
        draw = ImageDraw.Draw(img)
        x, y = (32, int(height * 0.45))
        font = ImageFont.truetype(os.path.join(data_dir, "fonts", self.medium_font), 36)
        width, height = font.getsize(text)
        lines = textwrap.wrap(text, width=50)
        for line in lines:
            draw.text((x, y), line, font=font, fill=(255, 255, 255))
            y += height

    def _write_author(self, img, text):
        width, height = img.size
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(os.path.join(data_dir, "fonts", self.medium_font), 36)
        lines = textwrap.wrap(text, width=36)
        if self.brand == "binx.io":
            draw.text(
                (32 + 247 + 16, height - 36 - 16 - 32),
                text,
                font=font,
                fill=(255, 255, 255),
            )
        else:
            draw.text(
                (32, height - 36 - 16 - 32),
                text,
                font=font,
                fill=(255, 255, 255),
            )


    def _write_logo(self, img):
        x, y = img.size
        logo_x, logo_y = self.logo.size
        logo = self.logo.resize((247, int(247 / logo_x * logo_y)))
        if self.brand == "binx.io":
            img.paste(logo, (32, y - 32 - logo.size[1]), logo)
        else:
            img.paste(logo, (x - 247 - 32, y - 32 - logo.size[1]), logo)


    def generate(
        self,
        blog: Blog,
        in_file: str,
        out_file: str,
        overwrite: bool = False,
        gradient_magnitude: float = 0.9,
    ):
        img = Image.open(in_file)
        img = resize_image(img)
        img = self._mask(img, gradient_magnitude)
        log.info("add logo")
        self._write_logo(img)
        log.info("add title")
        self._write_title(img, blog.title)
        log.info("add subtitle")
        self._write_subtitle(img, blog.subtitle)
        log.info("add author")
        self._write_author(img, blog.author)
        if not out_file:
            out_file = os.path.join(
                os.path.dirname(in_file), "og-" + os.path.basename(in_file)
            )

        if os.path.exists(out_file) and not overwrite:
            log.error("%s already exists, and no --overwrite was specified", out_file)
            return

        if img.mode != "RGB" and (
            out_file.endswith(".jpg") or out_file.endswith(".jpeg")
        ):
            img = img.convert("RGB")

        img.save(out_file)
        log.info("og image saved to %s", out_file)


def resize_image(image: Image) -> Image:
    """
    resize the image to be the perfect og image size: 1200x630px
    """
    width, height = image.size
    if width != 1200:
        new_height = int(height * 1200 / width)
        log.info("resizing %dx%d to %dx%d", width, height, 1200, new_height)
        image = image.resize((1200, new_height))
        width = 1200
        width, height = image.size

    if height > 630:
        log.info("cropping to maximum height of 630px")
        top = int((height - 630) / 2)
        bottom = 630 + top
        image = image.crop((0, top, 1200, bottom))
        width, height = image.size

    if height < 630:
        log.info(
            "resizing %dx%d to 1200x630, ratio match %d%%",
            width,
            height,
            int((width / height) / (1200 / 630) * 100),
        )
        new_image = Image.new("RGBA", (1200, 630), (255, 0, 0, 0))
        new_image.paste(image, (0, int((630 - height) / 2)))
        image = new_image

    return image


def generate(
    blog: Blog,
    in_file: str,
    out_file: str,
    overwrite: bool = False,
    gradient_magnitude: float = 0.9,
    brand: str = "xebia.com",
):
    generator = Generator(brand)
    generator.generate(blog, in_file, out_file, overwrite, gradient_magnitude)


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
    "--brand",
    type=click.Choice(["xebia.com", "binx.io"]),
    required=True,
    default="xebia.com",
    help="of the blog",
)
@click.argument("image", type=click.Path(dir_okay=False, exists=True), nargs=1)
def main(title, subtitle, author, output, image, overwrite, gradient_magnitude, brand):
    overwrite = overwrite or output
    blog = Blog(title, subtitle, author)
    generate(
        blog,
        in_file=image,
        out_file=output,
        overwrite=overwrite,
        gradient_magnitude=gradient_magnitude,
        brand=brand,
    )
