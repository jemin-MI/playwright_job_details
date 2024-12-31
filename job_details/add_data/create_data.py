
from models import SessionLocal
from schema.pydentic import JobBase
from models import Job



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
        industry= data_list_pydantic.industry,
        job_type =  data_list_pydantic.job_type,
        industry_function =  data_list_pydantic,
        skill_list = data_list_pydantic,
        early_applicant =  data_list_pydantic.industry_function,
        job_id =  data_list_pydantic.job_id,
        job_role =  data_list_pydantic.job_role,
        interview_process =  data_list_pydantic.interview_process,
        education =  data_list_pydantic.education,
        specialization =  data_list_pydantic.specialization,
    )

    # Step 3: Add to session and commit
    session.add(job_data)
    session.commit()
    session.refresh(job_data)