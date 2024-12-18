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
        self.soup = BeautifulSoup(html_doc, 'html.parser')
        self.set_order_items()

    def items_table(self):
        if (self.order_items_table == None):
            self.order_items_table = self.soup.find('table', class_='table-list')

        return self.order_items_table

    def set_order_items(self):
        self.order_items = self.collect_order_items()

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
