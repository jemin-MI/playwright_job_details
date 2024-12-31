import asyncio
import datetime
import json
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

        job_title = 'Intern'
        job_location = 'Worldwide'

        await page.goto(f"https://www.naukri.com/intern-jobs?k={job_title}", wait_until="domcontentloaded")
        await page.wait_for_timeout(4000)

        page_count = 2
        pagewise = []
        for k in range(page_count):

            main_div = page.locator("#listContainer")
            second_div = main_div.locator("> div").nth(1)
            inner_div = second_div.locator("> div")
            sub_divs = inner_div.locator("> div")
            sub_div_count = await sub_divs.count()

            data_list = []
            for i in range(sub_div_count):

                try:
                    sub_div = sub_divs.nth(i)  # Get the i-th <sub div>
                    job_div = sub_div.locator('a.title')
                    link = await job_div.get_attribute('href')
                    job_title = await job_div.inner_text() or 'Not Found'
                    comp_name_div = sub_div.locator('a.comp-name')
                    company = await comp_name_div.inner_text() or 'Not Found'
                    company_url = await comp_name_div.get_attribute('href') or 'Not Found'
                    await page.goto(link)
                except:
                    continue

                job_type_ = 'Not found'
                last_date = 'Not found'
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
                    print("jobt type------------", job_type_)

                except:
                    pass
                applicants = 'Not Found'
                opening = 'Not Found'
                try:
                    main_second_div = sub_page_main_div.locator("> div").nth(1)
                    sub_second_div = main_second_div.locator("> div").nth(0)
                    sub_span_list = sub_second_div.locator('> span')

                    posted_on = await sub_span_list.nth(0).locator('span').inner_text() or 'Not Found'
                    opening = await sub_span_list.nth(1).locator('span').inner_text() or 'Not Found'
                    applicants = await sub_span_list.nth(2).locator('span').inner_text() or 'Not Found'
                except:
                    pass

                try:
                    script_tag = page.locator('script[type="application/ld+json"]')
                    # Iterate through all matching script tags (if there are multiple)
                    script_content = await script_tag.nth(0).inner_text()
                    json_data = json.loads(script_content)
                    description = json_data.get("description", "Description not found")
                    job_description = html_to_text(description)
                except:
                    pass

                data_dict = {
                    "platform": "Naukari",
                    "platform_link": "https://www.naukri.com/",
                    "company": company or None,
                    "company_link": company_url or None,
                    "job_title": job_title or None,
                    "job_link": link,
                    "location": job_location or None,
                    "job_type": job_type_ or None,
                    "duration": duration or None,
                    "salary": salary or None,
                    "last_date_application": last_date or None,
                    "posted_on": f"{posted_on} as per the {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} or None",
                    "applicant": applicants or None,
                    "opening": opening or None,
                    "job_description": job_description or None
                }
                add_data_db(data_dict)
                breakpoint()
                data_list.append(data_dict)
                with open('naukari_data.json', 'w') as file:
                    file.write(json.dumps(data_list))
                # add_data_db(data_dict)

                await page.go_back()
                await page.wait_for_timeout(3000)

        pagewise.append({'page_' + str(k + 1): data_list})
        with open('page_wose_naukari.json', 'w') as file:
            file.write(json.dumps(pagewise))

        icons = page.locator('.ni-icon-arrow-2')
        icon_count = await icons.count()

        if icon_count > 1 and page_count > 1:
            # Get the second icon (index 1) and click it
            second_icon = icons.nth(1)
            await second_icon.click()
            print("Clicked the second icon.")
        else:
            print("Second icon not found.")
        await browser.close()


asyncio.run(main())
