# Базовый образ
FROM python:3.10-alpine

# Установка рабочей директории в контейнере
WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    gfortran \
    cmake \
    && rm -rf /var/lib/apt/lists/* \
RUN pip install numpy

# Копирование файлов зависимостей
COPY . /app
RUN pip install --upgrade pip
RUN pip install setuptools wheel
RUN pip install -r requirements.txt
# Делаем entrypoint скрипт исполняемым
RUN chmod +x entrypoint.sh