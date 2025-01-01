import asyncio
import json

from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        # Launch the browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Load cookies from a file
        # with open("indeed_cookie.json", "r") as f:
        #     cookies = json.loads(f.read())
        # await context.add_cookies(cookies)

        # Wait for the page to load
        await page.wait_for_timeout(4000)

        # Navigate to Indeed and wait until DOM content is loaded
        await page.goto("https://in.indeed.com/", wait_until="domcontentloaded")

        # Wait for the URL to load properly
        await page.wait_for_url("https://in.indeed.com/")  # Wait

        job_title = 'developer'
        job_locations = 'Worldwide'
        await asyncio.sleep(5)
        await page.locator('#text-input-what').fill(job_title)
        await asyncio.sleep(2)
        await page.locator('#text-input-what').press('Enter')

        await asyncio.sleep(2)
        await page.locator('#text-input-where').fill(job_locations)
        await asyncio.sleep(2)
        await page.locator('#text-input-where').press('Enter')

        await asyncio.sleep(2)
        await page.locator("button.yosegi-InlineWhatWhere-primaryButton").press('Enter')
        await asyncio.sleep(4)

        # await page.wait_for_selector("div#mosaic-provider-jobcards ul")

        # Iterate through each <li> element and print its text content
        li_elements = await page.query_selector_all("#mosaic-provider-jobcards li")
        data_list = []
        for index, li in enumerate(li_elements):
            data_dict = {"platform": "Indeed",
                         "platform_link": "https://in.indeed.com/", }
            html_li = await li.inner_html()

            job_div = await li.query_selector("h2.jobTitle")
            if job_div:
                a_tag = await job_div.query_selector("a")
                if a_tag:
                    job_href = await a_tag.get_attribute("href")
                    job_heading = await a_tag.text_content()

                    if job_href and job_heading:
                        # Fix for company name, location, and rating

                        company_name_selector = await li.query_selector(
                            "div.company_location span[data-testid='company-name']")
                        company_location_selector = await li.query_selector("div[data-testid='text-location']")
                        company_rating_selector = await li.query_selector("span[data-testid='holistic-rating']")

                        company_name = await company_name_selector.text_content() if company_name_selector else None
                        company_location = await company_location_selector.text_content() if company_location_selector else None
                        company_rating = await company_rating_selector.text_content() if company_rating_selector else None

                        # Fix for metadata
                        job_metadata_div = await li.query_selector_all("div.jobMetaDataGroup ul li")

                        metadata_list = []
                        for meta_list in job_metadata_div:
                            text = await meta_list.text_content()
                            metadata_list.append(text.strip())

                        data_dict['Job Link'] = 'https://in.indeed.com' + job_href
                        data_dict['Job Title'] = job_heading
                        data_dict['Company Name'] = company_name
                        data_dict['Company Location'] = company_location
                        data_dict['Rating'] = company_rating
                        data_list.append(data_dict)
                        with open('indded_data.json', 'w') as file:
                            file.write(json.dumps(data_list))

        # await page.wait_for_selector("text=Results")
        await asyncio.sleep(3)
        await browser.close()


asyncio.run(main())
