from browser_manager import BrowserManager
from time import sleep, strftime

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
        self.mobile_menu = await self.browser_manager.wait_for_element('.mobile-menu', { 'get_element': True })
        sleep(3)

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

        result_title_selector = '.section.recent-part .product-card'
        await self.browser_manager.wait_for_element(result_title_selector, { 'visible': True })

    async def goto_product(self, product_name):
        await self.search_product(product_name)
        sleep(5)

        product_card_selector = '.section.recent-part .product-card'
        product_name_selector = '.details-content .details-name'

        return await self.retry_click(product_card_selector, product_name_selector)

    async def retry_click(self, selector, expect_selector):
        await self.browser_manager.wait_and_click(selector)

        expect_element = await self.browser_manager.get_element(expect_selector)
        retries = 0
        while (retries < 3 and expect_element == None):
            retries += 1

            element = await self.browser_manager.wait_for_element(selector, { 'get_element': True })
            if (element != None):
                await self.browser_manager.click(selector)
                sleep(retries)

            expect_element = await self.browser_manager.get_element(expect_selector)

        return expect_element

    async def add_product_to_cart(self, product_name, size, quantity):
        await self.goto_product(product_name)
        size_element = await self.select_product_size(size)

        if (size_element == None):
            print(f'size {size} not found')
            return

        await self.set_product_quantity(quantity)

        add_button_selector = '.details-content .details-action-group .product-adds'
        await self.browser_manager.click(add_button_selector)

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

    async def set_product_quantity(self, quantity):
        quantity_selector = '.details-content .product-action input[type="text"]'
        await self.browser_manager.replace_text(quantity_selector, str(quantity))

    async def open_cart(self):
        if (self.mobile_menu == None):
            cart_selector = '.header-widget .header-cart'
        else:
            cart_selector = 'button.cart-btn .fa-shopping-basket'

        await self.browser_manager.click(cart_selector)
        await self.browser_manager.wait_for_element('.cart-footer', { 'visible': True })

    async def close_cart(self):
        cart_selector = '.cart-header .cart-close'
        await self.browser_manager.click(cart_selector)

    async def screenshot_cart(self):
        cart_sidebar_selector = '.cart-sidebar.active'
        cart_sidebar = await self.browser_manager.get_element(cart_sidebar_selector)

        if (cart_sidebar == None):
            await self.open_cart()
            sleep(1)

        timestamp = strftime("%Y%m%d%H%M")
        await self.browser_manager.screenshot_element(
            cart_sidebar_selector,
            f'images/tiptop_cart_{timestamp}.png',
            { 'fullPage': True })
