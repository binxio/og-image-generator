FROM python:3.9-alpine

WORKDIR /app
ADD ./ /app/

RUN apk add --no-cache g++ gcc musl-dev freetype-dev libffi-dev python3-dev jpeg-dev zlib-dev && \
    python setup.py build install

RUN mkdir /images

WORKDIR /images

CMD ["sh", "-c", "binx-og-image-generator ${imagename} --title \"${title}\" --subtitle \"${subtitle}\" --author \"${author}\""]

