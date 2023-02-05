import hashlib
import os
import textwrap
from collections import namedtuple
from io import BytesIO

import click
import numpy as np
import requests
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from .logger import log

data_dir = os.path.dirname(__file__)

Blog = namedtuple("Blog", "title subtitle author email")


class Generator:
    def __init__(
        self,
        author: str,
        title: str,
        subtitle: str,
        gradient_magnitude: float = 0.85,
        email: str = None,
    ):
        self.medium_font = "Ubuntu-M.ttf"
        self.bold_font = "Ubuntu-B.ttf"
        self.logo = Image.open(os.path.join(data_dir, "images", "binx-logo-white.png"))
        self.author = author
        self.email = email
        self.title = title
        self.subtitle = subtitle
        self.gradient_magnitude = gradient_magnitude


class BinxGenerator(Generator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.medium_font = "Ubuntu-M.ttf"
        self.bold_font = "Ubuntu-B.ttf"
        self.logo = Image.open(os.path.join(data_dir, "images", "binx-logo-white.png"))

    def _mask(self, img):
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        width, height = img.size
        gradient = Image.new("L", (width, 1), color=0xFF)
        for x in range(width):
            gradient.putpixel(
                (x, 0), int(255 * (1 - self.gradient_magnitude * float(x) / width))
            )
        alpha = gradient.resize(img.size)
        black_img = Image.new("RGBA", (width, height), color=0)  # i.e. black
        black_img.putalpha(alpha)
        return Image.alpha_composite(img, black_img)

    def _write_title(self, img):
        x, y = (32, 32)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(os.path.join(data_dir, "fonts", self.bold_font), 64)
        width, height = font.getsize(self.title)
        lines = textwrap.wrap(self.title, width=32)
        for line in lines:
            draw.text((x, y), line, font=font, fill=(255, 255, 255))
            y += height

    def _write_subtitle(self, img):
        width, height = img.size
        draw = ImageDraw.Draw(img)
        x, y = (32, int(height * 0.45))
        font = ImageFont.truetype(os.path.join(data_dir, "fonts", self.medium_font), 36)
        width, height = font.getsize(self.subtitle)
        lines = textwrap.wrap(self.subtitle, width=50)
        for line in lines:
            draw.text((x, y), line, font=font, fill=(255, 255, 255))
            y += height

    def _write_author(self, img):
        width, height = img.size
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(os.path.join(data_dir, "fonts", self.medium_font), 36)
        draw.text(
            (32 + 247 + 16, height - 36 - 16 - 32),
            self.author,
            font=font,
            fill=(255, 255, 255),
        )

    def _write_logo(self, img):
        x, y = img.size
        logo_x, logo_y = self.logo.size
        logo = self.logo.resize((247, int(247 / logo_x * logo_y)))
        img.paste(logo, (32, y - 32 - logo.size[1]), logo)

    def generate(self, img):
        img = self._mask(img)
        self._write_logo(img)
        self._write_title(img)
        self._write_subtitle(img)
        self._write_author(img)
        return img


class XebiaGenerator(Generator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.medium_font = "proximanova-medium.ttf"
        self.bold_font = "proximanova-bold.ttf"
        self.logo = Image.open(os.path.join(data_dir, "images", "xebia-logo-white.png"))
        self.overlay = Image.open(
            os.path.join(data_dir, "images", "xebia-overlay-purple.png")
        )
        self.profile_mask = Image.open(
            os.path.join(data_dir, "images", "profile-mask.png")
        ).convert("L")

    def _mask(self, img):
        img.paste(self.overlay, (0, 0), self.overlay)
        return img

    def _write_title(self, img):
        x, y = (75, 140)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(os.path.join(data_dir, "fonts", self.bold_font), 50)
        _, _, width, height = font.getbbox(self.title)
        lines = textwrap.wrap(self.title, width=23)
        for line in lines:
            draw.text((x, y), line, font=font, fill=(255, 255, 255))
            y += height

    def _write_author(self, img):
        width, height = img.size
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(os.path.join(data_dir, "fonts", self.medium_font), 36)
        ascent, descent = font.getmetrics()
        first_name = self.author.split()[0]
        last_name = " ".join(self.author.split()[1:])
        text_width = font.getmask(self.author).getbbox()[2]
        text_height = font.getmask(self.author).getbbox()[3] + descent
        position = (width - 320, height - 170)
        draw.text(
            position,
            first_name,
            font=font,
            fill=(255, 255, 255),
        )

        draw.text(
            (position[0], position[1] + text_height),
            last_name,
            font=font,
            fill=(255, 255, 255),
        )

    def _add_profile_picture(self, img):
        if not self.email:
            return

        url = (
            "https://www.gravatar.com/avatar/"
            + hashlib.md5(self.email.lower().encode("utf8")).hexdigest()
        )

        response = requests.get(
            url, params={"size": self.profile_mask.size[0], "d": "404"}
        )
        if response.status_code != 200:
            log.warning(
                "failed to retrieve profile image for %s, %s",
                self.email,
                response.status_code,
            )
            return

        picture = Image.open(BytesIO(response.content))
        if picture.mode != "RGB":
            picture = picture.convert("RGB")

        rgb = np.array(picture)
        opacity = np.array(self.profile_mask)
        image_array = np.dstack((rgb, opacity))
        final_image = Image.fromarray(image_array).resize(size=(170, 170))

        x, y = img.size
        img.paste(final_image, (x - 532, y - 218), final_image)
        return

    def generate(
        self,
        img,
    ):
        img = self._mask(img)
        self._write_title(img)
        self._write_author(img)

        if self.email:
            self._add_profile_picture(img)

        return img


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
    kwargs = {
        "title": blog.title,
        "subtitle": blog.subtitle,
        "email": blog.email,
        "author": blog.author,
        "gradient_magnitude": gradient_magnitude,
    }
    if brand == "binx.io":
        generator = BinxGenerator(**kwargs)
    else:
        generator = XebiaGenerator(**kwargs)

    img = Image.open(in_file)
    img = resize_image(img)
    img = generator.generate(img)
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
@click.option("--email", required=False, help="of the blog author")
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
def main(
    title, subtitle, author, email, output, image, overwrite, gradient_magnitude, brand
):
    overwrite = overwrite or output
    blog = Blog(title, subtitle, author, email)
    kwargs = {
        "title": title,
        "subtitle": subtitle,
        "email": email,
        "author": author,
        "gradient_magnitude": gradient_magnitude,
    }
    if brand == "binx.io":
        generator = BinxGenerator(**kwargs)
    else:
        generator = XebiaGenerator(**kwargs)

    generate(
        blog,
        in_file=image,
        out_file=output,
        overwrite=overwrite,
        gradient_magnitude=gradient_magnitude,
        brand=brand,
    )
