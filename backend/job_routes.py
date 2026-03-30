from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from database import get_db
from auth import require_hr, get_current_user
import models

router = APIRouter(tags=["Jobs"])


class JobCreate(BaseModel):
    title:               str
    description:         str
    sector:              str
    education_required:  str
    skills_required:     str
    experience_required: str


@router.post("/create_job")
def create_job(
    job: JobCreate,
    db:  Session = Depends(get_db),
    current_user: models.User = Depends(require_hr)
):
    if not current_user.company_name:
        raise HTTPException(
            status_code=400,
            detail="Your account has no company name. Please contact support."
        )

    duplicate = db.query(models.Job).filter(
        models.Job.title       == job.title.strip(),
        models.Job.description == job.description.strip(),
        models.Job.posted_by   == current_user.id
    ).first()
    if duplicate:
        raise HTTPException(status_code=400, detail="This job is already posted")

    try:
        db_job = models.Job(
            title               = job.title.strip(),
            description         = job.description.strip(),
            sector              = job.sector,
            company_name        = current_user.company_name,  
            education_required  = job.education_required,
            skills_required     = job.skills_required.strip(),
            experience_required = job.experience_required.strip(),
            posted_by           = current_user.id
        )
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")

    return {
        "message": "Job posted successfully",
        "job_id":  db_job.job_id
    }


@router.get("/jobs")
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(models.Job).all()
    return [
        {
            "job_id":              j.job_id,
            "title":               j.title,
            "company_name":        j.company_name,
            "description":         j.description,
            "sector":              j.sector,
            "education_required":  j.education_required,
            "skills_required":     j.skills_required,
            "experience_required": j.experience_required,
            "posted_by":           j.posted_by,
        }
        for j in jobs
    ]


@router.get("/job/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id":              job.job_id,
        "title":               job.title,
        "company_name":        job.company_name,
        "description":         job.description,
        "sector":              job.sector,
        "education_required":  job.education_required,
        "skills_required":     job.skills_required,
        "experience_required": job.experience_required,
    }


@router.get("/filter_candidates")
def filter_candidates(
    education:  Optional[str] = Query(None),
    sector:     Optional[str] = Query(None),
    skill:      Optional[str] = Query(None),
    experience: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_hr)
):
    query = (
        db.query(models.Application, models.Job, models.User)
        .join(models.Job,  models.Application.job_id       == models.Job.job_id)
        .join(models.User, models.Application.candidate_id == models.User.id)
    )
    if education:  query = query.filter(models.Job.education_required.ilike(f"%{education}%"))
    if sector:     query = query.filter(models.Job.sector.ilike(f"%{sector}%"))
    if skill:      query = query.filter(models.Job.skills_required.ilike(f"%{skill}%"))
    if experience: query = query.filter(models.Job.experience_required.ilike(f"%{experience}%"))

    response = []
    for application, job, user in query.all():
        score_rec = db.query(models.MatchScore).filter(
            models.MatchScore.candidate_id == user.id,
            models.MatchScore.job_id       == job.job_id
        ).first()
        response.append({
            "application_id":     application.id,
            "candidate_name":     user.name,
            "candidate_email":    user.email,
            "job_title":          job.title,
            "company_name":       job.company_name,
            "sector":             job.sector,
            "education_required": job.education_required,
            "skills_required":    job.skills_required,
            "application_status": application.status,
            "ai_score":           round(score_rec.score, 2) if score_rec else "Not screened",
        })
    return {"count": len(response), "candidates": response}


@router.put("/shortlist/{application_id}")
def shortlist(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_hr)
):
    app = db.query(models.Application).filter(models.Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    app.status = "shortlisted"
    db.commit()
    return {"message": "Candidate shortlisted"}


@router.put("/reject/{application_id}")
def reject(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_hr)
):
    app = db.query(models.Application).filter(models.Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    app.status = "rejected"
    db.commit()
    return {"message": "Candidate rejected"}