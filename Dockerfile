# syntax=docker/dockerfile:1
FROM python:3.7.12-buster
RUN apt-get update && apt-get -y dist-upgrade
RUN apt install -y netcat

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV POSTGRES_NAME=postgres
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_HOST=db

# Copy project
RUN mkdir -p /opt/chatApplication
WORKDIR /opt/chatApplication

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD ./entrypoint.sh ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]