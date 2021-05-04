FROM python:3.9
WORKDIR /party-bot
COPY . .
RUN pip install --upgrade pip && pip install pipenv && pipenv install --system --deploy --ignore-pipfile
CMD ["python", "main.py"]