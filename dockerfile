# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /home/joao_nishimoto/docker-test

COPY requirements.txt requirements.txt

RUN apt-get -y update
RUN python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5000

CMD python web-server-teste.py
