FROM rasa/rasa:latest-full

USER root

RUN mkdir /app
COPY . /app/
WORKDIR /app

ENTRYPOINT ["rasa", "run", "actions", "--debug"]

EXPOSE 80
