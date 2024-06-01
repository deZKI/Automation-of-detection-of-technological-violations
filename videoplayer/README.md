### VIDEOPLAYER

### Requirements

Python 3.9!!!

```sh
brew install python-tk@3.9
``` 

### Установка виртуального окружения

#### Windows

```sh
python3.9 -m venv venv
venv\Scripts\activate
``` 

#### macOS and Linux

```sh
python3.9 -m venv venv
source venv/bin/activate
``` 

### Установка библиотек окружения

```sh
pip install -r requirements.txt
``` 

### Запуск

Поправьте .env в соответствие с адресом сервера

```sh
python main.py
```