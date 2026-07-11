import os
import textwrap
from collections import namedtuple
import typing

import click
from PIL import Image, ImageDraw, ImageFont

from binx_og_image_generator.logger import log
from binx_og_image_generator.gravatar import load_profile_picture
from binx_og_image_generator.themes import Theme, THEMES

data_dir = os.path.dirname(__file__)

Blog = namedtuple("Blog", "title subtitle author email")


class Generator:
    def __init__(
        self,
        author: str,
        title: str,
        subtitle: str,
        gradient_magnitude: float = 0.85,
        email: str | None = None,
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
    """Generates OpenGraph banner with Xebia branding"""

    """General content padding"""
    __PADDING = 40

    """Logo area width"""
    __LOGO_WIDTH = 100

    """Gravatar block """
    __PROFILE_PIC_WIDTH = 100

    """Author block with optional Gravatar"""
    __AUTHOR_BLOCK = {"x": __PADDING, "y": __PADDING}

    def __init__(self, *, theme: Theme, **kwargs):
        """ """
        super().__init__(**kwargs)

        self.theme = theme

        self._image_mask = Image.open(theme.banner_mask).convert("L")
        self._profile_mask = Image.open(theme.profile_mask).convert("L")

        self.profile_mask = Image.open(
            os.path.join(data_dir, "images", "profile-mask.png")
        ).convert("L")

        [profile_width, _] = self._profile_mask.size
        self.profile_picture: Image.Image | None = load_profile_picture(
            self.email, profile_width
        )

    def generate(self, img):
        """ """

        self.__result = Image.new("RGB", img.size, self.theme.background_color)

        canvas = ImageDraw.Draw(self.__result)
        title_position = self.__render_author(canvas)
        self.__write_title(canvas, title_position)
        self.__render_footer(canvas)
        self.__paste_image(img)

        return self.__result

    @property
    def content_block_width(self) -> int:
        """ """
        [w, _] = self.__result.size
        [mask_w, _] = self._image_mask.size
        return int(w - mask_w - self.__PADDING * 1.75)

    def __render_author(self, canvas: ImageDraw.ImageDraw) -> typing.Tuple[int, int]:
        """Renders blog post author block with optinal Gravatar image

        Returns a tuple with coordinates to render next block
        """

        font = ImageFont.truetype(self.theme.normal_font, 26)
        _, descent = font.getmetrics()
        first_name = self.author.split()[0]
        last_name = " ".join(self.author.split()[1:])
        text_height = font.getmask(self.author).getbbox()[3] + descent

        xy = self.__AUTHOR_BLOCK.copy()

        if self.profile_picture:
            self.__result.paste(
                self.profile_picture.resize(
                    size=(self.__PROFILE_PIC_WIDTH, self.__PROFILE_PIC_WIDTH)
                ),
                (xy["x"], xy["y"]),
                self._profile_mask,
            )

            xy["x"] += int(self.__PROFILE_PIC_WIDTH + self.__PADDING * 0.5)
            xy["y"] += int(self.__PROFILE_PIC_WIDTH * 0.5 - text_height)

        first_name = self.author.split()[0]
        last_name = " ".join(self.author.split()[1:])
        text_height = font.getmask(self.author).getbbox()[3] + descent

        canvas.text(
            (xy["x"], xy["y"]), first_name, font=font, fill=self.theme.text_color
        )

        canvas.text(
            (xy["x"], xy["y"] + text_height),
            last_name,
            font=font,
            fill=self.theme.text_color,
        )

        sx = self.__AUTHOR_BLOCK["x"]
        sy = self.__PROFILE_PIC_WIDTH + self.__PADDING * 1.5
        ex = self.content_block_width
        canvas.line(xy=(sx, sy, ex, sy), fill=self.theme.border_color, width=1)

        return (self.__PADDING, int(self.__PROFILE_PIC_WIDTH + self.__PADDING * 2.25))

    def __write_title(self, canvas, position):
        """ """
        x, y = position
        font = ImageFont.truetype(self.theme.bold_font, 48)
        _, _, _, height = font.getbbox(self.title)
        lines = textwrap.wrap(self.title, width=25)
        for line in lines:
            canvas.text((x, y), line, font=font, fill=self.theme.text_color)
            y += height * 1.25

    def __render_footer(self, canvas: ImageDraw.ImageDraw):
        """Renders footer with deviders, logo and brand moto"""

        [_, h] = self.__result.size
        [logo_w, logo_h] = self.__paste_logo()

        # Line, to the right from the logo
        sx = self.__LOGO_WIDTH + self.__PADDING * 1.5
        sy = h - logo_h - self.__PADDING
        ey = h - self.__PADDING
        canvas.line([sx, sy, sx, ey], self.theme.border_color, 1)

        # Line, above the logo
        sx = self.__PADDING
        sy = int(h - logo_h - self.__PADDING * 1.5)
        ex = self.content_block_width
        canvas.line([sx, sy, ex, sy], self.theme.border_color, 1)

        # Text
        font = ImageFont.truetype(self.theme.bold_font, 16)
        x = logo_w + self.__PADDING * 2
        y = h - self.__PADDING - logo_h * 0.65
        canvas.text(
            xy=(x, y),
            text="Shaping Tomorrow with AI Today",
            font=font,
            fill=self.theme.text_color,
        )

    def __paste_image(self, img):
        """Pastes post image into the resulting banner"""

        [w, _] = img.size
        [crop_w, crop_h] = self._image_mask.size
        paste_x = w - crop_w - self.__PADDING
        self.__result.paste(
            img.crop((0, 0, crop_w, crop_h)),
            (paste_x, self.__PADDING),
            self._image_mask,
        )

    def __paste_logo(self) -> typing.Tuple[int, int]:
        """ """

        [_, h] = self.__result.size

        logo = Image.open(self.theme.logo).convert("RGBA")
        [logo_w, logo_h] = logo.size
        resize_h = int(logo_h * self.__LOGO_WIDTH / logo_w)

        logo = logo.resize((self.__LOGO_WIDTH, resize_h), Image.Resampling.BOX)
        self.__result.paste(logo, (self.__PADDING, h - self.__PADDING - resize_h), logo)

        return (self.__LOGO_WIDTH, resize_h)


def resize_image(image: Image.Image) -> Image.Image:
    """
    resize the image to be the perfect og image size: 1200x630px
    """
    width, height = image.size
    if height < 630:
        log.info("resizing to maximum height of 630px")
        new_width = int(width * (630 / height))
        image = image.resize((width, 630))
        width, height = image.size

    if width < 1200:
        new_height = int(height * 1200 / width)
        log.info("resizing %dx%d to %dx%d", width, height, 1200, new_height)
        image = image.resize((1200, new_height))
        width, height = image.size

    if height > 630 or width > 1200:
        log.info("cropping %dx%d to 1200x630", width, height)
        top = int((height - 630) / 2)
        left = int(width - 1200/ 2)
        image = image.crop((left, top, left+1200, top+630))

    return image


def generate(
    blog: Blog,
    in_file: str,
    out_file: str,
    overwrite: bool = False,
    gradient_magnitude: float = 0.9,
    brand: str = "xebia.com",
    theme: str = "xebia-dark",
):
    kwargs = {
        "title": blog.title,
        "subtitle": blog.subtitle,
        "email": blog.email,
        "author": blog.author,
        "gradient_magnitude": gradient_magnitude,
        "theme": THEMES[theme],
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
@click.option("--theme", type=str, default="xebia-dark", help="of the Xebia branding")
@click.argument("image", type=click.Path(dir_okay=False, exists=True), nargs=1)
def main(
    title,
    subtitle,
    author,
    email,
    output,
    image,
    overwrite,
    gradient_magnitude,
    brand,
    theme,
):
    overwrite = overwrite or output
    blog = Blog(title, subtitle, author, email)

    generate(
        blog,
        in_file=image,
        out_file=output,
        overwrite=overwrite,
        gradient_magnitude=gradient_magnitude,
        brand=brand,
        theme=theme,
    )
