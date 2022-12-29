ARG BASE_IMAGE=docker.io/library/python:3.11-slim-bullseye
FROM $BASE_IMAGE

WORKDIR /burgertunes

COPY main requirements.txt /burgertunes/
COPY static /burgertunes/static
COPY templates /burgertunes/templates

RUN pip install -r requirements.txt

RUN mkdir /burgertunes/static/cache
COPY config.ini /burgertunes/

CMD ["python", "main"]
EXPOSE 8080
