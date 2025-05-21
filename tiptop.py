from browser_manager import BrowserManager
from time import sleep, strftime
# Import Playwright's TimeoutError to catch it specifically if needed
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

class Tiptop:
    def __init__(self, branch = 'Pondok Bambu'):
        self.branch = branch
        self.branch_on_page = None
        self.browser_manager = BrowserManager()
        self.mobile_menu_locator = None # Store locator instead of ElementHandle

    async def set_branch_page(self):
        print("set_branch_page: Starting...")
        await self.browser_manager.open_browser_page()
        print("set_branch_page: Browser page opened.")
        await self.browser_manager.goto('https://shop.tiptop.co.id')
        print("set_branch_page: Navigated to homepage.")

        # Use Playwright's xpath locator
        sel_path = f'//span[@class="card-text-store" and contains(text(), "{self.branch}")]'
        print(f"set_branch_page: Attempting to click branch with xpath: {sel_path}")
        try:
            await self.browser_manager.click_xpath(sel_path)
            print(f"set_branch_page: Clicked branch '{self.branch}'.")
            print("set_branch_page: Checking branch on page...")
            self.branch_on_page = await self.check_branch_on_page()
            print(f"set_branch_page: check_branch_on_page returned: {self.branch_on_page}")
        except PlaywrightTimeoutError:
            print(f"set_branch_page: Playwright Timeout Error: Could not find or click branch '{self.branch}'.")
            self.branch_on_page = None # Indicate failure
        except Exception as e:
            print(f"set_branch_page: An unexpected error occurred while setting branch: {e}")
            self.branch_on_page = None

        # Store the locator for mobile menu - check if page is available
        if self.browser_manager.page:
             self.mobile_menu_locator = self.browser_manager.page.locator('.mobile-menu')
             print("set_branch_page: Mobile menu locator stored.")
        else:
             self.mobile_menu_locator = None
             print("set_branch_page: Browser page not available, mobile menu locator not stored.")

        print("set_branch_page: Finished.")


    async def page_branch(self):
        if (self.branch_on_page == None):
            self.branch_on_page = await self.check_branch_on_page()

        return self.branch_on_page

    async def check_branch_on_page(self):
        print("check_branch_on_page: Starting...")
        # Reverted selector back to the branch name element
        branch_header_selector = '.header-content a.header-logo'
        print(f"check_branch_page: Waiting for element: {branch_header_selector}")
        # wait_for_element now returns a locator
        branch_header_locator = await self.browser_manager.wait_for_element(branch_header_selector, {'timeout': 10000}) # Added timeout
        print(f"check_branch_on_page: wait_for_element returned: {branch_header_locator}")
        if branch_header_locator:
             print("check_branch_on_page: Element found, getting text content.")
             text = await branch_header_locator.text_content() # Use locator.text_content()
             print(f"check_branch_on_page: Text content: {text}")
             print("check_branch_on_page: Finished, returning text.")
             return text
        print("check_branch_on_page: Element not found, returning None.")
        return None


    async def type_search(self, product_name):
        search_selector = '.header-form-search.active input[type="text"]'
        print(f"type_search: Typing '{product_name}' into '{search_selector}'")
        # browser_manager.type_text now uses locator.type()
        await self.browser_manager.type_text(search_selector, product_name)
        print("type_search: Finished.")

    async def search_product(self, product_name):
        print(f"search_product: Searching for '{product_name}'...")
        await self.type_search(product_name)
        # browser_manager.press_enter now uses page.keyboard.press()
        print("search_product: Pressing Enter.")
        await self.browser_manager.press_enter()

        # Wait for the search results container or at least one product card to appear
        result_container_selector = '.section.recent-part .container .row'
        print(f"search_product: Waiting for search results container: {result_container_selector}")
        await self.browser_manager.wait_for_element(result_container_selector, { 'visible': True, 'timeout': 15000 }) # Wait for container
        print("search_product: Search results container visible.")


    async def goto_product(self, product_name):
        print(f"goto_product: Navigating to product details for '{product_name}'...")
        await self.search_product(product_name)
        print(f"goto_product: Search completed for '{product_name}'.")

        # Construct a specific locator for the product card containing the name
        # Assuming the product name text is directly within or a descendant of .product-card
        # This locator will find the *specific* card for the product name
        # Using the selector provided in the user's last message
        product_card_locator = self.browser_manager.page.locator('.section.recent-part .product-card .product-name a', has_text=product_name).first # Use .first in case multiple match
        print(f"goto_product: Created locator for product card with text '{product_name}'.")

        # Selector for the element expected on the details page (e.g., the product name on the details page)
        product_name_selector_details_page = '.details-content .details-name'
        print(f"goto_product: Expecting element '{product_name_selector_details_page}' on details page.")

        # Click the specific product card locator and wait for the details page element
        # retry_click now accepts a locator
        print("goto_product: Calling retry_click...")
        result = await self.retry_click(product_card_locator, product_name_selector_details_page)
        print(f"goto_product: retry_click returned: {result}")
        return result

    # retry_click now accepts a Locator for the element to click
    async def retry_click(self, element_to_click_locator, expect_selector):
        print(f"retry_click: Starting for element {element_to_click_locator} and expecting {expect_selector}")
        try:
            # Wait for the element to click to be visible
            print(f"retry_click: Waiting for element to click to be visible...")
            # Use locator.wait_for() to ensure the specific element is ready
            await element_to_click_locator.wait_for(state='visible', timeout=15000) # Wait up to 15 seconds
            print(f"retry_click: Element to click is visible.")

            # Check if the locator actually exists after waiting (should be > 0 if wait_for succeeded)
            if await element_to_click_locator.count() == 0:
                 print(f"retry_click: Locator for element to click not found after waiting.")
                 return None

            print(f"retry_click: Clicking element...")
            # --- MODIFIED: Removed force=True from the click ---
            await element_to_click_locator.click(timeout=15000) # Added click timeout
            print(f"retry_click: Click successful. Waiting for expected element '{expect_selector}'...")

            # Wait for the expected element to appear on the next page (product details page)
            # wait_for_element returns a locator
            expect_locator = await self.browser_manager.wait_for_element(expect_selector, {'timeout': 10000}) # Wait up to 10 seconds for details page element
            print(f"retry_click: wait_for_element for '{expect_selector}' returned: {expect_locator}")

            if expect_locator:
                 print("retry_click: Expected element found. Getting ElementHandle.")
                 # Return the ElementHandle of the expected element on the details page
                 # .element_handle() gets the underlying ElementHandle from a Locator
                 handle = await expect_locator.element_handle()
                 print("retry_click: Finished, returning ElementHandle.")
                 return handle
            else:
                 print(f"retry_click: Expected element '{expect_selector}' not found after clicking product card.")
                 return None # Return None if the expected element doesn't appear
        except PlaywrightTimeoutError as e:
            # This catches timeout errors from element_to_click_locator.wait_for() or click()
            # or from wait_for_element(expect_selector) if it's not caught internally there.
            print(f"retry_click: Playwright Timeout Error: {e}")
            print(f"retry_click: Failed during click or waiting for '{expect_selector}'.")
            return None # Return None if the click or subsequent wait failed
        except Exception as e:
            print(f"retry_click: An unexpected error occurred: {e}")
            return None


    async def add_product_to_cart(self, product_name, size, quantity):
        print(f"add_product_to_cart: Adding '{product_name}' size '{size}' quantity '{quantity}'...")
        # goto_product now returns ElementHandle of the details page name element, or None
        details_name_element_handle = await self.goto_product(product_name)

        # Check if the product details page was reached successfully
        if details_name_element_handle is None:
            print(f"add_product_to_cart: Could not navigate to product details page for {product_name}. Skipping item.")
            # Optional: Navigate back to search results or home page if needed
            # await self.browser_manager.goto('https://shop.tiptop.co.id') # Example
            return # Exit if navigation failed

        print(f"add_product_to_cart: Navigated to details page for {product_name}")

        # Now proceed with selecting size and quantity on the details page
        # select_product_size expects a size string and returns a locator or None
        print(f"add_product_to_cart: Selecting size '{size}'...")
        size_locator = await self.select_product_size(size)

        if (size_locator == None):
            print(f'add_product_to_cart: Size "{size}" not found for product "{product_name}". Skipping item.')
            # Optional: Navigate back or close modal
            # await self.browser_manager.goto('https://shop.tiptop.co.id') # Example
            return

        print(f"add_product_to_cart: Selected size {size}")

        print(f"add_product_to_cart: Setting quantity to {quantity}...")
        await self.set_product_quantity(quantity)
        print(f"add_product_to_cart: Set quantity to {quantity}")

        add_button_selector = '.details-content .details-action-group .product-adds'
        print(f"add_product_to_cart: Clicking 'Add to Cart' button: {add_button_selector}")
        # browser_manager.click now uses locator.click() and auto-waits
        try:
            await self.browser_manager.click(add_button_selector)
            print(f"add_product_to_cart: Clicked 'Add to Cart' for {product_name}")

            # Wait for the cart sidebar to become active as an indicator the item was processed
            # This replaces the sleep(5) in reorder.py
            cart_sidebar_selector = '.cart-sidebar.active'
            print(f"add_product_to_cart: Waiting for cart sidebar to become active: {cart_sidebar_selector}")
            # Use a shorter timeout here, maybe 5 seconds, as the cart should appear quickly
            await self.browser_manager.wait_for_element(cart_sidebar_selector, { 'visible': True, 'timeout': 5000 })
            print("add_product_to_cart: Cart sidebar appeared, item likely added.")

            # Optional: Close the product details page/modal if it's still open
            # This depends on the UI flow. If clicking add to cart closes the modal, this isn't needed.
            # If it stays open, we might need a close button selector.
            # Assuming it closes or doesn't block the next search.

        except PlaywrightTimeoutError:
            print(f"add_product_to_cart: Playwright Timeout Error: Failed to click 'Add to Cart' or wait for cart sidebar for {product_name}. Skipping item.")
            # Optional: Navigate back or close modal
            # await self.browser_manager.goto('https://shop.tiptop.co.id') # Example
        except Exception as e:
            print(f"add_product_to_cart: An unexpected error occurred after clicking add to cart: {e}")

        print(f"add_product_to_cart: Finished adding '{product_name}'.")


    async def select_product_size(self, size):
        print(f"select_product_size: Selecting size '{size}'...")
        available_sizes_selector = '.details-content .row div'
        # get_element_by_text now returns a locator or None
        # This finds the div containing the size text, then looks for the clickable 'a' inside it
        print(f"select_product_size: Getting element by text '{size}' within '{available_sizes_selector}'")
        size_locator = await self.browser_manager.get_element_by_text(available_sizes_selector, size)
        print(f"select_product_size: get_element_by_text returned: {size_locator}")

        if (size_locator != None):
            # size_locator is the locator for the 'a' element inside the div
            # Playwright's click automatically waits for this 'a' element
            try:
                print(f"select_product_size: Clicking size locator...")
                await size_locator.click(timeout=10000) # Added click timeout
                print("select_product_size: Click successful. Waiting for green indicator...")
                # You might want to add a wait here for the 'a.btn-green' to appear/change state
                chosen_size_selector = '.details-content .row div a.btn-green' # Selector for the chosen size indicator
                # wait_for_element now returns a locator
                # Wait up to 5 seconds for the green indicator to appear on the clicked size
                await self.browser_manager.wait_for_element(chosen_size_selector, {'timeout': 5000})
                print("select_product_size: Green indicator appeared.")
                # Return the locator for the size element that was clicked
                print("select_product_size: Finished, returning size locator.")
                return size_locator
            except PlaywrightTimeoutError:
                 print(f"select_product_size: Playwright Timeout Error: Clicking size '{size}' failed or timed out.")
                 return None
            except Exception as e:
                 print(f"select_product_size: An unexpected error occurred while selecting size: {e}")
                 return None
        else:
            print(f"select_product_size: Size locator not found for '{size}'. Returning None.")
            return None


    async def set_product_quantity(self, quantity):
        print(f"set_product_quantity: Setting quantity to {quantity}...")
        quantity_selector = '.details-content .product-action input[type="text"]'
        # browser_manager.replace_text now uses locator.fill() and auto-waits
        try:
            await self.browser_manager.replace_text(quantity_selector, str(quantity))
            print(f"set_product_quantity: Quantity set to {quantity}.")
        except PlaywrightTimeoutError:
            print(f"set_product_quantity: Playwright Timeout Error: Failed to set quantity to {quantity}.")
        except Exception as e:
            print(f"set_product_quantity: An unexpected error occurred while setting quantity: {e}")


    async def open_cart(self):
        print("open_cart: Starting...")
        # Check if the mobile menu locator exists and is visible
        is_mobile = self.mobile_menu_locator and await self.mobile_menu_locator.is_visible()

        if is_mobile:
            cart_selector = 'button.cart-btn .fa-shopping-basket'
            print("open_cart: Using mobile cart selector.")
        else:
            cart_selector = '.header-widget .header-cart'
            print("open_cart: Using desktop cart selector.")

        # browser_manager.click now uses locator.click() and auto-waits
        try:
            print(f"open_cart: Clicking cart button: {cart_selector}")
            await self.browser_manager.click(cart_selector)
            # wait_for_element now returns a locator
            print("open_cart: Waiting for cart footer...")
            await self.browser_manager.wait_for_element('.cart-footer', { 'visible': True, 'timeout': 10000 }) # Wait for cart footer
            print("open_cart: Cart opened.")
        except PlaywrightTimeoutError:
            print("open_cart: Playwright Timeout Error: Failed to open cart or wait for cart footer.")
        except Exception as e:
            print(f"open_cart: An unexpected error occurred while opening cart: {e}")

        print("open_cart: Finished.")


    async def close_cart(self):
        print("close_cart: Starting...")
        cart_selector = '.cart-header .cart-close'
        # browser_manager.click now uses locator.click() and auto-waits
        try:
            print(f"close_cart: Clicking close cart button: {cart_selector}")
            await self.browser_manager.click(cart_selector)
            # Optional: Wait for the cart sidebar to become hidden
            print("close_cart: Waiting for cart sidebar to become hidden...")
            await self.browser_manager.page.wait_for_selector('.cart-sidebar.active', state='hidden', timeout=5000)
            print("close_cart: Cart closed.")
        except PlaywrightTimeoutError:
            print("close_cart: Playwright Timeout Error: Failed to close cart.")
        except Exception as e:
            print(f"close_cart: An unexpected error occurred while closing cart: {e}")

        print("close_cart: Finished.")


    async def screenshot_cart(self):
        print("screenshot_cart: Starting...")
        cart_sidebar_selector = '.cart-sidebar.active'
        # wait_for_element now returns a locator
        # Ensure the cart is visible before attempting screenshot
        print(f"screenshot_cart: Waiting for cart sidebar to be active: {cart_sidebar_selector}")
        cart_sidebar_locator = await self.browser_manager.wait_for_element(cart_sidebar_selector, { 'visible': True, 'timeout': 5000 }) # Wait for cart to be active

        if (cart_sidebar_locator is None):
            print("screenshot_cart: Cart sidebar not found or not active for screenshot. Cannot take screenshot.")
            return # Exit if not found initially

        timestamp = strftime("%Y%m%d%H%M")
        screenshot_path = f'images/tiptop_cart_{timestamp}.png'
        print(f"screenshot_cart: Taking screenshot of cart: {screenshot_path}")
        # browser_manager.screenshot_element now uses locator.screenshot()
        try:
            await self.browser_manager.screenshot_element(
                cart_sidebar_selector, # Pass the selector to the method
                screenshot_path,
                { 'fullPage': False }) # fullPage=True might capture the whole page, not just the element
            print("screenshot_cart: Screenshot taken.")
        except Exception as e: # Catch potential errors during screenshot
            print(f"screenshot_cart: Failed to take screenshot: {e}")

        print("screenshot_cart: Finished.")
