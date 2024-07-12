FROM python:3.10-alpine

WORKDIR /app
ADD ./ /app/

RUN apk add --no-cache g++ gcc musl-dev freetype-dev libffi-dev python3-dev jpeg-dev zlib-dev && \
    python setup.py build install

RUN mkdir /images

WORKDIR /images

ENTRYPOINT [ "binx-og-image-generator" ]

