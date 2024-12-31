from pydantic import BaseModel, HttpUrl
from typing import Optional

class JobBase(BaseModel):
    platform: Optional[str] = None
    platform_link: Optional[HttpUrl] = None
    job_title: Optional[str] = None
    job_link: HttpUrl = None
    company: Optional[str] = None
    company_link: Optional[str] = None
    posted_on: Optional[str] = None
    position: Optional[str] = None
    salary: Optional[str] = None
    duration: Optional[str] = None
    applicant: Optional[str] = None
    last_updated: Optional[str] = None
    job_description: Optional[str] = None
    experience_level: Optional[str] = None
    location: Optional[str] = None
    opening:Optional[str] = None
    last_date_application: Optional[str] = None
    industry : Optional[str] = None
    job_type : Optional[str] = None
    industry_function : Optional[str] = None
    skill_list : Optional[str] = None
    early_applicant : Optional[str] = None
    job_id : Optional[str] = None
    job_role : Optional[str] = None
    interview_process : Optional[str] = None
    education : Optional[str] = None
    specialization : Optional[str] = None

    # class Config:
    #     orm_mode = True  # Enables compatibility with SQLAlchemy models
