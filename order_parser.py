import time
import logging


from datetime import datetime as dt
from messages import (
    CONFIG_PARSER_START_TEXT, CONFIG_PARSER_END_TEXT,
    PARSER_AUTHENTICATION_START_TEXT, PARSER_OPEN_LINK_TEXT,
    PARSER_ENTER_TEXT, PARSER_AUTHENTICATION_END_TEXT,
    CHECK_ORDER_EXISTANCE_TEXT, PARSING_PRODCUTS_START_TEXT,
    HANDLING_CODE_TEXT, HANDLING_NEW_CLINET_TEXT, HANDLING_PRICE_TEXT,
    HANDLING_DATE_TEXT, PARSING_ORDER_INFO_START_TEXT,
    CHECK_ORDER_EXISTANCE_RESULT_TEXT, PARSING_MAIN_INFO_START_TEXT,
    ORDER_READY_TEXT, PARSING_CLIENT_INFO_START_TEXT,
    PARSING_CLIENT_INFO_END_TEXT, GO_TO_HOMEPAGE_TEXT,
    PARSING_PRODUCT_END_TEXT
)

from selenium import webdriver


class Product:
    def __init__(
        self, name: str, price: float, count: int, available_count: int
    ) -> None:
        self.name = name
        self.price = price
        self.count = count
        self.available_count = available_count

    def __repr__(self) -> str:
        return self.display_product_data()

    def display_product_data(self) -> str:
        return (f'\n{self.name}\n'
                f'Цена за 1 шт: {self.price}\n'
                f'Количество товара: {self.count}\n'
                f'Доступное количество: {self.available_count}\n')


class Client:
    def __init__(
        self, name: str, surname: str, country: str,
        city: str, district: str, phone: str
    ) -> None:
        self.name = name
        self.surname = surname
        self.country = country
        self.city = city
        self.district = district
        self.phone = phone

    def __str__(self) -> str:
        return self.display_client_info()

    def display_client_info(self) -> str:
        return (f'Имя: {self.name}\n'
                f'Фамилия: {self.surname}\n'
                f'Страна: {self.country}\n'
                f'Город: {self.city}\n'
                f'Адрес: {self.district}\n'
                f'Телефон: {self.phone}\n')


class Order:
    def __init__(
        self, id: int, code: int, is_a_new_client: bool,
        delivering_country: str, price: float, payment: str,
        status: str, date: dt, client: Client,
        products: list
    ) -> None:
        self.id = id
        self.code = code
        self.is_a_new_client = is_a_new_client
        self.delivering_country = delivering_country
        self.price = price
        self.payment = payment
        self.status = status
        self.date = date
        self. client = client
        self.products = products

    def __str__(self) -> str:
        return self.display_order_info()

    def display_order_info(self) -> str:
        return (f'Заказ №{self.id}\n'
                f'Дата заказа: {self.date}\n'
                f'Код: {self.code}\n'
                f'Страна доставки: {self.delivering_country}\n'
                f'К оплате: {self.price}\n'
                f'Способ оплаты: {self.payment}\n'
                f'Статус заказа: {self.status}\n\n'
                f'Клиент: \n{self.client.__str__()}\n'
                f'Список продуктов: {str(self.products.__repr__())}\n')


class Parser:
    MAIN_SELECTORS = {
        'login_email_sel': '#email',
        'login_password_sel': '#passwd',
        'orders_sel': '#subtab-AdminParentOrders > a',
        'login_btn_sel': '#submit_login',
        'orders_description_sel': '#table-order > tbody > tr:nth-child(1)'
    }

    ORDER_SELECTORS = {
        'id_sel': ('#table-order > tbody > tr:nth-child(1) > '
                   'td.pointer.fixed-width-xs.text-center'),
        'main_info_sel': ('#table-order > tbody > tr:nth-child(1) > '
                          'td:nth-child({})'),
    }

    def __init__(self, link: str, email: str, password: str) -> None:
        self.link = link
        self.email = email
        self.password = password
        self.driver = webdriver.Chrome(
            executable_path='chromedriver.exe',
            service_log_path='logs/chromedriver'
        )
        self.options = webdriver.ChromeOptions()

    def configure_parser(self) -> None:
        logging.debug(CONFIG_PARSER_START_TEXT)
        self.options.add_experimental_option('excludeSwitches',
                                             ['enable-logging'])
        self.options.add_argument('--log-level=3')
        self.options.add_argument('--start-maximized')
        logging.debug(CONFIG_PARSER_END_TEXT)

    def authenticate_parser(self) -> None:
        """Выполняет аутентификацию в CMS системе"""
        logging.debug(PARSER_AUTHENTICATION_START_TEXT)
        self.driver.get(self.link)
        logging.debug(PARSER_OPEN_LINK_TEXT)
        time.sleep(5)

        login_email_element = self.driver.find_element_by_css_selector(
            self.MAIN_SELECTORS['login_email_sel']
        )
        login_password_element = self.driver.find_element_by_css_selector(
            self.MAIN_SELECTORS['login_password_sel']
        )
        login_btn_element = self.driver.find_element_by_css_selector(
            self.MAIN_SELECTORS['login_btn_sel']
        )
        time.sleep(5)

        logging.debug(PARSER_ENTER_TEXT)
        login_email_element.send_keys(self.email)
        login_password_element.send_keys(self.password)
        login_btn_element.click()
        logging.debug(PARSER_AUTHENTICATION_END_TEXT)
        time.sleep(5)

    def check_new_order(self, id: int) -> bool:
        logging.debug(CHECK_ORDER_EXISTANCE_TEXT)
        with open('last_order_id.txt', 'r') as file:
            if int(file.readline()) == id:
                print('True')
                return True
        with open('last_order_id.txt', 'w') as file:
            file.write(str(id))
            print('False')
            return False

    def validate_orders_info(self, code: str, new_client: str,
                             price: str, date: str) -> tuple:
        logging.debug(HANDLING_CODE_TEXT)
        code = int(code)

        logging.debug(HANDLING_NEW_CLINET_TEXT)
        if new_client.lower() != 'да' and new_client.lower() != 'нет':
            raise Exception('ошибка валидации ячейки нового клиента')
        new_client = True if new_client == 'Да' else False

        logging.debug(HANDLING_PRICE_TEXT)
        if not price.isalnum:
            raise Exception('ошибка валидации ячейки цены')
        price = int(price.replace(' руб.', '').replace(' ', ''))

        logging.debug(HANDLING_DATE_TEXT)
        date = dt.strptime(date, '%d.%m.%Y %H:%M')

        return (code, new_client, price, date)

    def handle_order_info(self) -> Order:
        logging.debug(PARSING_ORDER_INFO_START_TEXT)
        orders_element = self.driver.find_element_by_css_selector(
            self.MAIN_SELECTORS['orders_sel']
        )
        orders_element.click()
        id: int = int(
            self.driver.find_element_by_css_selector(
                self.ORDER_SELECTORS['id_sel']
            ).text
        )
        if self.check_new_order(id):
            return None
        logging.debug(CHECK_ORDER_EXISTANCE_RESULT_TEXT.format('не найден'))

        logging.debug(PARSING_MAIN_INFO_START_TEXT)
        orders_data = []
        for i in range(3, 11):
            orders_data.append(
                self.driver.find_element_by_css_selector(
                    self.ORDER_SELECTORS['main_info_sel'].format(i)
                ).text
            )

        orders_data = tuple(orders_data)
        (code, new_client, country, client,
         price, payment, status, date) = orders_data
        (code, new_client,
         price, date) = self.validate_orders_info(
            code, new_client, price, date
        )

        order_description_element = self.driver.find_element_by_css_selector(
            self.MAIN_SELECTORS['orders_description_sel']
        )
        order_description_element.click()
        client_info = self.handle_client_info()
        product_list = self.handle_products_info()

        order = Order(
            id, code, new_client, country, price, payment, status,
            date, client_info, product_list
        )
        logging.debug(ORDER_READY_TEXT)
        return order

    def handle_client_info(self) -> Client:
        logging.debug(PARSING_CLIENT_INFO_START_TEXT)
        client_info = self.driver.find_element_by_css_selector(
            '#addressShipping > div > div > div:nth-child(1)'
        ).text
        key_words = tuple((client_info.split('\n'))[1:])
        if len(key_words) == 4:
            fullname, country, city, district = key_words
            phone = '-'
        else:
            fullname, country, city, district, phone = key_words
        name = fullname.split(' ')[0]
        surname = fullname.split(' ')[1]

        client = Client(name, surname, country, city, district, phone)
        logging.debug(PARSING_CLIENT_INFO_END_TEXT)
        return client

    def handle_products_info(self) -> list:
        logging.debug(PARSING_PRODCUTS_START_TEXT)
        product_index = 1
        product_list: list = []

        try:
            while True:
                product_data = []
                for i in range(2, 6):
                    product_data.append(
                        self.driver.find_element_by_css_selector(
                            (f'#orderProducts > tbody > '
                                f'tr:nth-child({product_index}) '
                                f'> td:nth-child({i})')
                        ).text
                    )
                product_index += 1
                product_data = tuple(product_data)
                (title, price, count, available_count) = product_data
                print(product_data)
                price = price.replace(' ', '').replace('руб.', '')
                count = count
                available_count = available_count

                product = Product(title, price, count, available_count)
                product_list.append(product)
        except Exception as error:
            logging.debug(error)
            return product_list
        logging.debug(PARSING_PRODUCT_END_TEXT)

    def return_to_homepage(self) -> None:
        logging.debug(GO_TO_HOMEPAGE_TEXT)
        back_btn = self.driver.find_element_by_css_selector(
            self.MAIN_SELECTORS['orders_sel']
        )
        back_btn.click()
