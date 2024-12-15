from pyppeteer import launch

class BrowserManager:
    def __init__(self):
        self.browser = None
        self.page = None

    async def open_browser_page(self):
        self.browser = await launch({'headless': False})
        pages = await self.browser.pages()
        self.page = pages[0]

    async def close(self):
        await self.browser.close()

    async def goto(self, url):
        await self.page.goto(url)

    async def screenshot(self, path):
        await self.page.screenshot({'path': path})

    async def type_text(self, selector, text):
        await self.page.focus(selector)
        await self.page.keyboard.type(text)

    async def press_enter(self):
        await self.page.keyboard.press('Enter')

    async def click(self, selector):
        await self.page.click(selector)

    async def click_xpath(self, expression):
        el_handle = await self.page.xpath(expression)
        await el_handle[0].click()

    async def get_element(self, selector):
        return await self.page.querySelector(selector)

    async def get_elements(self, selector):
        return await self.page.querySelectorAll(selector)

    async def get_element_text(self, selector):
        return await self.page.evaluate(f'document.querySelector("{selector}").innerText')

    async def wait_for_element(self, selector, options = None):
        try:
            await self.page.waitForSelector(selector, options)
            if (options != None and options.get('get_element') == True):
                return await self.get_element(selector)
        except TimeoutError:
            print(f'Element {selector} not found')

    async def wait_and_click(self, selector, options = None):
        if (options == None):
            options = { 'visible': True }
        else:
            options['visible'] = True

        options['get_element'] = True
        element = await self.wait_for_element(selector, options)
        await element.click()
