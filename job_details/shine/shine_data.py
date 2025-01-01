import asyncio
import json
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import logging

from sqlalchemy.testing import assert_warns
from sqlalchemy.util import await_only

from contants_dir.constant import Shine_link, Shine, TimesJob_Api_Url, Shine_Job_Search, input_job_location, \
    input_job_role, \
    shine_job_experiance, page_count, Naukari_link
from models.database import SessionLocal
from schema.pydentic import JobBase
from models.model import Job

# Set up logger
logger = logging.getLogger('shine_scraper')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def add_data_db(data_dict):
    """
    Adds job data to the database.
    Maps Pydantic model to SQLAlchemy model and adds it to the session.

    Args:
        data_dict (dict): Data dictionary containing job details.
    """
    try:
        session = SessionLocal()
        data_list_pydantic = JobBase(**data_dict)

        # Map Pydantic model to SQLAlchemy model
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

        # Add to session and commit
        session.add(job_data)
        session.commit()
        session.refresh(job_data)
        logger.info(f"Successfully added job data: {data_dict['job_title']}")
    except Exception as e:
        logger.error(f"Error in add_data_db: {e}")
        raise


def html_to_text(html_content):
    """
    Converts HTML content to plain text.

    Args:
        html_content (str): HTML string to convert.

    Returns:
        str: Plain text extracted from the HTML.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Define a list to hold the formatted text parts
        formatted_text = []

        # Iterate through all elements in the parsed HTML
        for element in soup.descendants:
            if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:  # Heading tags
                formatted_text.append(f"[heading] {element.get_text(strip=True)}")
            elif element.name == "strong":  # Bold tags
                formatted_text.append(f"[bold] {element.get_text(strip=True)}")
            elif element.name == "br":  # Line breaks
                formatted_text.append("\n")
            elif element.name is None and element.strip():  # Plain text
                formatted_text.append(element.strip())

        # Combine all parts with spaces to form the final string
        return " ".join(formatted_text)
    except Exception as e:
        logger.error(f"Error in html_to_text: {e}")
        return 'Not Found'


async def pagination(data_list, pagewise, page, context):
    current_page = 1
    page_dict = {current_page: data_list}
    pagewise.append(page_dict)
    # Save page-wise data to JSON
    with open(f'page_wise{Shine}.json', 'w') as page_file:
        page_file.write(json.dumps(pagewise))

    # Navigate to next page if available
    left_panel = page.locator('.jsrp_leftPanel > div')
    second_div = left_panel.nth(1).locator('a').last

    if await second_div.is_visible():
        await second_div.click()
        await main_iterator(page, pagewise, context)
        logger.info(f"Navigating to page {current_page + 1}")
    else:
        logger.warning(f"Next page button not visible, ending loop on page {current_page + 1}")
        return None


async def main_iterator(page, pagewise, context):
    current_page = 1
    # Wait and get job results from the page
    await page.wait_for_timeout(2000)
    script_tag = page.locator('script#\\__NEXT_DATA__')
    script_content = await script_tag.text_content()

    data_dict = json.loads(script_content)
    main_dict = data_dict['props']['pageProps']['initialState']['jsrp']['searchresult']['data']['results']

    data_list = []
    for i in main_dict:
        company_name = i['jCName']
        job_title = i['jJT']
        job_id = i['id']
        job_link = f'{Shine_Job_Search}' + i['jSlug']
        job_location = i['jLoc']
        posted_on = i['jPDate']
        required_experiance = i['jExp']

        # Fetch job details from API
        url = f'{TimesJob_Api_Url}{job_id}/'
        response = requests.get(url)
        data = response.json()
        await page.wait_for_timeout(1500)

        # Extract job description and other details
        job_description = html_to_text(data['results'][0]['jJD'])
        required_skills = data['results'][0]['jKwd']
        job_area = data['results'][0]['jArea']
        min_salary = data['results'][0]['min_salary']
        max_salary = data['results'][0]['max_salary']

        # Prepare data dictionary
        data_dict = {
            "platform": Shine,
            "platform_link": Shine_link,
            "company": company_name,
            "job_title": job_title,
            "job_link": job_link,
            "location": str(job_location),
            "posted_on": posted_on,
            "experiance": required_experiance,
            "skill_list": required_skills,
            "job_type": ', '.join(map(str, job_area)),
            "min_salary": min_salary,
            "max_salary": max_salary,
            "salary": min_salary + ' ' + max_salary,
            "job_description": job_description
        }

        # Add data to the database and save to JSON
        add_data_db(data_dict)
        data_list.append(data_dict)
        with open('shine_data.json', 'w') as file:
            file.write(json.dumps(data_list))

    # Page-wise data collection
    await pagination(data_list, pagewise, page, context)


async def page_loader(page):
    await page.goto(f"{Shine_link}", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)

    # Fill out search form with job role, location, and experience
    input_toggle_div = page.locator('#webSearchBar')
    await input_toggle_div.click()
    await page.fill('#id_q', input_job_role)
    await page.fill('#id_loc', input_job_location)
    job_experince_div = page.locator('#id_exp')
    await job_experince_div.fill(shine_job_experiance)
    await job_experince_div.press('Enter')


async def main():
    """
    Scrapes job data from the Shine website using Playwright, processes it,
    and saves it to the database and JSON files.
    """
    try:
        async with async_playwright() as p:
            # Launch the browser
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            await page_loader(page)

            pagewise = []
            await main_iterator(page, pagewise, context)

            await browser.close()

    except Exception as e:
        logger.error(f"Error in main: {e}")


# Run the main function asynchronously
asyncio.run(main())
