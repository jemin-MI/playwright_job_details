import asyncio
import json
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
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


async def main():
    async with async_playwright() as p:
        # Launch the browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # with open("linkedin_cookie.json", "r") as f:
        #     cookies = json.loads(f.read())

        await page.goto(f"https://www.shine.com/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        job_type = 'Intern'
        job_location = 'Worldwide'
        job_experiance = ''
        page_count = 2

        input_toggle_div = page.locator('#webSearchBar')
        await input_toggle_div.click()
        await page.fill('#id_q', job_type)
        await page.fill('#id_loc', job_location)
        job_experince_div = page.locator('#id_exp')
        await job_experince_div.fill(job_experiance)
        await job_experince_div.press('Enter')

        pagewise = []
        current_page = 0
        for k in range(page_count):

            # Ensure the href is not None
            await page.wait_for_timeout(2000)
            script_tag = page.locator('script#\\__NEXT_DATA__')
            script_content = await script_tag.text_content()

            # Print the content
            data_dict = json.loads(script_content)
            main_dict = data_dict['props']['pageProps']['initialState']['jsrp']['searchresult']['data']['results']

            data_list = []
            for i in main_dict:
                company_name = i['jCName']
                job_title = i['jJT']
                job_id = i['id']
                job_link = 'https://www.shine.com/job-search/' + i['jSlug']
                job_location = i['jLoc']
                posted_on = i['jPDate']
                required_experiance = i['jExp']

                url = f'https://www.shine.com/api/v2/search/job-description/{job_id}/'
                response = requests.get(url)
                data = response.json()
                await page.wait_for_timeout(1500)

                job_description = html_to_text(data['results'][0]['jJD'])
                required_skills = data['results'][0]['jKwd']
                job_area = data['results'][0]['jArea']
                min_salary = data['results'][0]['min_salary']
                max_salary = data['results'][0]['max_salary']

                data_dict = {
                    "platform": "Shine",
                    "platform_link": "https://www.shine.com/",
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
                add_data_db(data_dict)
                breakpoint()
                data_list.append(data_dict)
                with open('shine_data.json', 'w') as file:
                    file.write(json.dumps(data_list))
            current_page += 1
            page_dict = {current_page: data_list}
            pagewise.append(page_dict)

            with open('shine_page_wise.json', 'w') as page_file:
                page_file.write(json.dumps(pagewise))

            left_panel = page.locator('.jsrp_leftPanel > div')
            second_div = left_panel.nth(1).locator('a').last

            if await second_div.is_visible():
                await second_div.click()
            else:
                print("Last <a> tag not found or not visible.")

    await browser.close()


asyncio.run(main())
