from asyncio import sleep as async_sleep
from time import time
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

class BrowserManager:
    def __init__(self):
        self.browser = None
        self.page = None
        self._playwright_context = None # To hold the async_playwright context

    async def open_browser_page(self):
        # Use async with for cleaner resource management
        self._playwright_context = await async_playwright().__aenter__()
        self.browser = await self._playwright_context.chromium.launch(headless=False)
        self.page = await self.browser.new_page()

    async def close(self):
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.page = None
        if self._playwright_context:
            await self._playwright_context.__aexit__(None, None, None)
            self._playwright_context = None

    async def goto(self, url):
        await self.page.goto(url)

    async def screenshot(self, path, options = None):
        options = {} if options is None else options
        # The page.screenshot method expects path as a keyword argument
        await self.page.screenshot(path=path, **options)


    async def screenshot_element(self, selector, path, options = None):
        options = {} if options is None else options

        # Playwright recommends locators
        locator = self.page.locator(selector)
        await locator.screenshot(path=path, **options)


    async def type_text(self, selector, text):
        # Playwright recommends locators
        await self.page.locator(selector).type(text)

    async def press_backspace(self):
        await self.page.keyboard.press('Backspace')

    async def press_ctrl_a(self):
        await self.page.keyboard.down('Control')
        await self.page.keyboard.press('KeyA')
        await self.page.keyboard.up('Control')

    async def press_enter(self):
        # This assumes the focus is on an input field.
        # If not, you might need to focus first or use a specific locator.
        await self.page.keyboard.press('Enter')

    async def replace_text(self, selector, text):
        # Playwright recommends locators
        locator = self.page.locator(selector)
        await locator.fill(text) # fill() is often better than type() for replacing text

    async def click(self, selector):
        # Playwright recommends locators and click automatically waits
        await self.page.locator(selector).click()

    async def click_xpath(self, expression):
        # Playwright recommends locators, using xpath= prefix
        await self.page.locator(f'xpath={expression}').click()

    async def get_element(self, selector):
        # Use query_selector for single element handle (less common in Playwright)
        # Playwright generally prefers locators
        return await self.page.query_selector(selector)

    async def get_elements(self, selector):
        # Use query_selector_all for multiple element handles
        return await self.page.query_selector_all(selector)

    async def get_element_text(self, selector):
        # Use locator.text_content()
        locator = self.page.locator(selector)
        return await locator.text_content()

    async def get_element_by_text(self, selector, text):
        # Playwright locators can filter by text
        # Assuming the text is directly within the element matched by selector
        # If text is in a child element (like 'a' in your original code), adjust selector
        locator = self.page.locator(selector, has_text=text)
        # Check if any element matches
        count = await locator.count()
        if count > 0:
            # Return the first matching element's child 'a' if needed, or the locator itself
            # Based on your original code returning element.querySelector('a')
            # Note: query_selector returns an ElementHandle, locator returns a Locator
            # Returning a Locator is often more useful for subsequent actions
            # If you specifically need the ElementHandle, use query_selector on the locator
            # For now, returning the Locator for the child 'a'
            child_locator = locator.first.locator('a')
            if await child_locator.count() > 0:
                 return child_locator.first # Return the Locator for the 'a' element
            else:
                 # If no 'a' child, maybe return the parent locator? Or None?
                 # Based on original code, it seems to expect an element to click.
                 # Let's return the locator for the parent element if no 'a' child is found,
                 # or None if the parent itself wasn't found by text.
                 print(f"Element with text '{text}' found, but no clickable 'a' child within selector '{selector}'")
                 return locator.first # Return the locator for the element found by text
        else:
             print(f"Element with text '{text}' not found within selector '{selector}'")
             return None

    async def wait_for_element(self, selector, options = None):
        try:
            # Playwright's wait_for_selector is sufficient for visibility/presence
            # For waiting for text content, use locator.wait_for() or evaluate
            # Timeout is in milliseconds in Playwright
            timeout_ms = options.get('timeout', 20) * 1000 if options else 20000
            await self.page.wait_for_selector(selector, state='visible', timeout=timeout_ms)
            # Return the locator for the element after waiting
            return self.page.locator(selector)
        except PlaywrightTimeoutError:
            print(f'Element {selector} not found within timeout')
            return None

    # Playwright actions like click automatically wait for the element to be ready
    # The custom wait_and_click method can likely be replaced by just calling click()
    # Keeping it for now but simplifying its implementation
    async def wait_and_click(self, selector, options = None):
        # Playwright's locator.click() automatically waits for the element
        # to be visible, enabled, and receive events.
        # We can just call click directly on the locator.
        # The options dictionary is not directly used by locator.click() in the same way
        # as pyppeteer's waitForSelector, but click has its own timeout option.
        timeout_ms = options.get('timeout', 20) * 1000 if options else 20000
        try:
            await self.page.locator(selector).click(timeout=timeout_ms)
        except PlaywrightTimeoutError:
             print(f'Element {selector} not found or clickable within timeout')
             raise # Re-raise the exception if click fails after waiting
