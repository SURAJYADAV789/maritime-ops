FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "until nc -z db 5432; do echo 'Waiting for DB...'; sleep 2; done && python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"]