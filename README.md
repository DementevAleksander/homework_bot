# python_telegram_bot
Проект «Бот-помощник. Уведомление о проверке домашней работы.».

# Описание
В рамках проекта реализовн бот-помощник, который опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы. При обновлении статуса отправляет соответствующее уведомление в Telegram, содержащее информацию из ответа API формата JSON.


# Установка
## 1) Клонировать репозиторий и перейти в него в командной строке:
```
git@github.com:DementevAleksander/homework_bot.git
```
```
cd homework_bot
```
## 2) Cоздать и активировать виртуальное окружение:
```
python -m venv venv
```

```
source venv/Scripts/activate
```

## 3) Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

## 4) Установить актуальные библиотеки:
```
pip install requests
```
```
pip install python-telegram-bot
```
```
pip install python-dotenv
```

## 5) Скорректируйте путь к логам:
```
например, filename='/homework_bot/homework.log',
```

## 6) Создайте файл переменные окружения .env:
```
PRACTICUM_TOKEN= Получить токен можно по адресу: https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a.
```
```
TELEGRAM_TOKEN = в переменной TELEGRAM_TOKEN сохраните токен вашего бота. Получить этот токен можно у бота @BotFather.
```
```
TELEGRAM_CHAT_ID = чтобы бот отправил сообщение именно вам, в переменной TELEGRAM_TO сохраните ID своего телеграм-аккаунта. Узнать свой ID можно у бота @userinfobot;
```

## 7) Запустите бота-помощника:
```
python homework.py
```
