import asyncio
import json
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from contants_dir.constant import input_job_role, input_job_location, page_count, Foundit_link, Foundit
from models.database import SessionLocal
from schema.pydentic import JobBase
from models.model import Job


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


def html_to_text(html_content):
    """
    Converts HTML content to plain text.

    Args:
        html_content (str): HTML string to convert.

    Returns:
        str: Plain text extracted from the HTML.
    """
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

async def navigate_to_search_page(page):
    await page.goto(Foundit_link, wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)

    await page.fill('#heroSectionDesktop-skillsAutoComplete--input', input_job_role)
    await page.fill('#heroSectionDesktop-locationAutoComplete--input', input_job_location)
    if input_job_location != '':
        await page.evaluate("""
            document.querySelector('#heroSectionDesktop-expAutoComplete--input').value = '1 Years';
        """)

    form_div = page.locator('#searchForm')
    submit_button = form_div.locator('.search_submit_btn').nth(0)
    await submit_button.click()
    await page.wait_for_timeout(5000)

async def scrape_job_data(page):
    pagewise = []
    for current_page in range(page_count):

        data_list = []
        main_div = page.locator('.srpResultCard .srpResultCardContainer')
        count = await main_div.count()
        await page.wait_for_timeout(4000)

        for i in range(count):
            data_dict = await scrape_job_card(page, main_div.nth(i))
            data_list.append(data_dict)
            add_data_db(data_dict)

        current_page += 1
        pagewise.append({"page" + str(current_page): data_list})

        # Save page-wise data to JSON
        with open(f'page_wise_{Foundit}.json', 'w') as file:
            file.write(json.dumps(pagewise))

        # Handle pagination
        if await page.locator('.arrow-right.disabled').count() > 0:
            break
        else:
            pagination = page.locator('.pagination .arrow-right')
            if await pagination.count() > 0 and page_count > 1:
                await pagination.click()
        await page.wait_for_timeout(5000)

async def scrape_job_card(page, card):
    await card.click()
    await page.wait_for_timeout(1500)

    job_title = await page.locator('.jdTitle').inner_text()
    company_name = await page.locator('.jdCompanyName').inner_text()

    label_text = ''
    job_label = page.locator('.jobLabelContainer')
    if await job_label.count() > 0:
        label_text = await job_label.locator('.jobLabels .labelText').inner_text()

    bullets_div = page.locator('.bulletText ul.text-list')
    li_elements = bullets_div.locator('li span')
    applicant = await li_elements.nth(1).inner_text()

    highlights = page.locator('.jdHighlights')
    experiance = (await highlights.locator('.highlightsRow').nth(0).inner_text()).replace('Exp: ', '')
    location = await highlights.locator('.highlightsRow').nth(1).inner_text()

    description_html = await page.locator('.jobDescInfoNew').inner_html()
    description_text = html_to_text(description_html)

    info_container = page.locator('.infoContainer p')
    industry = await info_container.nth(0).locator('span').nth(1).inner_text()
    industry_function = await info_container.nth(1).locator('span').nth(1).inner_text()
    job_type = await info_container.nth(2).locator('span').nth(1).inner_text()

    skills_container = page.locator('.pillsContainer .pillItem')
    skill_list = [await skills_container.nth(s).inner_text() for s in range(await skills_container.count())]

    report_job = page.locator('.reportJobContainer')
    posted_on = await report_job.locator('p').nth(0).inner_text()
    job_id = await report_job.locator('p').nth(1).inner_text()

    return {
        "platform": Foundit,
        "platform_link": Foundit_link,
        'job_title': job_title, 'company': company_name,
        'early_applicant': "Yes" if label_text else "No", 'location': location,
        'posted_on': posted_on, 'applicant': applicant, 'experience_level': experiance,
        'industry': industry, 'industry_function': industry_function, 'job_type': job_type,
        'skill_list': ', '.join(skill_list), 'job_id': job_id, 'job_description': description_text
    }

async def main():

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await navigate_to_search_page(page)
        await scrape_job_data(page)

        await browser.close()


asyncio.run(main())
