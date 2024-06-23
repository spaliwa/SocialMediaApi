FROM python:3.10.14-alpine3.20
WORKDIR /social_media_app
COPY requirements.txt requirements.txt
RUN    pip install -r requirements.txt
COPY . /social_media_app

