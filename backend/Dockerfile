# Базовый образ
FROM python:3.10-alpine

# Установка рабочей директории в контейнере
WORKDIR /app

# Копирование файлов зависимостей
COPY . /app
RUN pip install --upgrade pip
RUN pip install setuptools wheel
RUN pip install -r requirements.txt
# Делаем entrypoint скрипт исполняемым
RUN chmod +x entrypoint.sh