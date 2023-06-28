import time
from datetime import datetime as dt

from selenium import webdriver


class Product:
    def __init__(self, name: str, price: float, count: int,
                 is_returned: str, available_count: int) -> None:
        self.name = name
        self.price = price
        self.count = count
        self.is_returned = is_returned
        self.available_count = available_count

    def __repr__(self) -> str:
        return self.display_product_info()

    def display_product_info(self) -> str:
        return (f'\nНазвание продукта: {self.name}\n'
                f'Цена за 1 шт: {self.price}\n'
                f'Количество товара: {self.count}\n'
                f'Был возврат: {self.is_returned}\n'
                f'Доступное количество: {self.available_count}\n')


class Client:
    def __init__(self, name: str, surname: str, country: str,
                 city: str, district: str, phone: str) -> None:
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
    def __init__(self, id: int, code: int, is_a_new_client: bool,
                 delivering_country: str, price: float, payment: str,
                 status: str, date: dt, client: Client,
                 products: list) -> None:
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
                f'Клиент: \n{self.client}\n'
                f'Список продуктов: {str(self.products)}\n')


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
        self.driver = webdriver.Chrome(executable_path='chromedriver.exe',
                                       service_log_path='NULL')
        self.options = webdriver.ChromeOptions()

    def configure_parser(self):
        self.options.add_experimental_option('excludeSwitches',
                                             ['enable-logging'])
        self.options.add_argument('--log-level=3')
        self.options.add_argument('--start-maximized')

    def start_parsing(self) -> Order:
        self.driver.get(self.link)

        assert 'Коровушкино' in self.driver.title
        print('Сайт загрузился!')

        login_email_element = self.driver.find_element_by_css_selector(
            self.MAIN_SELECTORS['login_email_sel']
        )
        login_password_element = self.driver.find_element_by_css_selector(
            self.MAIN_SELECTORS['login_password_sel']
        )
        login_btn_element = self.driver.find_element_by_css_selector(
            self.MAIN_SELECTORS['login_btn_sel']
        )

        login_email_element.send_keys(self.email)
        login_password_element.send_keys(self.password)
        login_btn_element.click()
        time.sleep(5)

        orders_element = self.driver.find_element_by_css_selector(
            self.MAIN_SELECTORS['orders_sel']
        )
        orders_element.click()
        return self.handle_order_info()

    def check_new_order(self, id) -> bool:
        with open('last_order_id.txt', 'r') as file:
            if int(file.readline()) == id:
                return True
        with open('last_order_id.txt', 'w') as file:
            file.write(str(id))
            return False

    def handle_order_info(self) -> Order:
        id: int = int(self.driver.find_element_by_css_selector(
            self.ORDER_SELECTORS['id_sel']
        ).text)

        if self.check_new_order(id) is True:
            return None

        info_array = []

        for i in range(3, 11):
            info_array.append(self.driver.find_element_by_css_selector(
                (self.ORDER_SELECTORS['main_info_sel']).format(i)
            ).text)
        info_array = tuple(info_array)
        (code, new_client, country, client,
         price, payment, status, date) = info_array

        code: int = int(code)
        new_client = True if new_client == 'Да' else False
        price = int(price.replace(' руб.', '').replace(' ', ''))
        date = dt.strptime(date, '%d.%m.%Y %H:%M')

        order_description_element = self.driver.find_element_by_css_selector(
            self.MAIN_SELECTORS['orders_description_sel']
        )
        order_description_element.click()
        client_info = self.handle_client_info()
        product_list = self.handle_products_info()

        order = Order(id, code, new_client, country, price, payment, status,
                      date, client_info, product_list)
        return order

    def handle_client_info(self) -> Client:
        client_info = self.driver.find_element_by_css_selector(
            '#addressShipping > div > div > div:nth-child(1)'
        ).text
        key_words = tuple((client_info.split('\n'))[1:])

        fullname, country, city, district, phone = key_words
        name = fullname.split(' ')[0]
        surname = fullname.split(' ')[1]

        client = Client(name, surname, country, city, district, phone)
        return client

    def handle_products_info(self) -> list:
        product_index = 1
        product_list: list = []

        try:
            while True:
                product_info = []
                for i in range(2, 8):
                    if i != 5:
                        product_info.append(
                            self.driver.find_element_by_css_selector(
                                (f'#orderProducts > tbody > '
                                 'tr:nth-child({product_index}) '
                                 f'> td:nth-child({i})')
                            ).text
                        )
                product_index += 1

                product_info = tuple(product_info)
                (title, price, count, is_returned,
                 available_count) = product_info
                price = int(price.replace(' ', '').replace('руб.', ''))
                count = int(count)
                is_returned = 'да' if is_returned == '1' else 'нет'
                available_count = int(available_count)

                product = Product(title, price, count,
                                  is_returned, available_count)
                product_list.append(product)
        except Exception:
            return product_list

    def return_to_homepage(self):
        back_btn = self.driver.find_element_by_css_selector(
            self.MAIN_SELECTORS['orders_sel']
        )
        back_btn.click()
