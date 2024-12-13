from browser_manager import BrowserManager

class Tiptop:
    def __init__(self, branch = 'Pondok Bambu'):
        self.branch = branch
        self.browser_manager = BrowserManager()

    async def set_branch_page(self):
        await self.browser_manager.open_browser_page()
        await self.browser_manager.goto('https://shop.tiptop.co.id')

        sel_path = f'//span[@class="card-text-store" and contains(text(), "{self.branch}")]'
        await self.browser_manager.click_xpath(sel_path)
