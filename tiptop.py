from browser_manager import BrowserManager
from time import sleep

class Tiptop:
    def __init__(self, branch = 'Pondok Bambu'):
        self.branch = branch
        self.branch_on_page = None
        self.browser_manager = BrowserManager()

    async def set_branch_page(self):
        await self.browser_manager.open_browser_page()
        await self.browser_manager.goto('https://shop.tiptop.co.id')

        sel_path = f'//span[@class="card-text-store" and contains(text(), "{self.branch}")]'
        await self.browser_manager.click_xpath(sel_path)

    async def page_branch(self):
        if (self.branch_on_page == None):
            self.branch_on_page = await self.check_branch_on_page()

        return self.branch_on_page

    async def check_branch_on_page(self):
        branch_header_selector = '.header-media-group span.back'
        return await self.browser_manager.get_element_text(branch_header_selector)

    async def type_search(self, product_name):
        search_selector = '.header-form-search.active input[type="text"]'
        await self.browser_manager.type_text(search_selector, product_name)

    async def search_product(self, product_name):
        await self.type_search(product_name)
        await self.browser_manager.press_enter()

        result_title_selector = 'section.error-part span.fw-bold'
        await self.browser_manager.wait_for_element(result_title_selector, { 'visible': True })

    async def goto_product(self, product_name):
        await self.search_product(product_name)

        product_card_selector = '.section.recent-part .product-card'
        await self.browser_manager.wait_and_click(product_card_selector)

        product_name_selector = '.details-content .details-name'
        product_detail = await self.browser_manager.get_element(product_name_selector)

        retries = 0
        while (retries < 3 and product_detail == None):
            retries += 1
            print('retrying for ', retries)

            product_card = await self.browser_manager.wait_for_element(product_card_selector, { 'get_element': True })
            if (product_card != None):
                print('product_card is still exists', product_card)
                await self.browser_manager.click(product_card_selector)
                sleep(retries)

            product_detail = await self.browser_manager.get_element(product_name_selector)

        if (product_detail == None):
            print('product_detail is still None')
            return
