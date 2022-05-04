FROM python:3.10-slim

WORKDIR /src
COPY ./requirements.txt .
COPY ./release_bot/ .

RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["python3", "bot.py"]