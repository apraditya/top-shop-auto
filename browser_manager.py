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

    async def type(self, selector, text):
        await self.page.focus(selector)
        await self.page.keyboard.type(text)

    async def click(self, selector):
        await self.page.click(selector)

    async def click_xpath(self, expression):
        el_handle = await self.page.xpath(expression)
        await el_handle[0].click()
