"""
application_routes.py
Applications — HR sees only applicants for their own jobs.
"""
import os, shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db
from auth import require_candidate, get_current_user
import models

router = APIRouter(tags=["Applications"])

RESUME_DIR  = "uploads/resumes"
ALLOWED_EXT = {".pdf", ".docx"}
os.makedirs(RESUME_DIR, exist_ok=True)


@router.post("/apply_job")
async def apply_job(
    job_id: int = Form(...),
    resume: UploadFile = File(...),
    db:     Session = Depends(get_db),
    current_user: models.User = Depends(require_candidate)
):
    # Job must exist
    job = db.query(models.Job).filter(models.Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Valid file type
    ext = os.path.splitext(resume.filename)[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX resumes accepted")

    # No duplicate applications
    if db.query(models.Application).filter(
        models.Application.candidate_id == current_user.id,
        models.Application.job_id       == job_id
    ).first():
        raise HTTPException(status_code=400, detail="You have already applied for this job")

    # Save resume — candidate_id_job_id.ext
    filename  = f"{current_user.id}_{job_id}{ext}"
    file_path = os.path.join(RESUME_DIR, filename)
    with open(file_path, "wb") as buf:
        shutil.copyfileobj(resume.file, buf)

    application = models.Application(
        candidate_id = current_user.id,
        job_id       = job_id,
        resume_path  = file_path,
        status       = "applied"
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    return {
        "message":        "Application submitted successfully",
        "application_id": application.id,
        "job_id":         job_id,
        "status":         "applied"
    }


@router.get("/my_applications")
def my_applications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_candidate)
):
    """Candidate view — status only, no AI score."""
    rows = (
        db.query(models.Application, models.Job)
        .join(models.Job, models.Application.job_id == models.Job.job_id)
        .filter(models.Application.candidate_id == current_user.id)
        .all()
    )
    return {
        "applications": [
            {
                "application_id": app.id,
                "job_id":         job.job_id,
                "job_title":      job.title,
                "company_name":   job.company_name,
                "sector":         job.sector,
                "status":         app.status,
                "applied_at":     str(app.applied_at),
            }
            for app, job in rows
        ]
    }


@router.get("/job_applicants/{job_id}")
def job_applicants(
    job_id: int,
    db:     Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "HR":
        raise HTTPException(status_code=403, detail="HR access only")

    # Job must exist AND belong to this HR
    job = db.query(models.Job).filter(
        models.Job.job_id    == job_id,
        models.Job.posted_by == current_user.id       # ← key check
    ).first()
    if not job:
        raise HTTPException(
            status_code=403,
            detail="Job not found or you do not have access to this job."
        )

    rows = (
        db.query(models.Application, models.User)
        .join(models.User, models.Application.candidate_id == models.User.id)
        .filter(models.Application.job_id == job_id)
        .all()
    )

    applicants = []
    for app, user in rows:
        score_rec = db.query(models.MatchScore).filter(
            models.MatchScore.candidate_id == user.id,
            models.MatchScore.job_id       == job_id
        ).first()
        applicants.append({
            "application_id":  app.id,
            "candidate_id":    user.id,
            "candidate_name":  user.name,
            "candidate_email": user.email,
            "status":          app.status,
            "resume_path":     app.resume_path,
            "ai_score":        round(score_rec.score, 2) if score_rec else None,
            "screening_done":  score_rec is not None,
            "applied_at":      str(app.applied_at),
        })

    return {
        "job_id":           job_id,
        "job_title":        job.title,
        "company_name":     job.company_name,
        "total_applicants": len(applicants),
        "screening_done":   any(a["screening_done"] for a in applicants),
        "applicants":       applicants,
    }