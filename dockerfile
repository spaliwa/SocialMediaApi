FROM python:3.10.14-alpine3.20
WORKDIR /social_media_app
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
COPY requirements.txt requirements.txt
RUN    pip install -r requirements.txt
COPY . /social_media_app

