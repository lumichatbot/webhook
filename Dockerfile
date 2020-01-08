FROM python:3.6

# Environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

# Project files and settings
RUN apt-get update && apt-get autoremove -y
RUN pip3 install -U pip setuptools && pip3 install pipenv

RUN mkdir /app
COPY . /app/

WORKDIR /app

RUN pipenv install --deploy --system
RUN python -m spacy download en_core_web_sm
RUN python -m nltk.downloader wordnet

CMD gunicorn -w 3 app:app

EXPOSE 80
