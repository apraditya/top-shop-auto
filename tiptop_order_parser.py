from bs4 import BeautifulSoup

class TiptopOrderParser:
    @classmethod
    def from_file(cls, html_file):
        with open(html_file, 'r') as file:
            html_doc = file.read()
        return cls(html_doc)

    def __init__(self, html_doc):
        self.html_doc = html_doc
        self.order_items_table = None
        self.cart_items_list = None
        self.soup = BeautifulSoup(html_doc, 'html.parser')
        self.set_order_items()

    def items_list(self):
        if (self.cart_items_list == None):
            self.cart_items_list = self.soup.find('ul', class_='cart-list')

        return self.cart_items_list

    def items_table(self):
        if (self.order_items_table == None):
            self.order_items_table = self.soup.find('table', class_='table-list')

        return self.order_items_table

    def set_cart_items(self):
        self.cart_items = self.collect_cart_items()

    def set_order_items(self):
        self.order_items = self.collect_order_items()
        if (len(self.order_items) == 0):
            self.order_items = self.collect_cart_items()

    def collect_cart_items(self):
        list = self.items_list()
        if list is None:
            return []

        list_items = list.find_all('li')

        items = []
        for index, list_item in enumerate(list_items, start=1):
            name = list_item.find('h6').text
            size = list_item.find('span', class_='text-green-cart').text

            price_text = list_item.find('p', class_='text-danger').text
            price = self._get_money(price_text)

            sub_total_text = list_item\
            .find('div', class_='cart-action-group')\
            .find('h6').text
            sub_total = self._get_money(sub_total_text)

            quantity = int(sub_total / price)
            item = {
                'no': index,
                'name': name,
                'size': size,
                'quantity': quantity,
                'price': price
            }
            items.append(item)  # Use append instead of push
        return items

    def collect_order_items(self):
        table = self.items_table()
        if table is None:
            return []

        rows = table.tbody.find_all('tr') if table.tbody else []

        items = []
        for row in rows:
            text_cols = row.find_all('h6')
            if len(text_cols) >= 5:  # Ensure there are at least 5 columns
                item = {
                    'no': text_cols[0].text,
                    'name': text_cols[1].text,
                    'size': text_cols[2].text,
                    'quantity': text_cols[4].text,
                    'price': text_cols[3].text
                }
                items.append(item)  # Use append instead of push
        return items

    def _get_money(self, text):
        return int(text.split(' ')[1].replace(',', ''))
