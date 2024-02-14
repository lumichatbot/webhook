FROM python:3.7

# Environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

# Project files and settings
RUN apt-get update && apt-get autoremove -y
RUN pip3 install -U pip setuptools poetry

RUN mkdir /app
COPY . /app/

WORKDIR /app

RUN poetry config virtualenvs.create false
RUN poetry install
RUN python -m spacy download en_core_web_md

CMD gunicorn -w 2 app:app

EXPOSE 80
