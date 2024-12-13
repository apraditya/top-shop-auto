from browser_manager import BrowserManager

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
