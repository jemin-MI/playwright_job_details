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

        await page.goto("https://in.indeed.com/", wait_until = "domcontentloaded")
        await page.wait_for_timeout(50000)
        #
        # await page.locator('#username').fill(username)
        # await page.wait_for_timeout(2000)


        # await page.wait_for_url("https://in.indeed.com/",wait_until = "domcontentloaded")
        breakpoint()
        cookies = await context.cookies()
        print("cookies", cookies)

        with open("indeed_cookie.json", 'w') as file:
            file.write(json.dumps(cookies))

        await browser.close()

asyncio.run(main())
