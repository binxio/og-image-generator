# Binx image generator

The binx-og-image-generator is a tool to generate images for your blog.

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


To generate an images, type:

```console
docker run --rm \
    -v $PWD:$PWD \
    -w $PWD \
    ghcr.io/binxio/og-image-generator \
    --title "foo" \
    --subtitle "bar" \
    --author "binx consultant" \
    ./banner.jpg
```

The generated image can be found in your current directory and is named `og-banner.jpg`.

## Pipenv
If you which to install the binx-og-image-generator on your host machine follow these steps.

### Prerequisites
- Python 3.9
- Pipenv


### Steps to use the OG Image Generator
- pip install pipenv
- pipenv shell
- pipenv install
- binx-og-image-generator --title "foo" --subtitle "bar" --author "binx consultant" banner.jpg

