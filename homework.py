import os
import time
import requests
import logging
import telegram

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s, %(levelname)s, %(message)s',
    level=logging.INFO,
    filename='main.log',
    filemode='w',
)
logger = logging.getLogger(__name__)
logger.addHandler(
    logging.StreamHandler()
)


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


def send_message(bot, message):
    """Отправка сообщений в TELEGRAM."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
    except Exception:
        logger.error('Ошибка отправки сообщения в TELEGRAM!')


def get_api_answer(current_timestamp):
    """Получение информации о домашней работе."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}

    try:
        homework = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params,
        )
        logger.info('Запрос к серверу Яндекс.Домашка.')
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}!')
        raise Exception(f'Ошибка при запросе к основному API: {error}!')
    if homework.status_code != 200:
        status_code = homework.status_code
        logging.error(f'Статус не равен 200: {status_code}!')
        raise Exception(f'Статус не равен 200: {status_code}!')
    try:
        return homework.json()
    except ValueError:
        logger.error('Ошибка обработки ответа от Яндекс.Домашка!')
        raise ValueError('Ошибка обработки ответа от Яндекс.Домашка!')


def check_response(response):
    """Проверка ответа API на корректность."""
    if type(response) is not dict:
        raise TypeError('Ответ от Яндекс.Домашка не является словарём!')
    try:
        list_homeworks = response.get('homeworks')
    except KeyError:
        logger.error('Ключ "homeworks" не найден!')
        raise KeyError('Ключ "homeworks" не найден!')
    try:
        homework = list_homeworks[0]
    except IndexError:
        logger.error('Домашняя работа не найдена!')
        raise IndexError('Домашняя работа не найдена!')
    return homework


def parse_status(homework):
    """Парсер статуса результатов домашней работы."""
    if 'homework_name' not in homework:
        raise KeyError('В ответе не найден ключ "homework_name"!')
    if 'status' not in homework:
        raise Exception('В ответе не найден ключ "status"!')

    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    if homework_status not in HOMEWORK_STATUSES:
        raise Exception(f'Статус работы не определён: {homework_status}!')

    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        return True
    else:
        return False


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    STATUS = ''

    if not check_tokens():
        logger.critical('На найдена переменная окрежения!')
        raise Exception('На найдена переменная окрежения!')

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            message = parse_status(homework)
            if message != STATUS:
                send_message(bot, message)
                STATUS = message
            current_timestamp = response.get('current_date')
            time.sleep(RETRY_TIME)
        except Exception as error:
            logger.error(error)
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)
        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
