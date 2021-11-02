# Binx image generator

The binx-og-image-generator is a tool to generate images for your blog.

## Docker
To use docker to generate images follow these steps:

Build the docker image
```console
docker build -t binx-og-image-generator .
```

Generate the images for your blog
```console
docker run -it --rm \
    -v `pwd`:/images \
    -e title="foo" \
    -e subtitle="bar" \
    -e author="binx consultant" \
    -e imagename="banner.jpg" \
    binx-og-image-generator
```

The generated image can be found in `pwd` (current directory)

## Pipenv
If you which to install the binx-og-image-generator on your host machine follow these steps.

### Prerequisites
- Python 3.9
- Pipenv


### Steps to use the OG Image Generator
- pip install pipenv
- pipenv shell
- pipenv install
- binx-og-image-generator banner.jpg --title "foo" --subtitle "bar" --author "binx consultant"

## binx.io og image generator

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

