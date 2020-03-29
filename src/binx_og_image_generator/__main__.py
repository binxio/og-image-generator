import click
from binx_og_image_generator.generator import generate


@click.command(help="generate an og image for blog")
@click.option("--title", required=True, help="of the blog")
@click.option("--subtitle", required=True, help="of the blog")
@click.option("--author", required=True, help="of the blog")
@click.option("--output", required=True, help='filename of the image')
@click.argument("image", type=click.Path(dir_okay=False, exists=True), nargs=1)
def main(title, subtitle, author, output, image):
    generate(in_file=image, out_file=output, title=title,subtitle=subtitle, author=author)


if __name__ == "__main__":
    main()
