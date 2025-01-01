import asyncio
import json
import re
import logging
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from contants_dir.constant import TimesJob_link, TimesJob, input_job_role, page_count
from models.database import SessionLocal
from schema.pydentic import JobBase
from models.model import Job

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        industry_function=data_list_pydantic.industry_function,
        skill_list=data_list_pydantic.skill_list,
        early_applicant=data_list_pydantic.early_applicant,
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


def clean_string(value):
    # Remove leading and trailing whitespace and extra newlines/spaces
    return re.sub(r'\s+', ' ', value.strip())


async def main():
    async with async_playwright() as p:
        # Launch the browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        try:
            with open("times_cookie.json", "r") as f:
                cookies = json.load(f)
                await context.add_cookies(cookies)  # Add cookies to the context
                logger.info("Cookies loaded successfully.")
        except FileNotFoundError:
            logger.warning("Cookie file not found. Proceeding without cookies.")
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from the cookie file.")

        page = await context.new_page()

        await page.goto(TimesJob_link, wait_until="domcontentloaded")
        await page.wait_for_timeout(4000)

        await page.fill('#txtKeywords', input_job_role)

        await page.locator('#quickSearchBean .common-btn').press('Enter')
        await page.wait_for_timeout(5500)

        page_list = []

        for k in range(page_count):

            link_list = []
            ul = page.locator("ul.new-joblist")
            # Get all the `li` elements within the `ul`
            list_items = ul.locator("li.clearfix.job-bx.wht-shd-bx")
            li_count = await list_items.count()  # Get the number of `li` elements

            data_list = []
            for i in range(li_count):
                h2 = list_items.nth(i).locator("h2.heading-trun")
                href = await h2.locator("a").get_attribute("href")
                link_list.append(href)

            link_c = 0
            for link in link_list:
                link_c += 1
                await page.goto(link)
                await page.wait_for_timeout(3500)

                await page.wait_for_selector(
                    ".jd-company-details")  # Wait for the element with class `jd-company-details`

                company = page.locator('.jd-company-details')
                company_name_locator = company.locator("h2 a")
                company_name = await company_name_locator.inner_text() if await company_name_locator.count() > 0 else "Not found"
                company_url = await company_name_locator.get_attribute(
                    "href") if await company_name_locator.count() > 0 else "Not found"
                job_title = await page.locator('.jd-job-title').inner_text()
                posted_on = company.locator('span.posted-days')
                posted_on_text = await posted_on.inner_text() if await posted_on.count() > 0 else "Not found"

                job_list = company.locator("ul.top-jd-dtl")

                # Get the list of li elements
                list_items = job_list.locator("li")
                experiance = await list_items.nth(0).inner_text() if await list_items.nth(
                    0).count() > 0 else "Not found"
                salary = await list_items.nth(1).inner_text() if await list_items.nth(1).count() > 0 else "Not found"

                location = await company.locator(
                    ".location-text__ .job-location-trunicate").inner_text() if await company.locator(
                    ".location-text__ .job-location-trunicate").count() > 0 else "Not found"
                applicant = await page.locator(".walkin-details").inner_text() if await page.locator(
                    ".walkin-details").count() > 0 else "Not found"

                description_div = await page.locator(".jd-desc.job-description-main").inner_html()
                job_description = html_to_text(description_div) if description_div else "Not found"

                job_function = 'Not found'
                industry = 'Not found'
                specialization = 'Not found'
                qualification = 'Not found'
                employment = 'Not found'

                job_basic_info = page.locator('.job-basic-info ul')
                job_basic = job_basic_info.locator('li.clearfix')
                li_count = await job_basic.count()

                for i in range(li_count):
                    label = await job_basic.nth(i).locator("label").text_content() if await job_basic.nth(i).locator(
                        "label").count() > 0 else "Not found"
                    value = await job_basic.nth(i).locator("span").text_content() if await job_basic.nth(i).locator(
                        "span").count() > 0 else "Not found"

                    # If value is within a nested ul, extract all values from it
                    if value == "Not found":  # If value is "Not found", it means we have a nested ul for "Qualification"
                        nested_list = await job_basic.nth(i).locator("span.basic-info-dtl ul").locator("li")
                        nested_values = []
                        nested_count = await nested_list.count()
                        for j in range(nested_count):
                            nested_values.append(await nested_list.nth(j).text_content())
                        value = ", ".join(nested_values) if nested_values else "Not found"

                    # Check if the variable is blank and replace with the new value
                    if label and value != "Not found":  # Ensure both label and value are not empty
                        if "Job Function" in label and job_function == 'Not found':
                            industry_function = clean_string(value)
                        elif "Industry" in label and industry == 'Not found':
                            industry = clean_string(value)
                        elif "Specialization" in label and specialization == 'Not found':
                            specialization = clean_string(value)
                        elif "Qualification" in label and qualification == 'Not found':
                            qualification = clean_string(value)
                        elif "Employment Type" in label and employment == 'Not found':
                            employment = clean_string(value)

                job_skills_div = page.locator("div.jd-sec.job-skills.clearfix")
                skill_tags = job_skills_div.locator("span.jd-skill-tag")
                skill_count = await skill_tags.count()

                skills = []
                for j in range(skill_count):
                    skill_name = await skill_tags.nth(j).locator("a").text_content() if await skill_tags.nth(j).locator(
                        "a").count() > 0 else "Not found"
                    skills.append(skill_name)

                data_dict = {
                    'platform': TimesJob,
                    'platform_link': TimesJob_link,
                    'job_title': job_title,
                    'job_link': link,
                    'company': company_name,
                    'company_link': company_url,
                    'posted_on': posted_on_text,
                    'location': location,
                    'salary': salary,
                    'applicant': applicant,
                    'job_description': job_description,
                    'industry_function': industry_function,
                    'industry': industry,
                    'specialization': specialization,
                    'education': qualification,
                    'job_type': employment,
                    'skill_list': ', '.join(map(str, skills)),
                }
                add_data_db(data_dict)
                data_list.append(data_dict)

                await page.go_back()
                with open('data_times.json', 'w') as file:
                    file.write(json.dumps(data_list))  # Writes JSON with indentation for readability

            page_list.append({'page_' + str(k + 1): data_list})

            pagination_div = page.locator('.srp-pagination em')
            if await pagination_div.count() > 1 and page_count > 1:
                await pagination_div.nth(1).click()
                await page.wait_for_timeout(3000)

                logger.info("New page clicked")
            with open(f'pagewise_{TimesJob}.json', 'w') as file:
                file.write(json.dumps(page_list))

        await browser.close()

# Run the script
asyncio.run(main())
