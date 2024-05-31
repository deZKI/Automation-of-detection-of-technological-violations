# Базовый образ
FROM python:3.10-alpine

# Install build tools
RUN apk update && apk add --no-cache \
    build-base \
    gfortran \
    cmake \
    libjpeg-turbo-dev \
    libpng-dev \
    tiff-dev \
    gtk+2.0-dev \
    ffmpeg-dev \
    && rm -rf /var/cache/apk/*

# Upgrade pip, setuptools, and wheel
RUN pip install --upgrade pip setuptools wheel

# Установка рабочей директории в контейнере
WORKDIR /app

# Копирование файлов зависимостей
COPY . /app

# Install Python dependencies
RUN pip install -r requirements.txt

# Делаем entrypoint скрипт исполняемым
RUN chmod +x entrypoint.sh