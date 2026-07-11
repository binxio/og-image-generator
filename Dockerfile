FROM python:3.13-alpine

WORKDIR /app
ADD ./ /app/

RUN apk add --no-cache g++ gcc musl-dev freetype-dev libffi-dev python3-dev jpeg-dev zlib-dev && \
    mkdir /images && \
    python3 -m ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools build && \
    pip3 install .

WORKDIR /images

ENTRYPOINT [ "binx-og-image-generator" ]

