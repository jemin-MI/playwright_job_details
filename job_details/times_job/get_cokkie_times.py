import time

from playwright.async_api import async_playwright
import json
async def login_example():
    async with async_playwright() as p:
        # Launch the browser
        browser = await p.chromium.launch(headless=False)  # Set headless=True for no UI
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the login page
        await page.goto("https://www.timesjobs.com/")  # Replace with your login URL
        time.sleep(5)
        # Fill in the email field
        await page.fill("#j_username", "jemin.ajudiya@mindinventory.com")  # Replace with your email

        # Fill in the password field
        await page.fill("#j_password", "Mind@123")  # Replace with your password

        # Click the login button
        await page.click("#submitbutton")

        # Wait for navigation or a specific element after login
        await page.wait_for_load_state('networkidle')  # Adjust based on page behavior

        # Print cookies to verify login success
        cookies = await context.cookies()
        for cookie in cookies:
            print(f"Name: {cookie['name']}, Value: {cookie['value']}, Domain: {cookie['domain']}")

        with open('times_cookie.json', 'w') as file:
            file.write(json.dumps(cookies))
        with open('times_cookie.txt', 'w') as file:
            file.write(str(cookies))
        # Close the browser
        await page.wait_for_timeout(10000)

        await browser.close()

# Run the login function
import asyncio
asyncio.run(login_example())
