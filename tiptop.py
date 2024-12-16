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
        self.branch_on_page = await self.check_branch_on_page()

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
        product_name_selector = '.details-content .details-name'

        return await self.retry_click(product_card_selector, product_name_selector)

    async def retry_click(self, selector, expect_selector):
        await self.browser_manager.wait_and_click(selector)

        expect_element = await self.browser_manager.get_element(expect_selector)
        retries = 0
        while (retries < 3 and expect_element == None):
            retries += 1
            print('retrying for ', retries)

            element = await self.browser_manager.wait_for_element(selector, { 'get_element': True })
            if (element != None):
                print('element is still exists', element)
                await self.browser_manager.click(selector)
                sleep(retries)

            expect_element = await self.browser_manager.get_element(expect_selector)

        return expect_element

    async def add_product_to_cart(self, product_name, size):
        await self.goto_product(product_name)
        size_element = await self.select_product_size(size)

    async def select_product_size(self, size):
        available_sizes_selector = '.details-content .row div'
        size_element = await self.browser_manager.get_element_by_text(available_sizes_selector, size)

        if (size_element != None):
            await size_element.click()

            chosen_size_selector = '.details-content .row div a.btn-green'
            chosen_size = await self.browser_manager.get_element(chosen_size_selector)

            retries = 0
            while (retries < 3 and chosen_size == None):
                retries += 1
                print('retry selecting size for ', retries)
                await size_element.click()
                sleep(1)
                chosen_size = await self.browser_manager.get_element(chosen_size_selector)

        return size_element
