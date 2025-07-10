import asyncio
import os
from datetime import datetime

from tiptop import Tiptop
from tiptop_order_parser import TiptopOrderParser

branch = 'Rawamangun'
tt = Tiptop(branch)
# Assuming order.html exists and TiptopOrderParser works correctly
order_file = 'order.html' # Use a variable for the filename
print(f"Parsing order file '{order_file}'...")
top = TiptopOrderParser.from_file(order_file)
print(f"Order file parsed. Found {len(top.order_items)} items.")


async def prepare_order(): # Renamed function for clarity
    print(f"Attempting to set branch to {branch}...")
    await tt.set_branch_page()

    if not tt.branch_on_page:
        print(f"Failed to set branch to {branch}. Exiting.")
        # Ensure browser is closed even on failure
        await tt.browser_manager.close()
        return

    print(f"Successfully set branch to {tt.branch_on_page}")

    # Check if there are items to process
    if not top.order_items:
        print("No items found in the order file. Nothing to add.")
    else:
        for item in top.order_items:
            print(f'Attempting to add {item["name"]} {item["size"]}: {item["quantity"]}')
            # add_product_to_cart now handles navigation and waiting internally
            await tt.add_product_to_cart(item['name'], item['size'], item['quantity'])
            # Removed sleep(5) - waiting is now handled in add_product_to_cart

        # Optional: Open cart and screenshot after adding all items
        print("Finished adding items. Opening cart...")
        await tt.open_cart()
        await tt.screenshot_cart()
        # Keep cart open for potential manual inspection before saving page content
        # await tt.close_cart() # Close cart after screenshot - Removed this line


        # --- Add a final await to keep the browser open ---
        print("Script finished. Keeping browser open. Press Ctrl+C to close.")
        # The browser will stay open here until interrupted
        await asyncio.Future() # This will keep the event loop running indefinitely

    # This part will only be reached if the asyncio.Future() is cancelled (e.g., by Ctrl+C)
    await tt.browser_manager.close()
    print("Browser closed.")

# Use asyncio.run to run the main async function
if __name__ == "__main__":
    try:
        asyncio.run(prepare_order())
    except KeyboardInterrupt:
        print("\nScript interrupted by user (Ctrl+C). Closing browser...")
        # The browser closing is handled by the code after asyncio.Future()
        # when the Future is cancelled by the interrupt.
        pass # Allow the cleanup code after asyncio.Future() to run
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        # Attempt to close the browser on other errors too
        asyncio.run(tt.browser_manager.close())

