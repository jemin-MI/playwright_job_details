import asyncio
import datetime
import json
from job_details.web_logger import ini_logger
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from contants_dir.constant import Naukari, Naukari_link, input_job_role, page_count
from models.database import SessionLocal
from schema.pydentic import JobBase
from models.model import Job

logger = ini_logger("WebsiteScraper")


def add_data_db(data_dict):
    try:
        session = SessionLocal()
        data_list_pydantic = JobBase(**data_dict)

        job_data = Job(
            platform=data_list_pydantic.platform,
            platform_link=data_list_pydantic.platform_link,
            job_title=data_list_pydantic.job_title,
            job_link=data_list_pydantic.job_link,
            company=data_list_pydantic.company,
            company_link=data_list_pydantic.company_link,
            posted_on=data_list_pydantic.posted_on,
            position=data_list_pydantic.position,
            salary=data_list_pydantic.salary,
            duration=data_list_pydantic.duration,
            applicant=data_list_pydantic.applicant,
            job_description=data_list_pydantic.job_description,
            experience_level=data_list_pydantic.experience_level,
            location=data_list_pydantic.location,
            last_date_application=data_list_pydantic.last_date_application,
            industry=data_list_pydantic.industry,
            job_type=data_list_pydantic.job_type,
            industry_function=data_list_pydantic,
            skill_list=data_list_pydantic,
            early_applicant=data_list_pydantic.industry_function,
            job_id=data_list_pydantic.job_id,
            job_role=data_list_pydantic.job_role,
            interview_process=data_list_pydantic.interview_process,
            education=data_list_pydantic.education,
            specialization=data_list_pydantic.specialization,
        )

        session.add(job_data)
        session.commit()
        session.refresh(job_data)
        logger.info(f"Successfully added job data: {data_dict['job_title']}")
    except Exception as e:
        logger.error(f"Error in add_data_db: {e}")
        raise


def html_to_text(html_content):
    """Converts HTML content to plain text."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        formatted_text = []
        for element in soup.descendants:
            if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                formatted_text.append(f"[heading] {element.get_text(strip=True)}")
            elif element.name == "strong":
                formatted_text.append(f"[bold] {element.get_text(strip=True)}")
            elif element.name == "br":
                formatted_text.append("\n")
            elif element.name is None and element.strip():
                formatted_text.append(element.strip())
        return " ".join(formatted_text)
    except Exception as e:
        logger.error(f"Error in html_to_text: {e}")
        raise


async def extract_job_details(page, sub_div):
    """Extracts job details from a given sub-div."""
    try:
        job_div = sub_div.locator('a.title')
        link = await job_div.get_attribute('href')
        job_title = await job_div.inner_text() or 'Not Found'

        comp_name_div = sub_div.locator('a.comp-name')
        company = await comp_name_div.inner_text() or 'Not Found'
        company_url = await comp_name_div.get_attribute('href') or 'Not Found'
        await page.goto(link)

        return job_title, company, company_url, link
    except Exception as e:
        logger.error(f"Error while extracting job data: {e}")
        return None, None, None, None


async def extract_job_type_and_date(page):
    """Extracts job type and posted date."""
    try:
        sub_page_main_div = page.locator('#job_header')
        main_first_div = sub_page_main_div.locator("> div").nth(0)
        sub_first_div = main_first_div.locator("> div").nth(1)
        main_div_first = sub_first_div.nth(0)
        div_list_sub = main_div_first.locator("> div")

        duration_div = div_list_sub.nth(0)
        duration_list_div = duration_div.locator("> div")
        duration = await duration_list_div.nth(0).inner_text() or 'Not Found'
        salary = await duration_list_div.nth(1).inner_text() or 'Not Found'

        location_div = div_list_sub.nth(1)
        location = await location_div.inner_text() or 'Not Found'

        last_data_div = div_list_sub.nth(2)
        last_date_list_div = last_data_div.locator("> div")
        job_start_time = await last_date_list_div.nth(0).inner_text() or 'Not Found'
        last_date = await last_date_list_div.nth(1).inner_text() or 'Not Found'

        job_type = div_list_sub.nth(3)
        job_type_ = await job_type.inner_text() or 'Not Found'
        logger.info(f"Job Type: {job_type_}")

        return job_type_, duration, salary, location, last_date
    except Exception as e:
        logger.error(f"Error while extracting job type and date: {e}")
        return 'Not Found', 'Not Found', 'Not Found', 'Not Found', 'Not Found'


async def extract_applicants_and_openings(page):
    """Extracts applicants and job openings."""
    try:
        main_second_div = page.locator('#job_header').locator("> div").nth(1)
        sub_second_div = main_second_div.locator("> div").nth(0)
        sub_span_list = sub_second_div.locator('> span')

        posted_on = await sub_span_list.nth(0).locator('span').inner_text() or 'Not Found'
        opening = await sub_span_list.nth(1).locator('span').inner_text() or 'Not Found'
        applicants = await sub_span_list.nth(2).locator('span').inner_text() or 'Not Found'

        return posted_on, opening, applicants
    except Exception as e:
        logger.error(f"Error while extracting applicants and openings: {e}")
        return 'Not Found', 'Not Found', 'Not Found'


async def extract_job_description(page):
    """Extracts job description from the page."""
    try:
        script_tag = page.locator('script[type="application/ld+json"]')
        script_content = await script_tag.nth(0).inner_text()
        json_data = json.loads(script_content)
        description = json_data.get("description", "Description not found")
        return html_to_text(description)
    except Exception as e:
        logger.error(f"Error while extracting job description: {e}")
        return 'Not Found'


async def handle_pagination(page, current_page, data_list, pagewise):
    """Handles pagination logic."""
    try:
        pagewise.append({'page_' + str(current_page + 1): data_list})

        with open(f'page_wise_{Naukari}.json', 'w') as file:
            file.write(json.dumps(pagewise))

        icons = page.locator('.ni-icon-arrow-2')
        icon_count = await icons.count()

        if icon_count > 1 and page_count > 1:
            second_icon = icons.nth(1)
            await second_icon.click()
            logger.info("Clicked the second icon.")
        else:
            logger.info("Second icon not found.")
    except Exception as e:
        logger.error(f"Error in handle_pagination: {e}")
        raise


async def main():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto(f"{Naukari_link}+{input_job_role}-jobs?k={input_job_role}", wait_until="domcontentloaded")
            await page.wait_for_timeout(4000)

            pagewise = []
            for k in range(page_count):
                main_div = page.locator("#listContainer")
                second_div = main_div.locator("> div").nth(1)
                inner_div = second_div.locator("> div")
                sub_divs = inner_div.locator("> div")
                sub_div_count = await sub_divs.count()

                data_list = []
                for i in range(sub_div_count):
                    job_title, company, company_url, link = await extract_job_details(page, sub_divs.nth(i))

                    if not job_title:
                        continue

                    job_type_, duration, salary, location, last_date = await extract_job_type_and_date(page)
                    posted_on, opening, applicants = await extract_applicants_and_openings(page)
                    job_description = await extract_job_description(page)

                    data_dict = {
                        "platform": Naukari,
                        "platform_link": Naukari_link,
                        "company": company or None,
                        "company_link": company_url or None,
                        "job_title": job_title or None,
                        "job_link": link,
                        "location": location or None,
                        "job_type": job_type_ or None,
                        "duration": duration or None,
                        "salary": salary or None,
                        "last_date_application": last_date or None,
                        "posted_on": f"{posted_on} as per the {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" or None,
                        "applicant": applicants or None,
                        "opening": opening or None,
                        "job_description": job_description or None
                    }

                    add_data_db(data_dict)
                    data_list.append(data_dict)
                    with open('naukari_data.json', 'w') as file:
                        file.write(json.dumps(data_list))

                    await page.go_back()
                    await page.wait_for_timeout(3000)

                await handle_pagination(page, k, data_list,pagewise)

            await browser.close()
    except Exception as e:
        logger.error(f"Error in main: {e}")


asyncio.run(main())
