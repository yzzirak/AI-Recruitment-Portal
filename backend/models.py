from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String(100), nullable=False)
    email        = Column(String(150), unique=True, index=True, nullable=False)
    password     = Column(String(255), nullable=False)
    role         = Column(String(20),  nullable=False)       
    company_name = Column(String(200), nullable=True)        
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    jobs_posted  = relationship("Job",         back_populates="poster")
    applications = relationship("Application", back_populates="candidate")
    match_scores = relationship("MatchScore",  back_populates="candidate")


class Job(Base):
    __tablename__ = "jobs"

    job_id              = Column(Integer, primary_key=True, index=True)
    title               = Column(String(200), nullable=False)
    description         = Column(Text,        nullable=False)
    sector              = Column(String(100), nullable=False)
    company_name        = Column(String(200), nullable=False)   
    education_required  = Column(String(100), nullable=False)
    skills_required     = Column(Text,        nullable=False)
    experience_required = Column(String(50),  nullable=False)
    posted_by           = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at          = Column(DateTime(timezone=True), server_default=func.now())

    poster       = relationship("User",        back_populates="jobs_posted")
    applications = relationship("Application", back_populates="job")
    match_scores = relationship("MatchScore",  back_populates="job")


class Application(Base):
    __tablename__ = "applications"

    id           = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"),     nullable=False)
    job_id       = Column(Integer, ForeignKey("jobs.job_id"),  nullable=False)
    resume_path  = Column(String(500), nullable=False)
    status       = Column(String(50),  default="applied")      # applied | shortlisted | rejected
    applied_at   = Column(DateTime(timezone=True), server_default=func.now())

    candidate = relationship("User", back_populates="applications")
    job       = relationship("Job",  back_populates="applications")

class MatchScore(Base):
    __tablename__ = "match_scores"

    id           = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"),    nullable=False)
    job_id       = Column(Integer, ForeignKey("jobs.job_id"), nullable=False)
    score        = Column(Float, nullable=False)               # 0.0 – 100.0
    screened_at  = Column(DateTime(timezone=True), server_default=func.now())

    candidate = relationship("User", back_populates="match_scores")
    job       = relationship("Job",  back_populates="match_scores")