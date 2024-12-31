import asyncio
import json
from binascii import a2b_qp

from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Launch the browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        # Navigate to a page
        username = 'jemin.ajudiya@mindinventory.com'
        password = 'Mind@123'

        await page.goto("https://www.linkedin.com/login/", wait_until = "domcontentloaded")
        await page.wait_for_timeout(3000)

        await page.locator('#username').fill(username)
        await page.wait_for_timeout(2000)

        await page.locator('#password').fill(password)
        await page.wait_for_timeout(2000)

        button = page.locator('button[aria-label="Sign in"]')
        await button.click()
        await page.wait_for_timeout(4000)



        await page.wait_for_url("https://www.linkedin.com/feed/",wait_until = "domcontentloaded")

        cookies = await context.cookies()

        with open("linkedin_cookie.json", 'w') as file:
            file.write(json.dumps(cookies))

        await browser.close()

asyncio.run(main())
