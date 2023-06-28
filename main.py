import os
import time

from cryptography.fernet import Fernet
from dotenv import load_dotenv
from telegram import Bot

from order_parser import Parser


def generate_access_key():
    key = Fernet.generate_key()
    with open('file.key', 'wb') as file:
        file.write(key)


def encrypte_private_data(file_name: str):
    with open('file.key', 'rb') as file_key:
        key = file_key.read()
    fernet = Fernet(key)

    with open(file_name, 'rb') as private_data:
        original_data = private_data.read()

    encrypte_data = fernet.encrypt(original_data)

    with open(file_name, 'wb') as private_data:
        private_data.write(encrypte_data)


def decrypte_private_data(file_name: str) -> list:
    with open('file.key', 'rb') as file_key:
        key = file_key.read()
    fernet = Fernet(key)

    with open(file_name, 'rb') as private_data:
        encrypte_data = private_data.read()

    decrypte_data: str = str(fernet.decrypt(encrypte_data)).replace('\'', '')
    return reformat_private_data(decrypte_data)


def reformat_private_data(data: str) -> list:
    reformatted_data = []
    first_index = 1

    for i in range(1, len(data)):
        if (data[i - 1] == '\\' and data[i] == 'n'):
            reformatted_data.append(data[first_index:i-3])
            first_index = i + 1
        elif i == len(data) - 1:
            reformatted_data.append(data[first_index:])
    return reformatted_data


if __name__ == '__main__':
    load_dotenv()
    # encrypte_private_data('private_data.txt') #Do not uncomment this line!
    private_data = decrypte_private_data('private_data.txt')
    TOKEN = os.getenv('token')
    CHAT_ID = os.getenv('chat_id')

    bot = Bot(TOKEN)
    bot.send_message(chat_id=os.getenv('chat_id'), text='Привет!')
    parser = Parser(
        link=private_data[0],
        email=private_data[1],
        password=private_data[2]
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
