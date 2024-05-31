# Базовый образ
FROM python:3.10-alpine


# Install build tools
RUN apt-get update && apt-get install -y \
    build-essential \
    gfortran \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, and wheel
RUN pip install --upgrade pip setuptools wheel

# Установка рабочей директории в контейнере
WORKDIR /app

# Копирование файлов зависимостей
COPY . /app
RUN pip install --upgrade pip
RUN pip install setuptools wheel
RUN pip install -r requirements.txt
# Делаем entrypoint скрипт исполняемым
RUN chmod +x entrypoint.sh