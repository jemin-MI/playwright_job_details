import asyncio
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

        # with open("linkedin_cookie.json", "r") as f:
        #     cookies = json.loads(f.read())

        await page.goto(f"https://www.freshersworld.com/jobs/jobsearch", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        job_type = 'intern'
        course = ''
        job_location = ''
        page_count = 2
        # input_toggle_div = page.locator('.searchJobs')
        # await input_toggle_div.click()

        await page.click("#seach-new-bar")
        await page.wait_for_timeout(1500)

        await page.fill('#keyword', job_type)
        select_course = page.locator('#course_id1')
        await select_course.select_option(course)
        await page.fill('#job_location', job_location)

        job_location_div = page.locator('#job_location')
        await job_location_div.press('Enter')
        await page.wait_for_timeout(7500)

        pagewise = []
        for current_page in range(page_count):

            main_div = page.locator('#sort-jobs')
            sub_divs = main_div.locator('> div.job-container')
            count = await sub_divs.count()

            data_list = []
            for i in range(count):
                job_display_url = await sub_divs.nth(i).get_attribute("job_display_url")

                job_page = await context.new_page()
                await job_page.goto(job_display_url, wait_until="domcontentloaded")
                await job_page.wait_for_timeout(4500)

                job_body_div = job_page.locator('div.job-body')
                if await job_body_div.count() > 0:
                    job_role = await job_body_div.locator('.job-role').inner_text()
                    company = await job_body_div.locator('.company-name').inner_text()

                    await job_page.wait_for_selector(".experience-and-salary-block")

                    experience_text = await job_page.locator(".experience .space").inner_text()
                    salary_text = await job_page.locator(".salary .space").inner_text()
                    location_block = job_body_div.locator('.location')
                    a_tags = location_block.locator('a')
                    a_tag_texts = []

                    for k in range(await a_tags.count()):
                        a_tag = a_tags.nth(k)  # Get the i-th <a> tag
                        text_content = await a_tag.text_content()  # Get the text content of the <a> tag
                        a_tag_texts.append(text_content)  # Add the text content to the list

                    posted_on_div = job_body_div.locator('.posted-on')
                    span_tags = posted_on_div.locator('span')
                    posted_on = await span_tags.nth(1).inner_text()
                    job_desc_div = job_page.locator('.job-desc')
                    job_desc_html = await job_desc_div.inner_html()
                    description = html_to_text(job_desc_html)
                    main_section = job_page.locator('.job-detail-section')

                    # Locate all 'job-part-block' elements within the main section
                    job_part_blocks = main_section.locator('.job-part-block')
                    block_count = await job_part_blocks.count()

                    # Initialize variables
                    education = ''
                    process = ''
                    employment_type = ''
                    job_id = ''

                    # Iterate through each block and extract the title and detail
                    for b in range(block_count):
                        # Get the title from the job-part-head span
                        title_locator = job_part_blocks.nth(b).locator('.job-part-head')
                        detail_locator = job_part_blocks.nth(b).locator('.job-part-detail')

                        # Extract text content
                        title = (await title_locator.text_content() or '').strip()
                        detail = (await detail_locator.text_content() or '').strip()

                        # Assign values to the appropriate variables
                        if title and detail:
                            if title == "Education":
                                education = detail
                            elif title == "Hiring Process":
                                process = detail
                            elif title == "Employment Type":
                                employment_type = detail
                            elif title == "Job Id":
                                job_id = detail
                            elif title == "Job Category":
                                job_category = detail

                    data_dict = {"platform": "Freshers",
                                 "platform_link": "https://www.freshersworld.com/", 'job_title': job_role,
                                 'company': company, 'salary': salary_text, 'education': education,
                                 # 'industry': job_category,
                                 'experience_text': experience_text, 'location': str(a_tag_texts),
                                 'interview_process': process,
                                 'posted_on': posted_on, 'description': description,
                                 'job_type': employment_type, 'job_id': job_id}
                    add_data_db(data_dict)
                    breakpoint()
                    data_list.append(data_dict)

                    with open('freshers_data.json', 'w') as file:
                        file.write(json.dumps(data_list))

                    await job_page.close()

            current_page += 1
            pagewise.append({"page" + str(current_page): data_list})

            with open('page_wise_freshers.json', 'w') as file:
                file.write(json.dumps(pagewise))

            ## checking for the paginations
            next_page_div = page.locator('li.paginate_button.next')
            if await next_page_div.count() > 0 and page_count > 1:
                await next_page_div.locator("a").click()

    await browser.close()


asyncio.run(main())
