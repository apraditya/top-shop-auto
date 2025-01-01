import asyncio
from time import sleep

from tiptop import Tiptop
from tiptop_order_parser import TiptopOrderParser

branch = 'Rawamangun'
tt = Tiptop(branch)
top = TiptopOrderParser.from_file('order.html')

async def prepare_pyppeteer():
    await tt.set_branch_page()
    bm = tt.browser_manager
    for item in top.order_items:
        print(f'Adding {item["name"]} {item["size"]}: {item["quantity"]}')
        await tt.add_product_to_cart(item['name'], item['size'], item['quantity'])
        sleep(5)

    await tt.screenshot_cart()

asyncio.run(prepare_pyppeteer())
