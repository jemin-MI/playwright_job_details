import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright
from models.database import SessionLocal
from schema.pydentic import JobBase
from models.model import Job
from contants_dir.constant import Linkedin, Linkedin_link, input_job_location, input_job_role, Linkedin_search, Linkedin_job_link, page_count
from job_details.web_logger import ini_logger

logger = ini_logger("WebsiteScraper")


def add_data_db(data_dict):
    session = SessionLocal()
    data_list_pydantic = JobBase(**data_dict)

    # Step 2: Map Pydantic model to SQLAlchemy model
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

    # Step 3: Add to session and commit
    session.add(job_data)
    session.commit()
    session.refresh(job_data)


async def navigate_to_search_page(page, context):
    with open("linkedin_cookie.json", "r") as f:
        cookies = json.loads(f.read())

    await context.add_cookies(cookies)
    await page.wait_for_timeout(2000)
    await page.goto(Linkedin_search, wait_until="domcontentloaded")

    await page.wait_for_timeout(3000)

    job_li = page.locator("li.global-nav__primary-item:has(span:has-text('Jobs'))")
    await job_li.click()

    await page.wait_for_timeout(3000)
    await page.fill('.jobs-search-box__keyboard-text-input', input_job_role)
    await page.wait_for_timeout(1000)
    await page.press('.jobs-search-box__keyboard-text-input', 'Enter')
    await page.wait_for_timeout(2000)

    await page.fill('.jobs-search-box__text-input--with-clear', input_job_location)
    await page.wait_for_timeout(1000)
    await page.press('.jobs-search-box__text-input--with-clear', 'Enter')
    await page.wait_for_timeout(3000)


async def get_company_and_title(page, data_dict):
    company_div = page.locator('.job-details-jobs-unified-top-card__company-name')
    a_tag_company = company_div.locator('a')
    company_name = await a_tag_company.inner_text()
    company_link = await a_tag_company.get_attribute('href')

    cm_div = page.locator('.job-details-jobs-unified-top-card__job-title')
    a_tag = cm_div.locator('a')
    job_title = await a_tag.inner_text()
    job_href = await a_tag.get_attribute('href')

    data_dict["company"] = company_name
    data_dict["company_link"] = company_link
    data_dict["job_title"] = job_title
    data_dict["job_href"] = job_href

    return data_dict


async def get_job_location_time(direct_child_divs, data_dict):
    job_location_span = direct_child_divs.nth(2).locator('span')
    all_span_text = await job_location_span.all_inner_texts()
    cleaned_text = [text.strip() for text in all_span_text if text.strip()]
    filtered_data = [text.strip() for text in cleaned_text if text.strip() != '·']

    seen = set()
    job_meta_data = [item for item in filtered_data if not (item in seen or seen.add(item))]

    job_location = job_meta_data[0]
    job_posted = f"{job_meta_data[1]} as per the {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    applicant_count = job_meta_data[-1]

    data_dict["location"] = job_location
    data_dict["posted_on"] = job_posted
    data_dict["applicant"] = applicant_count

    return data_dict


async def get_job_type(direct_child_divs, data_dict):
    ul_element = direct_child_divs.nth(3).locator('ul')
    first_li = ul_element.locator('li')
    span_elements = first_li.locator('span')
    span_tag = span_elements.nth(0).nth(0)
    nested_span_elements = span_tag.locator('span')

    job_data_list = []
    span_count = await nested_span_elements.count()
    for j in range(span_count):
        span = nested_span_elements.nth(j)
        text = await span.inner_text()
        job_data_list.append(text.strip())

    job_location = 'Not Found'
    job_type = 'Not Found'
    experience_level = 'Not Found'

    if 'remote' in job_data_list:
        job_location = 'Remote'
    if 'On-site' in job_data_list:
        job_location = 'On-site'
    if 'Hybrid' in job_data_list:
        job_location = 'Hybrid'

    if 'Full-time' in job_data_list:
        job_type = 'Full-time'
    if 'Contract' in job_data_list:
        job_type = 'Contract'
    if 'Volunteer' in job_data_list:
        job_type = 'Volunteer'
    if 'Internship' in job_data_list:
        job_type = 'Internship'
    if 'Temporary' in job_data_list:
        job_type = 'Temporary'
    if 'Part-time' in job_data_list:
        job_type = 'Part-time'
    if 'Others' in job_data_list:
        job_type = 'Others'

    if 'Associate' in job_data_list:
        experience_level = 'Associate'
    if 'Mid-Senior level' in job_data_list:
        experience_level = 'Mid-Senior level'
    if 'Entry level' in job_data_list:
        experience_level = 'Entry level'
    if 'Director' in job_data_list:
        experience_level = 'Director'
    if 'Executive' in job_data_list:
        experience_level = 'Executive'
    if 'Internship' in job_data_list and job_data_list[-1] == 'Internship':
        experience_level = 'Internship'

    data_dict["job_type"] = job_type
    data_dict["experience_level"] = experience_level

    return data_dict


async def get_job_desc(page, data_dict):
    await page.wait_for_selector('article.jobs-description__container')
    job_desc_div = page.locator('article.jobs-description__container')
    job_description = await job_desc_div.inner_text()
    formatted_description = " ".join(line.strip() for line in job_description.splitlines() if line.strip())

    data_dict["job_description"] = formatted_description
    return data_dict


async def pagination_setup(pagewise, current_page, data_list, page):
    pagewise.append({'page_' + str(current_page + 1): data_list})

    with open(f'pagewise_{Linkedin}.json', 'w') as file:
        file.write(json.dumps(pagewise))

    pagination_div = page.locator('.jobs-search-pagination')
    next_button = pagination_div.locator('.jobs-search-pagination__button--next')

    if await next_button.count() > 0 and page_count > 1:
        await next_button.click()
    else:

        logger.info("Next button not found or not visible.")


async def main():
    async with async_playwright() as p:
        # Launch the browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await navigate_to_search_page(page, context)

        pagewise = []
        for current_page in range(page_count):
            await page.wait_for_selector('.scaffold-layout__list-item')  # Wait for job items to appear
            job_lists_li = page.locator("li.ember-view.scaffold-layout__list-item")
            job_count = await job_lists_li.count()

            data_list = []
            for i in range(job_count):
                await job_lists_li.nth(i).click()
                await page.wait_for_timeout(3000)
                await page.wait_for_selector('div.job-details-jobs-unified-top-card__container--two-pane')
                parent_div = page.locator("div.job-details-jobs-unified-top-card__container--two-pane")
                main_div = parent_div.locator("> div")
                direct_child_divs = main_div.locator("> div")

                data_dict = {}
                await get_company_and_title(page, data_dict)
                await get_job_location_time(direct_child_divs, data_dict)
                await get_job_type(direct_child_divs, data_dict)
                await get_job_desc(page, data_dict)

                data_dict["platform"] = Linkedin
                data_dict["platform_link"] = Linkedin_link
                data_dict["job_link"] = Linkedin_job_link + data_dict["job_href"]

                add_data_db(data_dict)
                data_list.append(data_dict)

                with open('linked_data.json', 'w') as file:
                    file.write(json.dumps(data_list))

            await pagination_setup(pagewise, current_page, data_list, page)

        await browser.close()


asyncio.run(main())
