import asyncio
import json
from contants_dir.constant import Linkedin_user_id, Linkedin_User_password, Linkedin_login_url, Linkedin_link

from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Launch the browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        # Navigate to a page
        username = Linkedin_user_id
        password = Linkedin_User_password

        await page.goto(Linkedin_login_url, wait_until = "domcontentloaded")
        await page.wait_for_timeout(3000)

        await page.locator('#username').fill(username)
        await page.wait_for_timeout(2000)

        await page.locator('#password').fill(password)
        await page.wait_for_timeout(2000)

        button = page.locator('button[aria-label="Sign in"]')
        await button.click()
        await page.wait_for_timeout(4000)

        await page.wait_for_url(Linkedin_link + "feed/",wait_until = "domcontentloaded")

        cookies = await context.cookies()

        with open("linkedin_cookie.json", 'w') as file:
            file.write(json.dumps(cookies))

        await browser.close()

asyncio.run(main())
