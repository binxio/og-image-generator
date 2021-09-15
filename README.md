# Prerequisites
- Python 3.9
- Pipenv


# Steps to use the OG Image Generator
- pip install pipenv
- pipenv shell
- pipenv install
- binx-og-image-generator banner.jpg --title "foo" --subtitle "bar" --author "binx consultant"

# binx.io og image generator

utility to generate the binx.io social image for a blog.

```
Usage: binx-og-image-generator [OPTIONS] IMAGE

  generate an og image for blog

Options:
  --title TEXT     of the blog  [required]
  --subtitle TEXT  of the blog  [required]
  --author TEXT    of the blog  [required]
  --output TEXT    filename of the image  [required]
  --help           Show this message and exit.
```
