from sqlalchemy import Column, Integer, String, Text
from datetime import datetime
from models.database import Base


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    platform = Column(String(50), nullable=True)  # Job platform (ensure this is unique)
    platform_link = Column(String(255), nullable=True)  # Link to the platform (ensure this is unique)
    job_title = Column(String(250), nullable=True)  # Job title (removed unique constraint if not needed)
    job_link = Column(Text)  # Link to the job post
    company = Column(String(120), nullable=True)  # Company name
    company_link = Column(Text, nullable=True)  # Company website
    posted_on = Column(String(255), nullable=True)  # Date the job was posted
    position = Column(String(100), nullable=True)  # Job position
    salary = Column(String(50), nullable=True)  # Salary (can be a range or text)
    duration = Column(String(50), nullable=True)  # Duration (e.g., "Full-time", "Part-time")
    applicant = Column(String(100), nullable=True)  # Number of applicants
    last_updated = Column(String(255), default=datetime.utcnow, onupdate=datetime.utcnow)  # Timestamp of the last update
    job_description = Column(Text, nullable=True)  # Detailed job description
    experience_level = Column(String(50), nullable=True)  # Required experience level
    location = Column(String(100), nullable=True)  # Job location
    last_date_application = Column(String(250), nullable=True)  # Last date to apply
    opening = Column(String(50), nullable=True)
    industry = Column(String(150), nullable=True)
    job_type = Column(String(100), nullable=True)
    industry_function = Column(Text, nullable=True)
    skill_list =  Column(Text, nullable=True)
    early_applicant = Column(String(50), nullable=True)
    job_id = Column(String(50), nullable=True)
    job_role = Column(String(150), nullable=True)
    interview_process = Column(String(100), nullable=True)
    education = Column(String(250), nullable=True)
    specialization = Column(String(200), nullable=True)
