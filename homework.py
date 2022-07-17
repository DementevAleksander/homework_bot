import json
import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


class СustomException(Exception):
    """Кастомное исключение."""
    file_handler = logging.FileHandler(
        'exceptions.log',
        mode='w',
    )
    file_handler.setLevel(logging.ERROR)
    text_format = logging.Formatter('%(asctime)s, %(levelname)s, %(message)s')
    file_handler.setFormatter(text_format)
    logger.addHandler(file_handler)


def send_message(bot, message):
    """Отправка сообщений в TELEGRAM."""
    try:
        logger.info('Началась отправка сообщения в TELEGRAM!')
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
    except telegram.error.TelegramError as error:
        raise СustomException(
            f'Ошибка отправки сообщения в TELEGRAM: {error}!'
        )
    else:
        logger.info('Сообщение в TELEGRAM успешно отправлено!')


def get_api_answer(current_timestamp):
    """Получение информации о домашней работе."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    try:
        logger.info('Началась отправка запроса к Яндекс.Домашка!')
        homework = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params,
        )
        logger.info('Запрос к Яндекс.Домашка успешно отправлен!')
    except requests.exceptions.HTTPError as error:
        raise СustomException(f'Ошибка при запросе к основному API: {error}!')
    except requests.exceptions.Timeout as error:
        raise СustomException(f'Таймаут: {error}')
    except requests.exceptions.ConnectionError as error:
        raise СustomException(f'Ошибка соединения с Яндекс.Домашка: {error}')
    except requests.exceptions.RequestException as error:
        raise СustomException(f'Сбой запроса: {error}')
    if homework.status_code != HTTPStatus.OK:
        status_code = homework.status_code
        raise СustomException(f'Статус не равен 200: {status_code}!')
    try:
        homework_json = homework.json()
        return homework_json
    except json.decoder.JSONDecodeError:
        raise СustomException('Ответ от Яндекс.Домашка не формата JSON!')


def check_response(response):
    """Проверка ответа API на корректность."""
    if not isinstance(response, dict):
        raise TypeError('Ответ от Яндекс.Домашка не является словарём!')

    if 'homeworks' not in response or 'current_date' not in response:
        raise KeyError('Ключ "homeworks" или "current_date" не найдены!')

    list_homeworks = response.get('homeworks')

    if not isinstance(list_homeworks, list):
        raise KeyError(
            'В ответе от API под ключом "homeworks" пришел не список.'
            f' response = {response}.'
        )
    return list_homeworks


def parse_status(homework):
    """Парсер статуса результатов домашней работы."""
    if 'homework_name' not in homework:
        raise KeyError('В ответе не найден ключ "homework_name"!')
    if 'status' not in homework:
        raise СustomException('В ответе не найден ключ "status"!')

    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    if homework_status not in HOMEWORK_STATUSES:
        raise СustomException(f'Статус работы не найден: {homework_status}!')

    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка наличия переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Не найдена переменная окрежения!')
        sys.exit('Не найдена переменная окрежения!')

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    STATUS = ''

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            message = parse_status(homework[0])
            if message != STATUS:
                send_message(bot, message)
                STATUS = message
            current_timestamp = response.get('current_date')
        except Exception as error:
            logger.error(error)
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s, %(levelname)s, %(message)s',
        level=logging.INFO,
        filename='88_YandexPracticum/homework_bot/homework.log',
        filemode='w',
    )
    main()
