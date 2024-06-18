FROM python:3.9-slim-bullseye

WORKDIR /app

COPY requirements.txt requirements.txt
COPY requirements/* requirements/

RUN apt-get update
RUN apt-get install -y default-libmysqlclient-dev build-essential &&\
    python -m pip install --upgrade pip &&\
    python -m pip install -r requirements.txt

COPY . .

CMD ["sh", "gunicorn_start.sh"]

EXPOSE 80