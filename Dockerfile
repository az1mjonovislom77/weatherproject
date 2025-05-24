FROM python:3.10-slim

WORKDIR /code

# Sistemaga kerakli paketlar: pg_isready uchun postgresql-client hamda libpq-dev 
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python kutubxonalarini o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyihani konteynerga nusxalash
COPY . .

# Default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
