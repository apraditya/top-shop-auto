import asyncio
import os
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

class BrowserManager:
    def __init__(self):
        self.browser = None
        self.page = None
        self._playwright = None # Store playwright instance

    async def open_browser_page(self):
        """Opens a new browser instance and page."""
        print("Opening browser...")
        # Use async with for cleaner resource management - switching back to explicit start/stop
        # self._playwright_context = await async_playwright().__aenter__()
        self._playwright = await async_playwright().start()
        # Use headless=False to see the browser
        self.browser = await self._playwright.chromium.launch(headless=False)
        self.page = await self.browser.new_page()
        print("Browser opened.")

    async def close(self):
        """Closes the browser instance."""
        if self.browser:
            print("Closing browser...")
            await self.browser.close()
            self.browser = None
            self.page = None
            print("Browser closed.")
        # Use explicit stop instead of __aexit__
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None


    async def goto(self, url):
        """Navigates the page to a given URL."""
        if self.page:
            print(f"Navigating to {url}...")
            await self.page.goto(url)
            print("Navigation complete.")
        else:
            print("Error: Page not open. Cannot navigate.")

    async def screenshot(self, path, options = None):
        """Takes a screenshot of the full page."""
        if self.page:
            print(f"Taking screenshot: {path}")
            # The page.screenshot method expects path as a keyword argument
            await self.page.screenshot(path=path, full_page=True, **(options or {}))
            print("Screenshot saved.")
        else:
            print("Error: Page not open. Cannot take screenshot.")

    async def screenshot_element(self, selector, path, options = None):
        """Takes a screenshot of a specific element."""
        if self.page:
            print(f"Taking element screenshot: {path} (selector: {selector})")
            # Playwright recommends locators
            locator = self.page.locator(selector)
            await locator.screenshot(path=path, **(options or {}))
            print("Element screenshot saved.")
        else:
            print("Error: Page not open. Cannot take element screenshot.")

    async def type_text(self, selector, text):
        """Types text into an element."""
        if self.page:
            print(f"Typing '{text}' into '{selector}'")
            # Playwright recommends locators
            await self.page.locator(selector).type(text)
            print("Text typed.")
        else:
            print("Error: Page not open. Cannot type text.")

    async def press_backspace(self):
        """Presses the Backspace key."""
        if self.page:
            print("Pressing Backspace")
            await self.page.keyboard.press('Backspace')
            print("Backspace pressed.")
        else:
            print("Error: Page not open. Cannot press Backspace.")

    async def press_ctrl_a(self):
        """Presses Ctrl+A (select all)."""
        if self.page:
            print("Pressing Ctrl+A")
            # Use the combined key string
            await self.page.keyboard.press('Control+A')
            print("Ctrl+A pressed.")
        else:
            print("Error: Page not open. Cannot press Ctrl+A.")

    async def press_enter(self):
        """Presses the Enter key."""
        if self.page:
            print("Pressing Enter")
            # This assumes the focus is on an input field.
            # If not, you might need to focus first or use a specific locator.
            await self.page.keyboard.press('Enter')
            print("Enter pressed.")
        else:
            print("Error: Page not open. Cannot press Enter.")

    async def replace_text(self, selector, text):
        """Selects existing text and replaces it."""
        if self.page:
            print(f"Replacing text in '{selector}' with '{text}'")
            # Playwright recommends locators
            locator = self.page.locator(selector)
            # fill() is often better than type() for replacing text as it clears first
            await locator.fill(text)
            print("Text replaced.")
        else:
            print("Error: Page not open. Cannot replace text.")

    async def click(self, selector):
        """Clicks an element."""
        if self.page:
            print(f"Clicking '{selector}'")
            # Playwright recommends locators and click automatically waits
            await self.page.locator(selector).click()
            print("Clicked.")
        else:
            print("Error: Page not open. Cannot click.")

    async def click_xpath(self, expression):
        """Clicks an element using XPath."""
        if self.page:
            print(f"Clicking XPath '{expression}'")
            # Playwright recommends locators, using xpath= prefix
            await self.page.locator(f'xpath={expression}').click()
            print("Clicked XPath.")
        else:
            print("Error: Page not open. Cannot click XPath.")

    async def get_element(self, selector):
        """Gets a single element locator."""
        if self.page:
            print(f"Getting element '{selector}'")
            # Use locator for single element
            return self.page.locator(selector)
        else:
            print("Error: Page not open. Cannot get element.")
            return None

    async def get_elements(self, selector):
        """Gets a list of element locators."""
        if self.page:
            print(f"Getting elements '{selector}'")
            # Use locator.all() for multiple element locators
            return await self.page.locator(selector).all()
        else:
            print("Error: Page not open. Cannot get elements.")
            return []

    async def get_element_text(self, selector):
        """Gets the text content of an element."""
        if self.page:
            print(f"Getting text from '{selector}'")
            # Use locator.text_content()
            locator = self.page.locator(selector)
            try:
                text = await locator.text_content()
                print(f"Got text: '{text}'")
                return text
            except Exception as e:
                 print(f"Could not get text for '{selector}': {e}")
                 return None
        else:
            print("Error: Page not open. Cannot get element text.")
            return None

    async def get_element_by_text(self, selector, text):
        """Finds an element by its selector and text content."""
        if self.page:
            print(f"Getting element '{selector}' with text '{text}'")
            # Playwright locators can filter by text
            # Assuming the text is directly within the element matched by selector
            # If text is in a child element (like 'a' in your original code), adjust selector
            # Using get_by_text is often more robust for finding elements by visible text
            # Or filter by has_text
            locator = self.page.locator(selector, has_text=text)
            # Check if any element matches
            count = await locator.count()
            if count > 0:
                 # Return the locator for the first matching element
                 return locator.first
            else:
                 print(f"Element with text '{text}' not found within selector '{selector}'")
                 return None
        else:
             print("Error: Page not open. Cannot get element by text.")
             return None


    async def wait_for_element(self, selector, options = None):
        """Waits for an element to appear."""
        if self.page:
            print(f"Waiting for element '{selector}'...")
            try:
                # Playwright's wait_for_selector is sufficient for visibility/presence
                # For waiting for text content, use locator.wait_for() or evaluate
                # Timeout is in milliseconds in Playwright
                timeout_ms = options.get('timeout', 20) * 1000 if options else 20000
                await self.page.wait_for_selector(selector, state='visible', timeout=timeout_ms)
                print(f"Element '{selector}' found.")
                # Return the locator for the element after waiting
                return self.page.locator(selector)
            except PlaywrightTimeoutError:
                print(f'Element {selector} not found within timeout')
                return None
            except Exception as e:
                print(f"Error waiting for element '{selector}': {e}")
                return None
        else:
            print("Error: Page not open. Cannot wait for element.")
            return None

    async def wait_and_click(self, selector, options = None):
        """Waits for an element and then clicks it."""
        if self.page:
            print(f"Waiting for and clicking '{selector}'...")
            try:
                # Playwright's locator.click() automatically waits for the element
                # to be visible, enabled, and receive events.
                # We can just call click directly on the locator.
                # The options dictionary is not directly used by locator.click() in the same way
                # as pyppeteer's waitForSelector, but click has its own timeout option.
                timeout_ms = options.get('timeout', 20) * 1000 if options else 20000
                await self.page.locator(selector).click(timeout=timeout_ms)
                print(f"Element '{selector}' clicked after waiting.")
                return True
            except PlaywrightTimeoutError:
                 print(f'Element {selector} not found or clickable within timeout')
                 raise # Re-raise the exception if click fails after waiting
            except Exception as e:
                print(f"Error waiting for and clicking '{selector}': {e}")
                raise # Re-raise other exceptions
        else:
            print("Error: Page not open. Cannot wait and click.")
            return False

    async def get_page_content(self):
        """Retrieves the full HTML content of the current page."""
        if self.page:
            print("Retrieving page content...")
            try:
                content = await self.page.content()
                print("Page content retrieved.")
                return content
            except Exception as e:
                print(f"Error retrieving page content: {e}")
                return None
        else:
            print("Error: Page not open. Cannot retrieve content.")
            return None

