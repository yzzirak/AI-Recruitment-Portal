"""
ai_screening.py
AI screening — HR can only screen their own jobs.
"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "nlp"))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import require_hr
import models
from resume_parser    import extract_text_from_resume
from preprocessing    import preprocess_text
from similarity_model import compute_similarity

router = APIRouter(tags=["AI Screening"])


@router.post("/run_screening/{job_id}")
def run_screening(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_hr)
):
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

    job_text = (
        f"Title: {job.title}. Description: {job.description}. "
        f"Sector: {job.sector}. Education: {job.education_required}. "
        f"Skills: {job.skills_required}. Experience: {job.experience_required}."
    )
    clean_job = preprocess_text(job_text)

    applications = (
        db.query(models.Application, models.User)
        .join(models.User, models.Application.candidate_id == models.User.id)
        .filter(models.Application.job_id == job_id)
        .all()
    )
    if not applications:
        return {"message": "No applicants found for this job", "rankings": []}

    rankings, errors = [], []

    for application, candidate in applications:
        try:
            resume_text  = extract_text_from_resume(application.resume_path)
            if not resume_text.strip():
                errors.append({"candidate": candidate.name, "error": "Empty resume"})
                continue

            clean_resume = preprocess_text(resume_text)
            score_pct    = round(compute_similarity(clean_job, clean_resume) * 100, 2)

            # Upsert score
            existing = db.query(models.MatchScore).filter(
                models.MatchScore.candidate_id == candidate.id,
                models.MatchScore.job_id       == job_id
            ).first()
            if existing:
                existing.score = score_pct
            else:
                db.add(models.MatchScore(
                    candidate_id=candidate.id,
                    job_id=job_id,
                    score=score_pct
                ))

            rankings.append({
                "candidate_id":    candidate.id,
                "candidate_name":  candidate.name,
                "candidate_email": candidate.email,
                "match_score":     score_pct,
                "application_id":  application.id,
                "status":          application.status,
            })
        except Exception as e:
            errors.append({"candidate": candidate.name, "error": str(e)})

    db.commit()
    rankings.sort(key=lambda x: x["match_score"], reverse=True)
    for i, c in enumerate(rankings, 1):
        c["rank"] = i

    return {
        "job_id":         job_id,
        "job_title":      job.title,
        "total_screened": len(rankings),
        "errors":         errors,
        "rankings":       rankings,
    }