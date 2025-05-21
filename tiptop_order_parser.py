from bs4 import BeautifulSoup

class TiptopOrderParser:
    @classmethod
    def from_file(cls, html_file):
        try:
            with open(html_file, 'r', encoding='utf-8') as file: # Added encoding
                html_doc = file.read()
            return cls(html_doc)
        except FileNotFoundError:
            print(f"Error: Order file not found at {html_file}")
            return cls("") # Return an empty parser instance
        except Exception as e:
            print(f"Error reading order file {html_file}: {e}")
            return cls("") # Return an empty parser instance


    def __init__(self, html_doc):
        self.html_doc = html_doc
        self.order_items_table = None
        self.cart_items_list = None
        self.soup = BeautifulSoup(html_doc, 'html.parser')
        self.order_items = [] # Initialize order_items list
        if html_doc: # Only try to parse if html_doc is not empty
            self.set_order_items()
            print(f"TiptopOrderParser: Initialized and parsed. Found {len(self.order_items)} items.")
        else:
            print("TiptopOrderParser: Initialized with empty document.")


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
            print("TiptopOrderParser: No items found in order table, attempting to parse as cart items.")
            self.order_items = self.collect_cart_items()
            if (len(self.order_items) == 0):
                 print("TiptopOrderParser: No items found in cart list either.")

    def collect_cart_items(self):
        list = self.items_list()
        if list is None:
            print("TiptopOrderParser: No cart list element found.")
            return []

        list_items = list.find_all('li')
        print(f"TiptopOrderParser: Found {len(list_items)} potential cart list items.")

        items = []
        for index, list_item in enumerate(list_items, start=1):
            try: # Added error handling for parsing individual items
                name_tag = list_item.find('h6')
                size_tag = list_item.find('span', class_='text-green-cart')
                price_tag = list_item.find('p', class_='text-danger')
                sub_total_div = list_item.find('div', class_='cart-action-group')

                if not all([name_tag, size_tag, price_tag, sub_total_div]):
                    print(f"TiptopOrderParser: Warning: Skipping cart item {index} due to missing elements.")
                    continue

                name = name_tag.text.strip()
                size = size_tag.text.strip()

                price_text = price_tag.text.strip()
                price = self._get_money(price_text)

                sub_total_tag = sub_total_div.find('h6')
                if not sub_total_tag:
                     print(f"TiptopOrderParser: Warning: Skipping cart item {index} due to missing subtotal element.")
                     continue

                sub_total_text = sub_total_tag.text.strip()
                sub_total = self._get_money(sub_total_text)

                # Avoid division by zero if price is 0
                quantity = int(sub_total / price) if price > 0 else 0

                item = {
                    'no': index,
                    'name': name,
                    'size': size,
                    'quantity': quantity,
                    'price': price
                }
                items.append(item)
                print(f"TiptopOrderParser: Parsed cart item {index}: {item['name']} ({item['size']}) x{item['quantity']}")
            except Exception as e:
                print(f"TiptopOrderParser: Error parsing cart item {index}: {e}. Skipping item.")

        return items

    def collect_order_items(self):
        table = self.items_table()
        if table is None:
            print("TiptopOrderParser: No order table element found.")
            return []

        rows = table.tbody.find_all('tr') if table and table.tbody else [] # Added check for table
        print(f"TiptopOrderParser: Found {len(rows)} potential order table rows.")

        items = []
        for row in rows:
            try: # Added error handling for parsing individual items
                text_cols = row.find_all('h6')
                # Ensure there are at least 5 columns and extract text safely
                if len(text_cols) >= 5:
                    item = {
                        'no': text_cols[0].text.strip(),
                        'name': text_cols[1].text.strip(),
                        'size': text_cols[2].text.strip(),
                        'quantity': text_4.text.strip() if (text_4 := text_cols[4]) else '0', # Use assignment expression (Python 3.8+)
                        'price': text_3.text.strip() if (text_3 := text_cols[3]) else '0'
                    }
                    # Convert quantity and price to appropriate types
                    try:
                        item['quantity'] = int(item['quantity'])
                    except ValueError:
                        print(f"TiptopOrderParser: Warning: Could not convert quantity '{item['quantity']}' to int for item '{item['name']}'. Setting to 0.")
                        item['quantity'] = 0

                    try:
                        # Assuming price might have commas or currency symbols
                        item['price'] = self._get_money(item['price'])
                    except ValueError:
                         print(f"TiptopOrderParser: Warning: Could not parse price '{item['price']}' for item '{item['name']}'. Setting to 0.")
                         item['price'] = 0
                    except Exception as e:
                         print(f"TiptopOrderParser: Warning: Error parsing price '{item['price']}' for item '{item['name']}': {e}. Setting to 0.")
                         item['price'] = 0


                    items.append(item)
                    print(f"TiptopOrderParser: Parsed order item: {item['name']} ({item['size']}) x{item['quantity']}")
                else:
                    print(f"TiptopOrderParser: Warning: Skipping order row due to insufficient columns ({len(text_cols)} found).")
            except Exception as e:
                print(f"TiptopOrderParser: Error parsing order row: {e}. Skipping row.")

        return items

    def _get_money(self, text):
        # Handle potential non-numeric characters and commas
        cleaned_text = ''.join(filter(lambda x: x.isdigit() or x == ',', text))
        cleaned_text = cleaned_text.replace(',', '')
        return int(cleaned_text) if cleaned_text else 0 # Return 0 if text is empty after cleaning

