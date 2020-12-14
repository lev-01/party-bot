FROM python:latest

WORKDIR /usr/src/bot

RUN apt-get update && apt-get upgrade -y

RUN pip3 install --upgrade pip
RUN pip3 install pipenv

COPY . /usr/src/bot

RUN pipenv install --system

CMD ["python3", "bot.py"]
