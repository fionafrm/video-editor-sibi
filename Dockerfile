FROM python:3.12.8-slim

WORKDIR /app

# Install system dependencies for video processing
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY . .

# Collect static files for production
RUN python manage.py collectstatic --noinput

# --- REMOVE THIS LINE ---
# RUN python manage.py migrate --noinput

EXPOSE 8000

# --- CHANGE YOUR CMD TO THIS ---
# This runs migrate, and *then* runs the server
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"]