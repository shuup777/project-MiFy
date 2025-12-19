FROM python:3.11-slim

# Set environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static (AMAN walau gagal)
RUN python manage.py collectstatic --noinput || true

CMD ["gunicorn", "mify.wsgi:application", "--bind", "0.0.0.0:8000"]
