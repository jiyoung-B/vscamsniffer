FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    portaudio19-dev \
    python3-dev \
    libasound-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/

COPY .env /app/.env

RUN python manage.py collectstatic --noinput

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "corkagefree.asgi:application"]


