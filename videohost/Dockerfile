FROM python:3.12-alpine

WORKDIR /usr/src/videohost

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk update \
    && apk add --no-cache \
       postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip
COPY ./requirements.txt .

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["sh", "-c", "python3 manage.py collectstatic --noinput && daphne -b 0.0.0.0 -p 8000 videohost.asgi:application"]