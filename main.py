import logging
import os
import time
from datetime import datetime

from dotenv import load_dotenv
from telegram import Bot

from messages import (
    CHECK_TOKENS_START_TEXT, MISSING_TOKENS_TEXT, CHECK_TOKENS_END_TEXT
)
from order_parser import Parser

CURRENT_DATE = datetime.now().__str__().replace(
    ' ', '-'
).replace(':', '-').replace('.', '-')

logging.basicConfig(
    format=u'%(asctime)s, %(levelname)s, %(message)s',
    filemode='w',
    filename=f'logs/log_{CURRENT_DATE}.log',
    level=logging.DEBUG
)

load_dotenv()


TELEGRAM_TOKEN = os.getenv('token')

CMS_LINK = os.getenv('cms_link')

CMS_LOGIN = os.getenv('cms_login')

CMS_PASSWORD = os.getenv('cms_password')


def check_tokens():
    """Проверяет корректность токенов программы"""
    logging.debug(CHECK_TOKENS_START_TEXT)
    for name, value in (
        ('tg_token', TELEGRAM_TOKEN),
        ('cms_link', CMS_LINK),
        ('cms_login', CMS_LOGIN),
        ('cms_password', CMS_PASSWORD)
    ):
        if value is None:
            logging.critical(MISSING_TOKENS_TEXT.format(name))
            return
    logging.debug(CHECK_TOKENS_END_TEXT)


if __name__ == '__main__':
    check_tokens()
    try:
        bot = Bot(TELEGRAM_TOKEN)
        parser = Parser(
            link=CMS_LINK,
            email=CMS_LOGIN,
            password=CMS_PASSWORD
        )

        parser.configure_parser()
        parser.authenticate_parser()
    except Exception as error:
        print('Возникла ошибка: {}'.format(error))
    else:
        while True:
            try:
                parser.driver.refresh()
                order = parser.handle_order_info()
                print(order)
                if order is not None:
                    for chat_id in (539288377, 1258274970, 6192766051):
                        bot.send_message(
                            chat_id=chat_id,
                            text=order.__str__()
                        )
            except Exception as error:
                logging.debug('Возникла ошибка: {}'.format(error))
            finally:
                parser.return_to_homepage()
                time.sleep(10)
