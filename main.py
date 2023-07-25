import os
import time
import logging
import sys

from dotenv import load_dotenv
from telegram import Bot
from datetime import datetime

from order_parser import Parser
from messages import *

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

CHAT_ID = os.getenv('chat_id')

CMS_LINK = os.getenv('cms_link')

CMS_LOGIN = os.getenv('cms_login')

CMS_PASSWORD = os.getenv('cms_password')


def check_tokens():
    """Проверяет корректность токенов программы"""
    logging.debug(CHECK_TOKENS_START_TEXT)
    for name, value in (
        ('tg_token', TELEGRAM_TOKEN),
        ('chat_id', CHAT_ID),
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

    bot = Bot(TELEGRAM_TOKEN)
    parser = Parser(
        link=CMS_LINK,
        email=CMS_LOGIN,
        password=CMS_PASSWORD
    )
    
    parser.configure_parser()
    order = parser.start_parsing()

    while True:
        try:
            parser.driver.refresh()
            if order is not None:
                bot.send_message(
                    chat_id=CHAT_ID,
                    text=order.__str__()
                )
        except Exception as error:
            print('Возникла ошибка: {}'.format(error))
        finally:
            print('#############')
            parser.return_to_homepage()
            time.sleep(10)
